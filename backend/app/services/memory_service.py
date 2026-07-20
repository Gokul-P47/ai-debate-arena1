"""Conversation state manager: full transcript + optional legacy claim helpers."""

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
    """Stores the full conversation transcript used for LLM context.

    Claim-memory helpers remain for API compatibility / unit tests but are no
    longer fed into generation prompts.
    """

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
        self._browsed_notes = ""
        self._used_scenario_seeds: list[str] = []

        self._memories: dict[SpeakerRole, AgentClaimMemory] = {
            g.role: AgentClaimMemory(role=g.role) for g in self._guests
        }
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

    @property
    def browsed_notes(self) -> str:
        return self._browsed_notes

    def set_browsed_notes(self, notes: str) -> None:
        self._browsed_notes = (notes or "").strip()

    def set_news_articles(self, articles: list[dict[str, str]]) -> None:
        self._news_articles = list(articles) if articles else []

    @property
    def is_controversial(self) -> bool:
        from app.services.news_browser import is_controversial_pack

        return is_controversial_pack(self._browsed_notes)

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

    def format_conversation_transcript(self) -> str:
        """Full dialogue so far, grouped by round — primary LLM context."""
        if not self._messages:
            return "(The conversation has not started yet.)"

        lines: list[str] = []
        current_round: int | None = None
        for message in self._messages:
            if message.round_number != current_round:
                current_round = message.round_number
                lines.append(f"Round {current_round}")
                lines.append("")
            speaker = message.speaker or message.role.value
            lines.append(f"{speaker}:")
            lines.append(message.content.strip())
            lines.append("")
        return "\n".join(lines).strip()

    def format_news_summary(self) -> str:
        """Casual notes from the LLM news browse (not raw headlines)."""
        return self._browsed_notes

    def list_background_facts(self) -> list[str]:
        """Conversation angles from the knowledge pack (hooks + lived angles + knowledge)."""
        from app.services.news_browser import extract_section_bullets

        pack = self._browsed_notes or ""
        angles: list[str] = []
        for section in ("TALK HOOKS", "LIVED ANGLES", "KNOWLEDGE", "FOR", "AGAINST"):
            for bullet in extract_section_bullets(pack, section):
                if bullet and bullet not in angles:
                    angles.append(bullet)
        if angles:
            return angles
        # Fallback: any "- " lines
        for raw in pack.splitlines():
            line = raw.strip()
            if line.startswith("-"):
                text = line.lstrip("-").strip()
                if text and not text.upper().startswith("CONTROVERSIAL"):
                    angles.append(text)
        if angles:
            return angles
        for article in self._news_articles:
            title = (article.get("title") or "").strip()
            if title:
                angles.append(title)
        return angles

    def unused_background_facts(self) -> list[str]:
        """Angles not yet assigned as a soft turn hint."""
        used = {s.lower() for s in self._used_scenario_seeds}
        return [f for f in self.list_background_facts() if f.lower() not in used]

    def pick_scenario_seed(self) -> str:
        """Claim the next unused conversation angle (soft hint, not a news script)."""
        unused = self.unused_background_facts()
        if not unused:
            facts = self.list_background_facts()
            if not facts:
                return ""
            idx = len(self._messages) % len(facts)
            seed = facts[idx]
        else:
            seed = unused[0]

        self._used_scenario_seeds.append(seed)
        return seed

    def format_unused_angles(self) -> str:
        """List remaining angles so speakers know the show will cover more."""
        unused = self.unused_background_facts()
        if not unused:
            return "(Keep exploring fresh sides of the topic — do not rehash.)"
        lines = [f"- {fact}" for fact in unused[:6]]
        return "Other angles still available later:\n" + "\n".join(lines)

    def opinion_brief_for(self, role: SpeakerRole) -> str:
        """Optional on-topic enrichment — not a mandate to oppose the other guest."""
        from app.services.news_browser import extract_section_bullets

        pack = self._browsed_notes or ""
        hooks = extract_section_bullets(pack, "TALK HOOKS")
        if role == SpeakerRole.SUPPORT:
            lean = extract_section_bullets(pack, "FOR")[:2]
        elif role == SpeakerRole.OPPOSITION:
            # Prefer hooks over AGAINST so Sarah does not auto-counter every turn.
            lean = extract_section_bullets(pack, "LIVED ANGLES")[:2]
            if not lean:
                lean = extract_section_bullets(pack, "AGAINST")[:1]
        else:
            lean = []

        points: list[str] = []
        for bullet in hooks[:3] + lean:
            if bullet and bullet not in points:
                points.append(bullet)
        if not points:
            return ""
        label = (
            "Optional on-topic sparks (enrich the TOPIC — do NOT use to rebut "
            "the previous speaker every turn; prefer agree + add):"
        )
        return label + "\n" + "\n".join(f"- {p}" for p in points[:5])

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
        """Prefer format_conversation_transcript for prompts."""
        return self.format_conversation_transcript()

    @staticmethod
    def _snippet(text: str, max_len: int = 160) -> str:
        cleaned = " ".join(text.split()).strip()
        if len(cleaned) <= max_len:
            return cleaned
        return cleaned[: max_len - 1].rstrip() + "…"

    def _points_for_role(self, role: SpeakerRole) -> list[str]:
        points = [
            self._snippet(m.content)
            for m in self._messages
            if m.role == role and m.content.strip()
        ]
        return points[-3:]

    def to_debate_summary(self) -> DebateSummary:
        support_points = self._points_for_role(SpeakerRole.SUPPORT)
        opposition_points = self._points_for_role(SpeakerRole.OPPOSITION)
        participants = [
            ParticipantSummary(
                role=g.role,
                name=g.name,
                points=self._points_for_role(g.role),
            )
            for g in self._guests
        ]
        transcript = self.format_conversation_transcript()
        preview = self._snippet(transcript, max_len=400) if self._messages else ""
        return DebateSummary(
            text=preview or "Conversation complete.",
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
