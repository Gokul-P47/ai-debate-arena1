"""Host agent — manages the debate show without arguing."""

from collections.abc import AsyncIterator
from datetime import datetime, timezone

from app.providers.base_provider import BaseProvider
from app.schemas.debate_response import DebateMessage, SpeakerRole
from app.services.agent_context import AgentPrompt, topic_locked_prompts
from app.utils.logger import get_logger

logger = get_logger(__name__)

HOST_SPEAKER_NAME = "Host"


class HostAgent:
    """Moderator that welcomes, announces rounds, and closes the debate."""

    def __init__(self, provider: BaseProvider) -> None:
        self._provider = provider

    async def generate(self, prompt: AgentPrompt) -> DebateMessage:
        parts: list[str] = []
        async for chunk in self.stream(prompt):
            parts.append(chunk)
        return self.finalize("".join(parts), prompt.round_number)

    async def stream(self, prompt: AgentPrompt) -> AsyncIterator[str]:
        logger.info("HostAgent streaming round %d segment", prompt.round_number)
        system_prompt, user_prompt = topic_locked_prompts(prompt)
        async for chunk in self._provider.generate_stream(
            prompt=user_prompt,
            system_prompt=system_prompt,
        ):
            if chunk:
                yield chunk

    def finalize(self, content: str, round_number: int) -> DebateMessage:
        return DebateMessage(
            speaker=HOST_SPEAKER_NAME,
            role=SpeakerRole.HOST,
            content=content.strip(),
            timestamp=datetime.now(timezone.utc),
            round_number=max(1, round_number),
        )
