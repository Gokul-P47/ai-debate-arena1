"""Centralized smart prompt context builder for multi-guest talk shows."""

from app.core.participants import GuestSpec
from app.core.prompt_templates import (
    render_guest_system_prompt,
    render_guest_user_prompt,
    render_host_system_prompt,
    render_host_user_prompt,
)
from app.schemas.debate_request import DebateMood
from app.schemas.debate_response import SpeakerRole
from app.schemas.roles import HostSegment
from app.services.agent_context import AgentContext, AgentPrompt, HostContext
from app.services.memory_service import MemoryService


class ContextBuilder:
    """Build optimized LLM prompts from claim memory — never the full transcript."""

    def __init__(self, memory: MemoryService) -> None:
        self._memory = memory

    def _news_context_text(self) -> str:
        articles = self._memory.news_articles
        if not articles:
            return ""
        lines = []
        for a in articles:
            lines.append(f"- [Source: {a['source']}] Title: {a['title']}")
        return "\n".join(lines)

    def _guest_roster_text(self) -> str:
        guests = self._memory.guests
        if not guests:
            return "(No guests configured.)"
        return "\n".join(f"- {g.name} ({g.label}) — stance: {g.stance}" for g in guests)

    def build_guest_prompt(
        self,
        *,
        guest: GuestSpec,
        topic: str,
        mood: DebateMood,
        language: str,
        round_number: int,
        total_rounds: int,
        turn_seconds: int,
        peer_latest: str | None = None,
    ) -> AgentPrompt:
        """Build the only guest LLM input for this turn."""
        latest = (peer_latest or "").strip() or (
            "(You speak first this segment — open with your view.)"
        )
        context = AgentContext(
            topic=topic,
            mood=mood,
            language=language,
            round_number=round_number,
            total_rounds=total_rounds,
            turn_seconds=turn_seconds,
            side=guest.role,
            speaker_name=guest.name,
            stance_instructions=guest.stance_instructions,
            own_memory=self._memory.format_claims(guest.role),
            peers_memory=self._memory.format_peers_memory(guest.role),
            peer_latest=latest,
            already_used=self._memory.format_already_used(guest.role),
            defend_or_refine=self._memory.format_defend_or_refine(guest.role),
            guidance=self._guidance_for(guest),
            guest_roster=self._guest_roster_text(),
            news_context=self._news_context_text(),
        )
        return AgentPrompt(
            system_prompt=render_guest_system_prompt(context),
            user_prompt=render_guest_user_prompt(context),
            round_number=round_number,
            side=guest.role,
        )

    # Back-compat wrappers used by older tests
    def build_support_prompt(self, **kwargs) -> AgentPrompt:  # type: ignore[no-untyped-def]
        guests = self._memory.guests
        guest = next((g for g in guests if g.role == SpeakerRole.SUPPORT), guests[0])
        peer_latest = kwargs.pop("opponent_latest", None)
        return self.build_guest_prompt(
            guest=guest, peer_latest=peer_latest, **kwargs
        )

    def build_opposition_prompt(self, **kwargs) -> AgentPrompt:  # type: ignore[no-untyped-def]
        guests = self._memory.guests
        guest = next(
            (g for g in guests if g.role == SpeakerRole.OPPOSITION),
            guests[-1],
        )
        peer_latest = kwargs.pop("opponent_latest", None)
        return self.build_guest_prompt(
            guest=guest, peer_latest=peer_latest, **kwargs
        )

    def build_host_prompt(
        self,
        *,
        topic: str,
        mood: DebateMood,
        language: str,
        round_number: int,
        total_rounds: int,
        turn_seconds: int,
        segment: HostSegment,
    ) -> AgentPrompt:
        context = HostContext(
            topic=topic,
            mood=mood,
            language=language,
            round_number=round_number,
            total_rounds=total_rounds,
            turn_seconds=turn_seconds,
            segment=segment,
            guest_roster=self._guest_roster_text(),
            claim_overview=self._memory.summarized_context(),
            news_context=self._news_context_text(),
        )
        return AgentPrompt(
            system_prompt=render_host_system_prompt(context),
            user_prompt=render_host_user_prompt(context),
            round_number=max(1, round_number),
            side=SpeakerRole.HOST,
        )

    @staticmethod
    def _guidance_for(guest: GuestSpec) -> str:
        return (
            "Talk-show conversation rules:\n"
            f"1) Stay true to your stance ({guest.stance}).\n"
            "2) Do NOT repeat already-used points unless softly clarifying.\n"
            "3) You may contradict other guests — politely and warmly.\n"
            "4) React to the latest peer reply when one exists.\n"
            "5) This is a talk show couch, not a courtroom."
        )
