"""xAI Grok LLM provider (OpenAI-compatible API)."""

from app.core.config import Settings, get_settings
from app.providers.openai_compatible import OpenAICompatibleProvider


class GrokProvider(OpenAICompatibleProvider):
    """Grok-backed language model provider via xAI's OpenAI-compatible API."""

    def __init__(self, settings: Settings | None = None) -> None:
        settings = settings or get_settings()
        super().__init__(
            api_key=settings.grok_api_key,
            model=settings.grok_model,
            provider_name="grok",
            base_url=settings.grok_base_url,
        )
