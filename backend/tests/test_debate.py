"""Tests for structured claim memory, extraction, context builder, and debate flow."""

import asyncio
import json
from typing import AsyncIterator

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.providers.base_provider import BaseProvider
from app.schemas.claim import ClaimStatus
from app.schemas.debate_request import DebateMood, DebateRequest
from app.schemas.debate_response import SpeakerRole
from app.services.claim_extractor import ClaimExtractor, ExtractedClaim
from app.services.context_builder import ContextBuilder
from app.services.debate_service import DebateService
from app.services.memory_service import MemoryService


class FakeProvider(BaseProvider):
    """Routes responses by system-prompt intent for deterministic tests."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []
        self._agent_n = 0

    async def generate(self, prompt: str, system_prompt: str) -> str:
        self.calls.append((prompt, system_prompt))
        lower = system_prompt.lower()

        if "extract only the important core debate claims" in lower:
            if "Opposition reply" in prompt or "quality" in prompt.lower():
                return json.dumps(
                    {
                        "claims": [
                            {
                                "claim": "Lower costs often reduce quality",
                                "category": "Quality",
                                "confidence": 0.9,
                                "importance": 0.85,
                            }
                        ]
                    }
                )
            return json.dumps(
                {
                    "claims": [
                        {
                            "claim": "AI reduces healthcare costs",
                            "category": "Economics",
                            "confidence": 0.95,
                            "importance": 0.92,
                        },
                        {
                            "claim": "AI works continuously",
                            "category": "Scalability",
                            "confidence": 0.9,
                            "importance": 0.8,
                        },
                    ]
                }
            )

        if "directly challenges or defends existing claims" in lower:
            if "Opposition reply" in prompt or "quality" in prompt.lower():
                return json.dumps(
                    {
                        "contradicted_claims": [
                            {
                                "claim_id": "claim-001",
                                "reason": "Quality tradeoff from cheaper solutions",
                            }
                        ],
                        "defended_claims": [],
                    }
                )
            return json.dumps({"contradicted_claims": [], "defended_claims": []})

        if "opposition agent" in lower or "oppose the debate topic" in lower:
            self._agent_n += 1
            return f"Opposition reply #{self._agent_n}: Lower costs often reduce quality."

        self._agent_n += 1
        return (
            f"Support reply #{self._agent_n}: AI reduces healthcare costs and works continuously."
        )

    async def generate_stream(self, prompt: str, system_prompt: str) -> AsyncIterator[str]:
        text = await self.generate(prompt, system_prompt)
        # Simulate token streaming
        for word in text.split(" "):
            yield word + " "


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_memory_service_stores_rich_claims_and_contradictions() -> None:
    memory = MemoryService(
        debate_id="d1",
        topic="AI should be regulated",
        language="en",
        mood="SERIOUS",
    )
    created = memory.append_claims(
        SpeakerRole.SUPPORT,
        [
            ExtractedClaim(
                claim="AI reduces healthcare costs",
                category="Economics",
                confidence=0.95,
                importance=0.9,
            ),
            ExtractedClaim(
                claim="AI works continuously",
                category="Scalability",
                confidence=0.9,
                importance=0.8,
            ),
        ],
        round_number=1,
    )
    assert len(created) == 2
    assert created[0].id == "claim-001"
    assert created[0].category == "Economics"
    assert created[0].confidence == 0.95
    assert created[0].status == ClaimStatus.ACTIVE

    memory.mark_contradicted(
        SpeakerRole.SUPPORT,
        claim_id="claim-001",
        statement="Lower costs often reduce quality",
    )
    claim = memory.memory_for(SpeakerRole.SUPPORT).claims[0]
    assert claim.status == ClaimStatus.CONTRADICTED

    memory.mark_defended(
        SpeakerRole.SUPPORT,
        claim_id="claim-001",
        statement="Savings fund better patient care",
    )
    assert claim.status == ClaimStatus.DEFENDED

    memory.append_claims(
        SpeakerRole.OPPOSITION,
        [ExtractedClaim(claim="Human judgment remains essential")],
        round_number=1,
    )
    assert len(memory.memory_for(SpeakerRole.SUPPORT).claims) == 2
    assert "✓ AI reduces healthcare costs" in memory.format_already_used(SpeakerRole.SUPPORT)


def test_context_builder_centralizes_prompts_without_transcript() -> None:
    memory = MemoryService(
        debate_id="d1",
        topic="AI should be regulated",
        language="en",
        mood="SERIOUS",
    )
    memory.append_claims(
        SpeakerRole.SUPPORT,
        [ExtractedClaim(claim="AI reduces healthcare costs", category="Economics")],
        round_number=1,
    )
    memory.mark_contradicted(
        SpeakerRole.SUPPORT,
        claim_id="claim-001",
        statement="Cheap means lower quality",
    )
    memory.append_claims(
        SpeakerRole.OPPOSITION,
        [ExtractedClaim(claim="Human creativity is irreplaceable")],
        round_number=1,
    )

    builder = ContextBuilder(memory)
    support_prompt = builder.build_support_prompt(
        topic="AI should be regulated",
        mood=DebateMood.SERIOUS,
        language="en",
        round_number=2,
        total_rounds=3,
        opponent_latest="Cheap means lower quality.",
    )
    assert "AI should be regulated" in support_prompt.user_prompt
    assert "Already used" in support_prompt.user_prompt
    assert "AI reduces healthcare costs" in support_prompt.user_prompt
    assert "CONTRADICTED" in support_prompt.user_prompt
    assert "Full transcript" not in support_prompt.user_prompt
    assert "do NOT repeat" in support_prompt.user_prompt.lower() or "Already used" in support_prompt.user_prompt

    opposition_prompt = builder.build_opposition_prompt(
        topic="AI should be regulated",
        mood=DebateMood.SERIOUS,
        language="ta",
        round_number=2,
        total_rounds=3,
        opponent_latest="AI still reduces net cost.",
    )
    assert "Tamil" in opposition_prompt.system_prompt
    assert "Human creativity is irreplaceable" in opposition_prompt.user_prompt


def test_claim_extractor_returns_category_confidence_importance() -> None:
    provider = FakeProvider()
    extractor = ClaimExtractor(provider)
    claims = asyncio.run(
        extractor.extract(
            response_text="AI reduces costs and works 24/7.",
            topic="AI should be regulated",
        )
    )
    assert len(claims) >= 1
    assert claims[0].claim
    assert claims[0].category
    assert 0 <= claims[0].confidence <= 1
    assert 0 <= claims[0].importance <= 1


def test_debate_service_tracks_claims_across_rounds() -> None:
    provider = FakeProvider()
    service = DebateService(provider=provider)
    request = DebateRequest(
        topic="AI should be regulated",
        rounds=1,
        mood=DebateMood.SERIOUS,
        language="en",
    )
    result = asyncio.run(service.create_debate(request))

    assert len(result.transcript) == 2
    assert result.claim_memory is not None
    support_claims = result.claim_memory.support_memory.claims
    assert support_claims
    assert support_claims[0].category
    contradicted = [c for c in support_claims if c.status == ClaimStatus.CONTRADICTED]
    assert contradicted, "Expected at least one contradicted support claim"


def test_create_debate_endpoint_includes_claim_memory(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeProvider()
    monkeypatch.setattr("app.services.debate_service.get_provider", lambda: fake)

    client = TestClient(app)
    response = client.post(
        "/api/v1/debates",
        json={
            "topic": "AI should be regulated",
            "rounds": 1,
            "mood": "SERIOUS",
            "language": "en",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["debateId"]
    assert data["claimMemory"]["supportMemory"]["claims"]
    first = data["claimMemory"]["supportMemory"]["claims"][0]
    assert "category" in first
    assert "confidence" in first
    assert "importance" in first


def test_stream_debate_emits_tokens_and_lifecycle_events() -> None:
    provider = FakeProvider()
    service = DebateService(provider=provider)
    request = DebateRequest(
        topic="AI should be regulated",
        rounds=1,
        mood=DebateMood.SERIOUS,
        language="en",
    )

    async def _collect() -> list[dict]:
        return [item async for item in service.stream_debate(request)]

    events = asyncio.run(_collect())
    names = [item["event"] for item in events]
    assert names[0] == "debate_started"
    assert "token" in names
    assert names[-1] == "debate_completed"


def test_stream_debate_endpoint_returns_sse(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeProvider()
    monkeypatch.setattr("app.services.debate_service.get_provider", lambda: fake)

    client = TestClient(app)
    with client.stream(
        "POST",
        "/api/v1/debates/stream",
        json={
            "topic": "AI should be regulated",
            "rounds": 1,
            "mood": "SERIOUS",
            "language": "en",
        },
    ) as response:
        assert response.status_code == 200
        body = "".join(response.iter_text())

    assert "event: debate_started" in body
    assert "event: token" in body
    assert "event: debate_completed" in body
