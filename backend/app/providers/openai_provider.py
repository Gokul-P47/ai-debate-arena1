"""OpenAI LLM provider implementation."""

from app.core.config import Settings, get_settings
from app.providers.openai_compatible import OpenAICompatibleProvider


class OpenAIProvider(OpenAICompatibleProvider):
    """OpenAI-backed language model provider."""

    def __init__(self, settings: Settings | None = None) -> None:
        settings = settings or get_settings()
        super().__init__(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            provider_name="openai",
        )
