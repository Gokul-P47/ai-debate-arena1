"""Centralized smart prompt context builder (no full conversation history)."""

from app.core.prompt_templates import (
    render_opposition_system_prompt,
    render_opposition_user_prompt,
    render_support_system_prompt,
    render_support_user_prompt,
)
from app.schemas.debate_request import DebateMood
from app.schemas.debate_response import SpeakerRole
from app.services.agent_context import AgentContext, AgentPrompt
from app.services.memory_service import MemoryService


class ContextBuilder:
    """Build optimized LLM prompts from claim memory — never the full transcript.

    Inputs:
    - Topic, mood, language
    - Support / opposition claim memories
    - Latest opponent response
    - Current round
    - Already-used claims (anti-repetition)
    """

    def __init__(self, memory: MemoryService) -> None:
        self._memory = memory

    def build_context(
        self,
        *,
        topic: str,
        mood: DebateMood,
        language: str,
        round_number: int,
        total_rounds: int,
        side: SpeakerRole,
        opponent_latest: str | None = None,
    ) -> AgentContext:
        opponent_role = (
            SpeakerRole.OPPOSITION
            if side == SpeakerRole.SUPPORT
            else SpeakerRole.SUPPORT
        )

        if opponent_latest is not None and opponent_latest.strip():
            latest = opponent_latest.strip()
        elif side == SpeakerRole.SUPPORT:
            latest = self._memory.latest_opposition_content or (
                "(No opponent response yet — open the debate.)"
            )
        else:
            latest = self._memory.latest_support_content or (
                "(No opponent response yet.)"
            )

        return AgentContext(
            topic=topic,
            mood=mood,
            language=language,
            round_number=round_number,
            total_rounds=total_rounds,
            side=side,
            own_memory=self._memory.format_claims(side),
            opponent_memory=self._memory.format_claims(opponent_role),
            opponent_latest=latest,
            already_used=self._memory.format_already_used(side),
            defend_or_refine=self._memory.format_defend_or_refine(side),
            guidance=self._guidance_for(side),
        )

    def build_support_prompt(
        self,
        *,
        topic: str,
        mood: DebateMood,
        language: str,
        round_number: int,
        total_rounds: int,
        opponent_latest: str | None = None,
    ) -> AgentPrompt:
        """Build the only Support LLM input for this turn."""
        context = self.build_context(
            topic=topic,
            mood=mood,
            language=language,
            round_number=round_number,
            total_rounds=total_rounds,
            side=SpeakerRole.SUPPORT,
            opponent_latest=opponent_latest,
        )
        return AgentPrompt(
            system_prompt=render_support_system_prompt(context),
            user_prompt=render_support_user_prompt(context),
            round_number=round_number,
            side=SpeakerRole.SUPPORT,
        )

    def build_opposition_prompt(
        self,
        *,
        topic: str,
        mood: DebateMood,
        language: str,
        round_number: int,
        total_rounds: int,
        opponent_latest: str | None = None,
    ) -> AgentPrompt:
        """Build the only Opposition LLM input for this turn."""
        context = self.build_context(
            topic=topic,
            mood=mood,
            language=language,
            round_number=round_number,
            total_rounds=total_rounds,
            side=SpeakerRole.OPPOSITION,
            opponent_latest=opponent_latest,
        )
        return AgentPrompt(
            system_prompt=render_opposition_system_prompt(context),
            user_prompt=render_opposition_user_prompt(context),
            round_number=round_number,
            side=SpeakerRole.OPPOSITION,
        )

    def build(self, **kwargs) -> AgentContext:  # type: ignore[no-untyped-def]
        """Backwards-compatible alias for ``build_context``."""
        return self.build_context(**kwargs)

    @staticmethod
    def _guidance_for(side: SpeakerRole) -> str:
        if side == SpeakerRole.SUPPORT:
            return (
                "Progress rules:\n"
                "1) Do NOT repeat any claim marked already-used unless you are defending it.\n"
                "2) If a claim is CONTRADICTED: defend it with stronger reasoning, refine it, "
                "or introduce a genuinely new supporting argument.\n"
                "3) Prefer new angles over restating ACTIVE claims.\n"
                "4) Every round must advance the debate."
            )
        return (
            "Progress rules:\n"
            "1) Directly challenge ACTIVE opponent claims that are still unchallenged.\n"
            "2) Do NOT repeat counterarguments already recorded as challenges.\n"
            "3) If your own claim is CONTRADICTED: defend/refine it or open a new attack line.\n"
            "4) Every round must advance the debate."
        )
