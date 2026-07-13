"""Extract structured debate claims from agent responses via LLM."""

from dataclasses import dataclass

from app.providers.base_provider import BaseProvider
from app.utils.json_parse import parse_json_payload
from app.utils.logger import get_logger

logger = get_logger(__name__)

CLAIM_EXTRACTION_SYSTEM_PROMPT = """
You extract only the important core debate claims from an agent response.

Rules:
- Return JSON only (no markdown, no commentary).
- Ignore greetings, filler, examples, transitions, and rhetorical flourishes.
- Do not invent claims that are not present.
- Deduplicate near-identical ideas.
- Prefer short, atomic claims (one idea each).
- Normalize wording into a clear proposition.
- category examples: Economics, Ethics, Safety, Feasibility, Quality, Scalability, Governance, Social, Technical, General
- confidence: how sure you are this is a distinct core claim (0-1)
- importance: how central the claim is to the argument (0-1)

Schema:
{
  "claims": [
    {
      "claim": "AI reduces operational cost",
      "category": "Economics",
      "confidence": 0.95,
      "importance": 0.91
    }
  ]
}
""".strip()


@dataclass(frozen=True)
class ExtractedClaim:
    """Structured claim produced by the extractor (pre-id assignment)."""

    claim: str
    category: str = "General"
    confidence: float = 0.7
    importance: float = 0.7


class ClaimExtractor:
    """LLM-backed intelligent claim extraction, provider-agnostic."""

    def __init__(self, provider: BaseProvider) -> None:
        self._provider = provider

    async def extract(self, *, response_text: str, topic: str) -> list[ExtractedClaim]:
        """Return structured claims from an agent response."""
        if not response_text.strip():
            return []

        prompt = (
            f"Debate topic: {topic}\n\n"
            f"Agent response:\n{response_text.strip()}\n\n"
            "Extract important claims as JSON only."
        )

        raw = await self._provider.generate(
            prompt=prompt,
            system_prompt=CLAIM_EXTRACTION_SYSTEM_PROMPT,
        )

        try:
            payload = parse_json_payload(raw)
        except ValueError:
            logger.warning("Claim extraction JSON parse failed; using fallback split")
            return self._fallback_claims(response_text)

        claims_raw = payload.get("claims", payload) if isinstance(payload, dict) else payload
        if not isinstance(claims_raw, list):
            return self._fallback_claims(response_text)

        results: list[ExtractedClaim] = []
        for item in claims_raw:
            parsed = self._parse_item(item)
            if parsed:
                results.append(parsed)

        return results or self._fallback_claims(response_text)

    @staticmethod
    def _clamp(value: object, default: float) -> float:
        try:
            return min(1.0, max(0.0, float(value)))  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return default

    def _parse_item(self, item: object) -> ExtractedClaim | None:
        if isinstance(item, str):
            text = item.strip()
            if not text:
                return None
            return ExtractedClaim(claim=text)

        if not isinstance(item, dict):
            return None

        text = str(item.get("claim") or item.get("text") or "").strip()
        if not text:
            return None

        category = str(item.get("category") or "General").strip() or "General"
        return ExtractedClaim(
            claim=text,
            category=category,
            confidence=self._clamp(item.get("confidence", 0.7), 0.7),
            importance=self._clamp(item.get("importance", 0.7), 0.7),
        )

    @staticmethod
    def _fallback_claims(response_text: str) -> list[ExtractedClaim]:
        """Lightweight heuristic if the model does not return valid JSON."""
        parts = [
            p.strip(" .-•\n\t")
            for p in response_text.replace(";", ".").split(".")
            if len(p.strip()) > 24
        ]
        return [
            ExtractedClaim(claim=part, category="General", confidence=0.55, importance=0.6)
            for part in parts[:3]
        ]
