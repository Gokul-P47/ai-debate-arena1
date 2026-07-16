"""Opposition-side debate agent."""

from collections.abc import AsyncIterator
from datetime import datetime, timezone

from app.providers.base_provider import BaseProvider
from app.schemas.debate_response import DebateMessage, SpeakerRole
from app.services.agent_context import AgentPrompt
from app.utils.logger import get_logger

logger = get_logger(__name__)

OPPOSITION_SPEAKER_NAME = "Sarah"


class OppositionAgent:
    """Agent that argues against the debate topic via the configured LLM."""

    def __init__(self, provider: BaseProvider) -> None:
        self._provider = provider

    async def generate(self, prompt: AgentPrompt) -> DebateMessage:
        """Generate a counterargument (non-streaming)."""
        parts: list[str] = []
        async for chunk in self.stream(prompt):
            parts.append(chunk)
        return self.finalize("".join(parts), prompt.round_number)

    async def stream(self, prompt: AgentPrompt) -> AsyncIterator[str]:
        """Stream opposition argument tokens as they are generated."""
        logger.info(
            "OppositionAgent streaming round %d counterargument",
            prompt.round_number,
        )
        async for chunk in self._provider.generate_stream(
            prompt=prompt.user_prompt,
            system_prompt=prompt.system_prompt,
        ):
            if chunk:
                yield chunk

    def finalize(self, content: str, round_number: int) -> DebateMessage:
        """Build a DebateMessage from streamed content."""
        return DebateMessage(
            speaker=OPPOSITION_SPEAKER_NAME,
            role=SpeakerRole.OPPOSITION,
            content=content.strip(),
            timestamp=datetime.now(timezone.utc),
            round_number=round_number,
        )
