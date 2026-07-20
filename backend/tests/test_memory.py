"""Focused unit tests for claim extraction JSON parsing and analyzer."""

import asyncio
import json
from typing import AsyncIterator

from app.providers.base_provider import BaseProvider
from app.schemas.claim import ClaimStatus, DebateClaim
from app.schemas.roles import SpeakerRole
from app.services.claim_extractor import ClaimExtractor
from app.services.contradiction_analyzer import ContradictionAnalyzer
from app.utils.json_parse import parse_json_payload


class ScriptedProvider(BaseProvider):
    def __init__(self, response: str) -> None:
        self.response = response

    async def generate(self, prompt: str, system_prompt: str) -> str:
        return self.response

    async def generate_stream(self, prompt: str, system_prompt: str) -> AsyncIterator[str]:
        yield self.response


def test_parse_json_payload_from_fenced_block() -> None:
    raw = """Here you go:
```json
{"claims": [{"claim": "AI reduces cost", "category": "Economics", "confidence": 0.9, "importance": 0.9}]}
```
"""
    payload = parse_json_payload(raw)
    assert payload["claims"][0]["claim"] == "AI reduces cost"


def test_contradiction_analyzer_uses_reason_and_filters_unknown_ids() -> None:
    provider = ScriptedProvider(
        json.dumps(
            {
                "contradicted_claims": [
                    {"claim_id": "claim-001", "reason": "Quality tradeoff"},
                    {"claim_id": "claim-999", "reason": "Ignored"},
                ],
                "defended_claims": [
                    {"claim_id": "claim-002", "reason": "Still essential under pressure"}
                ],
            }
        )
    )
    analyzer = ContradictionAnalyzer(provider)
    target = [
        DebateClaim(
            id="claim-001",
            claim="AI reduces costs",
            round=1,
            status=ClaimStatus.ACTIVE,
            owner=SpeakerRole.SUPPORT,
            category="Economics",
        )
    ]
    own = [
        DebateClaim(
            id="claim-002",
            claim="Human judgment is essential",
            round=1,
            status=ClaimStatus.CONTRADICTED,
            owner=SpeakerRole.OPPOSITION,
            category="Governance",
        )
    ]
    result = asyncio.run(
        analyzer.analyze(
            response_text="Cheap often means lower quality. Human judgment is still essential.",
            topic="AI",
            target_claims=target,
            own_claims=own,
        )
    )
    assert len(result.contradictions) == 1
    assert result.contradictions[0].claim_id == "claim-001"
    assert result.contradictions[0].reason == "Quality tradeoff"
    assert len(result.defenses) == 1
    assert result.defenses[0].claim_id == "claim-002"


def test_claim_extractor_fallback_on_bad_json() -> None:
    provider = ScriptedProvider("not-json at all. This sentence is long enough to keep.")
    extractor = ClaimExtractor(provider)
    claims = asyncio.run(
        extractor.extract(
            response_text="A fairly long fallback sentence about regulation.",
            topic="AI",
        )
    )
    assert isinstance(claims, list)
    if claims:
        assert claims[0].category
