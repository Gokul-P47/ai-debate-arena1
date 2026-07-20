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

        if "you are the host of a" in lower or "you are the host of a witty" in lower:
            self._agent_n += 1
            if "segment: opening" in prompt.lower():
                return f"Host opening #{self._agent_n}: Welcome to the talk show."
            if "segment: closing" in prompt.lower():
                return f"Host closing #{self._agent_n}: Thanks for joining us tonight."
            return f"Host segment #{self._agent_n}: That was interesting — Dave, what's your take?"

        if "you are sarah" in lower or "calm, curious" in lower:
            self._agent_n += 1
            return f"Sarah reply #{self._agent_n}: Fair enough — though I wonder about the other side."

        if "you are winston" in lower or "down-to-earth" in lower:
            self._agent_n += 1
            return f"Winston reply #{self._agent_n}: On a normal day, what actually works?"

        if "you are chloe" in lower or "playful and imaginative" in lower:
            self._agent_n += 1
            return f"Chloe reply #{self._agent_n}: Wait, what if we look at it like this?"

        if "prepare private show notes" in lower or "private knowledge pack" in lower or "controversial:" in lower:
            return (
                "CONTROVERSIAL: yes\n\n"
                "KNOWLEDGE\n"
                "- This topic has real upsides and real worries\n\n"
                "LIVED ANGLES\n"
                "- How ordinary people bump into this in daily choices\n\n"
                "FOR\n"
                "- It can help people in practical ways\n\n"
                "AGAINST\n"
                "- It can create new problems if handled badly\n\n"
                "TALK HOOKS\n"
                "- Who actually benefits first?\n"
                "- What should change this year?"
            )

        self._agent_n += 1
        return (
            f"Dave reply #{self._agent_n}: Honestly, I see the upside — here's a simple story."
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


@pytest.fixture(autouse=True)
def stub_news_fetch(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _no_news(_query: str, max_results: int = 5):
        return [
            {
                "title": "People talk about the topic everywhere",
                "link": "https://example.com",
                "pub_date": "",
                "source": "Example News",
            }
        ]

    monkeypatch.setattr("app.utils.news.fetch_latest_news", _no_news)
    monkeypatch.setattr("app.services.news_browser.fetch_latest_news", _no_news)


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


def test_context_builder_uses_full_transcript() -> None:
    from datetime import datetime, timezone

    from app.schemas.debate_response import DebateMessage

    memory = MemoryService(
        debate_id="d1",
        topic="AI should be regulated",
        language="en",
        mood="SERIOUS",
    )
    memory.add_message(
        DebateMessage(
            speaker="Host",
            role=SpeakerRole.HOST,
            content="Welcome — tonight we talk AI regulation.",
            timestamp=datetime.now(timezone.utc),
            round_number=1,
        )
    )
    memory.add_message(
        DebateMessage(
            speaker="Dave",
            role=SpeakerRole.SUPPORT,
            content="Honestly, I think clear rules help people trust the tools.",
            timestamp=datetime.now(timezone.utc),
            round_number=1,
        )
    )

    builder = ContextBuilder(memory)
    support_prompt = builder.build_support_prompt(
        topic="AI should be regulated",
        mood=DebateMood.SERIOUS,
        language="en",
        round_number=2,
        total_rounds=3,
        turn_seconds=45,
    )
    assert "topic" in support_prompt.user_prompt.lower()
    assert support_prompt.topic == "AI should be regulated"
    assert "SHOW TOPIC" in support_prompt.user_prompt or "TOPIC LOCK" in support_prompt.system_prompt
    assert "comedy-forward" in support_prompt.system_prompt.lower() or "comedy podcast" in support_prompt.system_prompt.lower()
    assert "never get heated" in support_prompt.system_prompt.lower()
    assert "2–4 sentences" in support_prompt.system_prompt or "2-4 sentences" in support_prompt.system_prompt
    assert "CONTRADICTED" not in support_prompt.user_prompt
    assert "claim memory" not in support_prompt.user_prompt.lower()
    assert "simple" in support_prompt.system_prompt.lower()
    assert "complex" in support_prompt.system_prompt.lower() or "everyday words" in support_prompt.system_prompt.lower()
    assert "listeners" in support_prompt.system_prompt.lower() or "interesting" in support_prompt.system_prompt.lower()

    from app.services.agent_context import topic_locked_prompts

    locked_system, locked_user = topic_locked_prompts(support_prompt)
    assert "TOPIC LOCK" in locked_system
    assert "AI should be regulated" in locked_system
    assert 'SHOW TOPIC (mandatory): "AI should be regulated"' in locked_user
    assert support_prompt.user_prompt in locked_user
    assert "do not auto-counter" in locked_system.lower()
    assert "chase" in support_prompt.system_prompt.lower() or "chase" in locked_system.lower()
    assert "auto-counter" in support_prompt.system_prompt.lower()

    opposition_prompt = builder.build_opposition_prompt(
        topic="AI should be regulated",
        mood=DebateMood.SERIOUS,
        language="ta",
        round_number=2,
        total_rounds=3,
        turn_seconds=30,
        peer_latest="Dave: Honestly, I think clear rules help people trust the tools.",
    )
    assert "Tamil" in opposition_prompt.system_prompt
    assert "Sarah" in opposition_prompt.system_prompt
    assert "Dave:" in opposition_prompt.user_prompt
    assert "clear rules" in opposition_prompt.user_prompt

    fun_prompt = builder.build_support_prompt(
        topic="AI should be regulated",
        mood=DebateMood.FUN,
        language="en",
        round_number=1,
        total_rounds=2,
        turn_seconds=45,
    )
    assert "FUN" in fun_prompt.system_prompt
    assert "comedy" in fun_prompt.system_prompt.lower() or "joke" in fun_prompt.system_prompt.lower()

    from app.schemas.roles import HostSegment

    host_prompt = builder.build_host_prompt(
        topic="AI should be regulated",
        mood=DebateMood.SERIOUS,
        language="en",
        round_number=1,
        total_rounds=3,
        turn_seconds=45,
        segment=HostSegment.OPENING,
    )
    assert host_prompt.side == SpeakerRole.HOST
    assert "ai should be regulated" in host_prompt.system_prompt.lower()
    assert "comedy" in host_prompt.system_prompt.lower() or "cheeky" in host_prompt.system_prompt.lower()
    assert "witty hook" in host_prompt.user_prompt.lower() or "hand straight" in host_prompt.user_prompt.lower()
    assert "host" in host_prompt.system_prompt.lower()
    assert "far shorter than guests" in host_prompt.system_prompt.lower()
    assert "arre yaar" in host_prompt.system_prompt.lower() or "desi" in host_prompt.system_prompt.lower()

    nick_prompt = builder.build_support_prompt(
        topic="Bhavik Patel should run for office",
        mood=DebateMood.FUN,
        language="en",
        round_number=1,
        total_rounds=2,
        turn_seconds=45,
    )
    assert "BP" in nick_prompt.system_prompt or "Patel" in nick_prompt.system_prompt
    assert "Bhavik Patel" in nick_prompt.system_prompt
    assert "arre yaar" in nick_prompt.system_prompt.lower()

    host_outro = builder.build_host_prompt(
        topic="AI should be regulated",
        mood=DebateMood.FUN,
        language="en",
        round_number=3,
        total_rounds=3,
        turn_seconds=45,
        segment=HostSegment.CLOSING,
    )
    assert "witty closer" in host_outro.user_prompt.lower() or "joke" in host_outro.user_prompt.lower()


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


def test_debate_service_builds_natural_conversation_transcript() -> None:
    provider = FakeProvider()
    service = DebateService(provider=provider)
    request = DebateRequest(
        topic="AI should be regulated",
        rounds=1,
        mood=DebateMood.SERIOUS,
        language="en",
    )
    result = asyncio.run(service.create_debate(request))

    # Host opening + Support + Opposition + Host closing (no double host in round 1)
    assert len(result.transcript) == 4
    assert result.transcript[0].role == SpeakerRole.HOST
    assert result.transcript[1].role == SpeakerRole.SUPPORT
    assert result.transcript[2].role == SpeakerRole.OPPOSITION
    assert result.transcript[3].role == SpeakerRole.HOST
    assert result.metadata.extra.get("hosted") is True
    assert result.metadata.extra.get("memoryMode") == "full_transcript"
    assert result.claim_memory is not None
    # Claim extraction is no longer part of the live conversation loop.
    assert result.claim_memory.support_memory.claims == []
    assert result.summary.support_points
    assert "Dave" in result.summary.support_points[0] or "upside" in result.summary.support_points[0].lower() or len(result.summary.support_points[0]) > 0


def test_create_debate_endpoint_includes_transcript_summary(monkeypatch: pytest.MonkeyPatch) -> None:
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
    assert data["transcript"]
    assert data["summary"]["supportPoints"]
    assert "claimMemory" in data
    assert data["claimMemory"]["supportMemory"]["claims"] == []
    assert data["metadata"]["extra"]["memoryMode"] == "full_transcript"


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
    assert "debate_started" in names
    assert "token" in names
    assert names[-1] == "debate_completed"
    turn_roles = [
        item["data"]["role"]
        for item in events
        if item["event"] == "turn_started"
    ]
    assert turn_roles == ["host", "support", "opposition", "host"]
    started = next(item for item in events if item["event"] == "debate_started")
    assert started["data"]["participantCount"] == 2
    assert len(started["data"]["participants"]) == 2


def test_stream_debate_with_four_guests() -> None:
    provider = FakeProvider()
    service = DebateService(provider=provider)
    request = DebateRequest(
        topic="Remote work forever?",
        rounds=1,
        mood=DebateMood.MIXED,
        language="en",
        participant_count=4,
    )

    async def _collect() -> list[dict]:
        return [item async for item in service.stream_debate(request)]

    events = asyncio.run(_collect())
    started = next(item for item in events if item["event"] == "debate_started")
    assert started["data"]["participantCount"] == 4
    assert len(started["data"]["participants"]) == 4
    roles = [p["role"] for p in started["data"]["participants"]]
    assert roles == ["support", "opposition", "guest3", "guest4"]

    turn_roles = [
        item["data"]["role"]
        for item in events
        if item["event"] == "turn_started"
    ]
    # opening host, 4 guests, closing host (no double host in round 1)
    assert turn_roles == [
        "host",
        "support",
        "opposition",
        "guest3",
        "guest4",
        "host",
    ]

    completed = next(item for item in events if item["event"] == "debate_completed")
    summary = completed["data"]["summary"]
    assert summary is not None
    assert len(summary.get("participants") or []) == 4


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
