"""LLM-backed contradiction and defense detection against structured claims."""

from dataclasses import dataclass

from app.providers.base_provider import BaseProvider
from app.schemas.claim import DebateClaim
from app.utils.json_parse import parse_json_payload
from app.utils.logger import get_logger

logger = get_logger(__name__)

CONTRADICTION_SYSTEM_PROMPT = """
You analyze whether a new debate response directly challenges or defends existing claims.

Rules:
- Return JSON only (no markdown).
- Only reference claim ids from the provided lists.
- Do not mark unrelated claims.
- Do not use keyword matching alone — reason about whether the response truly challenges or defends the claim.
- contradicted_claims: opponent/target claims that this response directly challenges.
- defended_claims: the speaker's own prior claims that this response reinforces or repairs after challenge.
- reason: short explanation of how the response challenges or defends that claim.

Schema:
{
  "contradicted_claims": [
    {"claim_id": "claim-001", "reason": "Argues cheaper solutions reduce quality"}
  ],
  "defended_claims": [
    {"claim_id": "claim-002", "reason": "Clarifies cost savings fund better care"}
  ]
}
""".strip()


@dataclass(frozen=True)
class ClaimLink:
    claim_id: str
    reason: str


@dataclass(frozen=True)
class ContradictionAnalysis:
    contradictions: tuple[ClaimLink, ...]
    defenses: tuple[ClaimLink, ...]


class ContradictionAnalyzer:
    """Ask the LLM which claims are contradicted or defended — not string matching."""

    def __init__(self, provider: BaseProvider) -> None:
        self._provider = provider

    async def analyze(
        self,
        *,
        response_text: str,
        topic: str,
        target_claims: list[DebateClaim],
        own_claims: list[DebateClaim] | None = None,
    ) -> ContradictionAnalysis:
        """Compare a response to target (opponent) claims and optional own claims."""
        if not response_text.strip() or (not target_claims and not own_claims):
            return ContradictionAnalysis(contradictions=(), defenses=())

        target_block = self._format_claims(target_claims) or "(none)"
        own_block = self._format_claims(own_claims or []) or "(none)"

        prompt = (
            f"Debate topic: {topic}\n\n"
            f"Support/target claims that may be challenged:\n{target_block}\n\n"
            f"Speaker's own prior claims that may be defended:\n{own_block}\n\n"
            f"Opponent / new response:\n{response_text.strip()}\n\n"
            "Which claims are directly challenged? Which of the speaker's claims are defended?\n"
            "Return JSON only."
        )

        raw = await self._provider.generate(
            prompt=prompt,
            system_prompt=CONTRADICTION_SYSTEM_PROMPT,
        )

        try:
            payload = parse_json_payload(raw)
        except ValueError:
            logger.warning("Contradiction analysis JSON parse failed; skipping updates")
            return ContradictionAnalysis(contradictions=(), defenses=())

        if not isinstance(payload, dict):
            return ContradictionAnalysis(contradictions=(), defenses=())

        valid_target_ids = {c.id for c in target_claims}
        valid_own_ids = {c.id for c in (own_claims or [])}

        contradiction_raw = (
            payload.get("contradicted_claims")
            or payload.get("contradictions")
            or []
        )
        defense_raw = (
            payload.get("defended_claims")
            or payload.get("defenses")
            or []
        )

        contradictions = self._parse_links(contradiction_raw, allowed_ids=valid_target_ids)
        defenses = self._parse_links(defense_raw, allowed_ids=valid_own_ids)
        return ContradictionAnalysis(
            contradictions=tuple(contradictions),
            defenses=tuple(defenses),
        )

    @staticmethod
    def _format_claims(claims: list[DebateClaim]) -> str:
        lines: list[str] = []
        for index, claim in enumerate(claims, start=1):
            lines.append(
                f"{index}. [{claim.id}] {claim.claim} "
                f"(status={claim.status.value}, category={claim.category}, "
                f"importance={claim.importance:.2f})"
            )
        return "\n".join(lines)

    @staticmethod
    def _parse_links(raw_items: object, *, allowed_ids: set[str]) -> list[ClaimLink]:
        if not isinstance(raw_items, list):
            return []
        links: list[ClaimLink] = []
        for item in raw_items:
            if not isinstance(item, dict):
                continue
            claim_id = str(item.get("claim_id") or item.get("id") or "").strip()
            reason = str(
                item.get("reason")
                or item.get("statement")
                or item.get("text")
                or ""
            ).strip()
            if claim_id in allowed_ids and reason:
                links.append(ClaimLink(claim_id=claim_id, reason=reason))
        return links
