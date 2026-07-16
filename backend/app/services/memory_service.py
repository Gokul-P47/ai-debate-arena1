"""Structured claim memory manager for multi-guest talk shows."""

from datetime import datetime, timezone

from app.core.participants import GuestSpec, guests_for_count, is_guest_role
from app.schemas.claim import (
    AgentClaimMemory,
    ClaimStatus,
    DebateClaim,
    DebateState,
)
from app.schemas.debate_response import (
    DebateMessage,
    DebateSummary,
    DebateTurn,
    ParticipantSummary,
    SpeakerRole,
)
from app.services.claim_extractor import ExtractedClaim
from app.utils.logger import get_logger

logger = get_logger(__name__)


class MemoryService:
    """Stores transcript messages and structured per-guest claim memories."""

    def __init__(
        self,
        *,
        debate_id: str,
        topic: str,
        language: str,
        mood: str,
        guests: list[GuestSpec] | None = None,
        news_articles: list[dict[str, str]] | None = None,
    ) -> None:
        self._debate_id = debate_id
        self._topic = topic
        self._language = language
        self._mood = mood
        self._current_round = 0
        self._claim_counter = 0
        self._guests = list(guests) if guests is not None else guests_for_count(2)
        self._news_articles = list(news_articles) if news_articles else []

        self._memories: dict[SpeakerRole, AgentClaimMemory] = {
            g.role: AgentClaimMemory(role=g.role) for g in self._guests
        }
        # Ensure legacy slots exist even if somehow empty (tests).
        if SpeakerRole.SUPPORT not in self._memories:
            self._memories[SpeakerRole.SUPPORT] = AgentClaimMemory(role=SpeakerRole.SUPPORT)
        if SpeakerRole.OPPOSITION not in self._memories:
            self._memories[SpeakerRole.OPPOSITION] = AgentClaimMemory(
                role=SpeakerRole.OPPOSITION
            )

        self._messages: list[DebateMessage] = []
        self._turns: list[DebateTurn] = []

    @property
    def guests(self) -> list[GuestSpec]:
        return list(self._guests)

    @property
    def news_articles(self) -> list[dict[str, str]]:
        return list(self._news_articles)

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

    def latest_content_for(self, role: SpeakerRole) -> str | None:
        for message in reversed(self._messages):
            if message.role == role:
                return message.content
        return None

    @property
    def latest_support_content(self) -> str | None:
        return self.latest_content_for(SpeakerRole.SUPPORT)

    @property
    def latest_opposition_content(self) -> str | None:
        return self.latest_content_for(SpeakerRole.OPPOSITION)

    def memory_for(self, role: SpeakerRole) -> AgentClaimMemory:
        if role == SpeakerRole.HOST or not is_guest_role(role):
            raise ValueError("Only guest roles own claim memory.")
        if role not in self._memories:
            self._memories[role] = AgentClaimMemory(role=role)
        return self._memories[role]

    def other_guest_roles(self, role: SpeakerRole) -> list[SpeakerRole]:
        return [g.role for g in self._guests if g.role != role]

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
        if role == SpeakerRole.HOST:
            raise ValueError("Host remarks are not stored as debate claims.")
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
        return [c.claim for c in self.memory_for(role).claims]

    def format_claims(self, role: SpeakerRole) -> str:
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

    def format_peers_memory(self, role: SpeakerRole) -> str:
        peers = self.other_guest_roles(role)
        if not peers:
            return "(No other guests yet.)"
        blocks: list[str] = []
        name_by_role = {g.role: g.name for g in self._guests}
        for peer in peers:
            label = name_by_role.get(peer, peer.value)
            blocks.append(f"{label}:\n{self.format_claims(peer)}")
        return "\n\n".join(blocks)

    def format_already_used(self, role: SpeakerRole) -> str:
        used = self.already_used_claims(role)
        if not used:
            return "(None yet — opening round.)"
        return "\n".join(f"✓ {claim}" for claim in used)

    def format_defend_or_refine(self, role: SpeakerRole) -> str:
        contradicted = self.memory_for(role).contradicted_claims()
        if not contradicted:
            return "(None — introduce a new idea or gently extend an ACTIVE claim.)"
        lines = []
        for claim in contradicted:
            challenge = claim.contradicted_by[-1] if claim.contradicted_by else "challenged"
            lines.append(
                f"- [{claim.id}] {claim.claim} — currently CONTRADICTED because: {challenge}"
            )
        return "\n".join(lines)

    def open_claims_for_roles(self, roles: list[SpeakerRole]) -> list[DebateClaim]:
        claims: list[DebateClaim] = []
        for role in roles:
            claims.extend(self.memory_for(role).open_claims())
        return claims

    def summarized_context(self) -> str:
        blocks: list[str] = []
        name_by_role = {g.role: g.name for g in self._guests}
        for guest in self._guests:
            label = name_by_role.get(guest.role, guest.role.value)
            blocks.append(f"{label} claims:\n{self.format_claims(guest.role)}")
        return "\n\n".join(blocks) if blocks else "(No claims yet.)"

    def to_debate_summary(self) -> DebateSummary:
        support_points = [c.claim for c in self.memory_for(SpeakerRole.SUPPORT).claims]
        opposition_points = [
            c.claim for c in self.memory_for(SpeakerRole.OPPOSITION).claims
        ]
        participants = [
            ParticipantSummary(
                role=g.role,
                name=g.name,
                points=[c.claim for c in self.memory_for(g.role).claims],
            )
            for g in self._guests
        ]
        return DebateSummary(
            text=self.summarized_context(),
            support_points=support_points,
            opposition_points=opposition_points,
            participants=participants,
        )

    def snapshot(self) -> DebateState:
        guest_memories = [
            self.memory_for(g.role).model_copy(deep=True) for g in self._guests
        ]
        return DebateState(
            debate_id=self._debate_id,
            topic=self._topic,
            language=self._language,
            mood=self._mood,
            support_memory=self.memory_for(SpeakerRole.SUPPORT).model_copy(deep=True),
            opposition_memory=self.memory_for(SpeakerRole.OPPOSITION).model_copy(
                deep=True
            ),
            guest_memories=guest_memories,
            current_round=self._current_round,
        )
