"""A single talk-show guest agent (parameterized role + display name)."""

from collections.abc import AsyncIterator
from datetime import datetime, timezone

from app.providers.base_provider import BaseProvider
from app.schemas.debate_response import DebateMessage, SpeakerRole
from app.services.agent_context import AgentPrompt
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GuestAgent:
    """Generic guest that argues from a configured stance."""

    def __init__(
        self,
        provider: BaseProvider,
        *,
        role: SpeakerRole,
        speaker_name: str,
    ) -> None:
        self._provider = provider
        self._role = role
        self._speaker_name = speaker_name

    @property
    def role(self) -> SpeakerRole:
        return self._role

    @property
    def speaker_name(self) -> str:
        return self._speaker_name

    async def generate(self, prompt: AgentPrompt) -> DebateMessage:
        parts: list[str] = []
        async for chunk in self.stream(prompt):
            parts.append(chunk)
        return self.finalize("".join(parts), prompt.round_number)

    async def stream(self, prompt: AgentPrompt) -> AsyncIterator[str]:
        logger.info(
            "GuestAgent [%s] streaming round %d",
            self._speaker_name,
            prompt.round_number,
        )
        async for chunk in self._provider.generate_stream(
            prompt=prompt.user_prompt,
            system_prompt=prompt.system_prompt,
        ):
            if chunk:
                yield chunk

    def finalize(self, content: str, round_number: int) -> DebateMessage:
        return DebateMessage(
            speaker=self._speaker_name,
            role=self._role,
            content=content.strip(),
            timestamp=datetime.now(timezone.utc),
            round_number=round_number,
        )
