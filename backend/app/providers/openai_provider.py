"""OpenAI LLM provider implementation."""

from typing import AsyncIterator

from app.core.config import Settings, get_settings
from app.providers.base_provider import BaseProvider
from app.utils.logger import get_logger

logger = get_logger(__name__)


class OpenAIProvider(BaseProvider):
    """OpenAI-backed language model provider.

    Placeholder implementation for future OpenAI API integration.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        """Initialize the OpenAI provider.

        Args:
            settings: Application settings. Uses cached settings if not provided.
        """
        self._settings = settings or get_settings()
        logger.info("OpenAIProvider initialized with model: %s", self._settings.openai_model)

    async def generate(self, prompt: str, system_prompt: str) -> str:
        """Generate a text completion using the OpenAI API.

        Args:
            prompt: User or contextual prompt for the model.
            system_prompt: System-level instruction for the model.

        Returns:
            Generated text response.

        Raises:
            NotImplementedError: OpenAI integration is not yet implemented.
        """
        raise NotImplementedError("OpenAI generate() will be implemented in the next phase")

    async def generate_stream(self, prompt: str, system_prompt: str) -> AsyncIterator[str]:
        """Stream a text completion using the OpenAI API.

        Args:
            prompt: User or contextual prompt for the model.
            system_prompt: System-level instruction for the model.

        Yields:
            Incremental chunks of generated text.

        Raises:
            NotImplementedError: OpenAI streaming is not yet implemented.
        """
        raise NotImplementedError(
            "OpenAI generate_stream() will be implemented in the next phase"
        )
