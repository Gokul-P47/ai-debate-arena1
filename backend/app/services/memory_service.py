"""Structured claim memory manager for debates."""

from datetime import datetime, timezone

from app.schemas.claim import (
    AgentClaimMemory,
    ClaimStatus,
    DebateClaim,
    DebateState,
)
from app.schemas.debate_response import DebateMessage, DebateSummary, DebateTurn, SpeakerRole
from app.services.claim_extractor import ExtractedClaim
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MemoryService:
    """Stores transcript messages and structured per-agent claim memories.

    Agents never mutate opponent memory. Only ``DebateService`` (via this
    service) appends claims and updates statuses.
    """

    def __init__(self, *, debate_id: str, topic: str, language: str, mood: str) -> None:
        self._debate_id = debate_id
        self._topic = topic
        self._language = language
        self._mood = mood
        self._current_round = 0
        self._claim_counter = 0

        self._support_memory = AgentClaimMemory(role=SpeakerRole.SUPPORT)
        self._opposition_memory = AgentClaimMemory(role=SpeakerRole.OPPOSITION)

        self._messages: list[DebateMessage] = []
        self._turns: list[DebateTurn] = []

    # ── Transcript (for API / UI only; not used as LLM prompt memory) ─────────

    def add_message(self, message: DebateMessage) -> None:
        self._messages.append(message)
        self._current_round = max(self._current_round, message.round_number)

    def add_turn(self, turn: DebateTurn) -> None:
        self._turns.append(turn)
        self._current_round = max(self._current_round, turn.round_number)

    @property
    def messages(self) -> list[DebateMessage]:
        return list(self._messages)

    @property
    def turns(self) -> list[DebateTurn]:
        return list(self._turns)

    @property
    def message_count(self) -> int:
        return len(self._messages)

    @property
    def turn_count(self) -> int:
        return len(self._turns)

    @property
    def latest_support_content(self) -> str | None:
        for message in reversed(self._messages):
            if message.role == SpeakerRole.SUPPORT:
                return message.content
        return None

    @property
    def latest_opposition_content(self) -> str | None:
        for message in reversed(self._messages):
            if message.role == SpeakerRole.OPPOSITION:
                return message.content
        return None

    # ── Claim memory ─────────────────────────────────────────────────────────

    def memory_for(self, role: SpeakerRole) -> AgentClaimMemory:
        if role == SpeakerRole.SUPPORT:
            return self._support_memory
        return self._opposition_memory

    def _next_claim_id(self) -> str:
        self._claim_counter += 1
        return f"claim-{self._claim_counter:03d}"

    def append_claims(
        self,
        role: SpeakerRole,
        extracted: list[ExtractedClaim] | list[str],
        *,
        round_number: int,
    ) -> list[DebateClaim]:
        """Append newly extracted claims into the owning agent's memory only."""
        memory = self.memory_for(role)
        created: list[DebateClaim] = []
        existing = {c.claim.strip().lower() for c in memory.claims}

        normalized: list[ExtractedClaim] = []
        for item in extracted:
            if isinstance(item, ExtractedClaim):
                normalized.append(item)
            elif isinstance(item, str):
                normalized.append(ExtractedClaim(claim=item))

        for item in normalized:
            text = " ".join(item.claim.split()).strip()
            if not text or text.lower() in existing:
                continue

            claim = DebateClaim(
                id=self._next_claim_id(),
                claim=text,
                category=item.category or "General",
                confidence=min(1.0, max(0.0, item.confidence)),
                importance=min(1.0, max(0.0, item.importance)),
                round=round_number,
                status=ClaimStatus.ACTIVE,
                timestamp=datetime.now(timezone.utc),
                owner=role,
            )
            memory.claims.append(claim)
            existing.add(text.lower())
            created.append(claim)
            logger.info(
                "Stored %s claim %s [%s]: %s",
                role.value,
                claim.id,
                claim.category,
                claim.claim,
            )

        return created

    def mark_contradicted(
        self,
        owner_role: SpeakerRole,
        *,
        claim_id: str,
        statement: str,
    ) -> DebateClaim | None:
        """Mark an owned claim as CONTRADICTED and record the opposing reason."""
        memory = self.memory_for(owner_role)
        for claim in memory.claims:
            if claim.id != claim_id:
                continue
            statement = statement.strip()
            if statement and statement not in claim.contradicted_by:
                claim.contradicted_by.append(statement)
            if claim.status in {ClaimStatus.ACTIVE, ClaimStatus.DEFENDED}:
                claim.status = ClaimStatus.CONTRADICTED
            return claim
        return None

    def mark_defended(
        self,
        owner_role: SpeakerRole,
        *,
        claim_id: str,
        statement: str,
    ) -> DebateClaim | None:
        """Mark an owned claim as DEFENDED after the owner reinforces it."""
        memory = self.memory_for(owner_role)
        for claim in memory.claims:
            if claim.id != claim_id:
                continue
            statement = statement.strip()
            if statement and statement not in claim.defended_by:
                claim.defended_by.append(statement)
            if claim.status == ClaimStatus.CONTRADICTED:
                claim.status = ClaimStatus.DEFENDED
            return claim
        return None

    def mark_resolved(self, owner_role: SpeakerRole, claim_id: str) -> DebateClaim | None:
        memory = self.memory_for(owner_role)
        for claim in memory.claims:
            if claim.id == claim_id:
                claim.status = ClaimStatus.RESOLVED
                return claim
        return None

    def already_used_claims(self, role: SpeakerRole) -> list[str]:
        """Claim texts already used by this agent (for anti-repetition)."""
        return [c.claim for c in self.memory_for(role).claims]

    def format_claims(self, role: SpeakerRole) -> str:
        """Human-readable claim list for prompts."""
        claims = self.memory_for(role).claims
        if not claims:
            return "(No claims recorded yet.)"
        lines: list[str] = []
        for claim in claims:
            extras: list[str] = []
            if claim.contradicted_by:
                extras.append(f"challenged={claim.contradicted_by[-1]!r}")
            if claim.defended_by:
                extras.append(f"defended={claim.defended_by[-1]!r}")
            suffix = f" | {'; '.join(extras)}" if extras else ""
            lines.append(
                f"- [{claim.id}] {claim.claim} "
                f"({claim.status.value}, {claim.category}, "
                f"importance={claim.importance:.2f}, confidence={claim.confidence:.2f})"
                f"{suffix}"
            )
        return "\n".join(lines)

    def format_already_used(self, role: SpeakerRole) -> str:
        used = self.already_used_claims(role)
        if not used:
            return "(None yet — opening round.)"
        return "\n".join(f"✓ {claim}" for claim in used)

    def format_defend_or_refine(self, role: SpeakerRole) -> str:
        contradicted = self.memory_for(role).contradicted_claims()
        if not contradicted:
            return "(None — introduce a new argument or extend an ACTIVE claim carefully.)"
        lines = []
        for claim in contradicted:
            challenge = claim.contradicted_by[-1] if claim.contradicted_by else "challenged"
            lines.append(
                f"- [{claim.id}] {claim.claim} — currently CONTRADICTED because: {challenge}"
            )
        return "\n".join(lines)

    def summarized_context(self) -> str:
        """Compact debate context derived from claim memories."""
        return (
            "Support claims:\n"
            f"{self.format_claims(SpeakerRole.SUPPORT)}\n\n"
            "Opposition claims:\n"
            f"{self.format_claims(SpeakerRole.OPPOSITION)}"
        )

    def to_debate_summary(self) -> DebateSummary:
        """Build API summary fields from structured claims."""
        support_points = [c.claim for c in self._support_memory.claims]
        opposition_points = [c.claim for c in self._opposition_memory.claims]
        return DebateSummary(
            text=self.summarized_context(),
            support_points=support_points,
            opposition_points=opposition_points,
        )

    def snapshot(self) -> DebateState:
        """Return a serializable central debate state."""
        return DebateState(
            debate_id=self._debate_id,
            topic=self._topic,
            language=self._language,
            mood=self._mood,
            support_memory=self._support_memory.model_copy(deep=True),
            opposition_memory=self._opposition_memory.model_copy(deep=True),
            current_round=self._current_round,
        )
