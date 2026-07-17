"""Centralized prompt context builder for natural multi-guest conversations."""

from app.core.participants import GuestSpec
from app.core.prompt_templates import (
    render_guest_system_prompt,
    render_guest_user_prompt,
    render_host_system_prompt,
    render_host_user_prompt,
    round_focus_instruction,
)
from app.schemas.debate_request import DebateMood
from app.schemas.debate_response import SpeakerRole
from app.schemas.roles import HostSegment
from app.services.agent_context import AgentContext, AgentPrompt, HostContext
from app.services.memory_service import MemoryService


class ContextBuilder:
    """Build LLM prompts from full conversation transcript + persona context."""

    def __init__(self, memory: MemoryService) -> None:
        self._memory = memory

    def _news_context_text(self) -> str:
        return self._memory.format_news_summary()

    def _guest_roster_text(self) -> str:
        guests = self._memory.guests
        if not guests:
            return "(No guests configured.)"
        return "\n".join(
            f"- {g.name} ({g.stance}) — {g.personality.split('.')[0]}."
            for g in guests
        )

    def _latest_guest_reply(self) -> str:
        """Last guest utterance in the current chat (for in-round continuity)."""
        for message in reversed(self._memory.messages):
            if message.role == SpeakerRole.HOST:
                continue
            speaker = message.speaker or message.role.value
            return f"{speaker}: {message.content.strip()}"
        return ""

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
        if peer_latest and peer_latest.strip():
            reply_to = peer_latest.strip()
        else:
            reply_to = self._latest_guest_reply()

        scenario_seed = self._memory.pick_scenario_seed()
        unused_angles = self._memory.format_unused_angles()
        controversial = self._memory.is_controversial
        opinion_brief = self._memory.opinion_brief_for(guest.role)

        context = AgentContext(
            topic=topic,
            mood=mood,
            language=language,
            round_number=round_number,
            total_rounds=total_rounds,
            turn_seconds=turn_seconds,
            side=guest.role,
            speaker_name=guest.name,
            personality=guest.personality,
            viewpoint=guest.viewpoint,
            conversation_transcript=self._memory.format_conversation_transcript(),
            round_focus=round_focus_instruction(round_number, total_rounds),
            guest_roster=self._guest_roster_text(),
            news_context=self._news_context_text(),
            reply_to=reply_to,
            scenario_seed=scenario_seed,
            unused_angles=unused_angles,
            controversial=controversial,
            opinion_brief=opinion_brief,
        )
        return AgentPrompt(
            system_prompt=render_guest_system_prompt(context),
            user_prompt=render_guest_user_prompt(context),
            round_number=round_number,
            side=guest.role,
            topic=topic,
        )

    def build_support_prompt(self, **kwargs) -> AgentPrompt:  # type: ignore[no-untyped-def]
        guests = self._memory.guests
        guest = next((g for g in guests if g.role == SpeakerRole.SUPPORT), guests[0])
        kwargs.pop("opponent_latest", None)
        return self.build_guest_prompt(guest=guest, **kwargs)

    def build_opposition_prompt(self, **kwargs) -> AgentPrompt:  # type: ignore[no-untyped-def]
        guests = self._memory.guests
        guest = next(
            (g for g in guests if g.role == SpeakerRole.OPPOSITION),
            guests[-1],
        )
        kwargs.pop("opponent_latest", None)
        return self.build_guest_prompt(guest=guest, **kwargs)

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
        focus = round_focus_instruction(max(1, round_number), total_rounds)
        if segment == HostSegment.OPENING:
            focus = "Opening beat — set the room; the conversation has not started yet."
        elif segment == HostSegment.CLOSING:
            focus = "Closing beat — thank guests and leave the audience with a warm wrap."

        context = HostContext(
            topic=topic,
            mood=mood,
            language=language,
            round_number=round_number,
            total_rounds=total_rounds,
            turn_seconds=turn_seconds,
            segment=segment,
            guest_roster=self._guest_roster_text(),
            conversation_transcript=self._memory.format_conversation_transcript(),
            round_focus=focus,
            news_context=self._news_context_text(),
            controversial=self._memory.is_controversial,
        )
        return AgentPrompt(
            system_prompt=render_host_system_prompt(context),
            user_prompt=render_host_user_prompt(context),
            round_number=max(1, round_number),
            side=SpeakerRole.HOST,
            topic=topic,
        )
