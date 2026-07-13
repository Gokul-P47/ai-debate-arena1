"""Factory for resolving the configured LLM provider."""

from app.core.config import Settings, get_settings
from app.providers.base_provider import BaseProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.grok_provider import GrokProvider
from app.providers.openai_provider import OpenAIProvider
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_provider(settings: Settings | None = None) -> BaseProvider:
    """Return the LLM provider selected by ``LLM_PROVIDER``.

    Args:
        settings: Optional settings override. Uses cached settings when omitted.

    Returns:
        A concrete ``BaseProvider`` for openai, grok, or gemini.

    Raises:
        ValueError: If ``llm_provider`` is unsupported or the API key is missing.
    """
    settings = settings or get_settings()
    provider = settings.llm_provider

    logger.info("Resolving LLM provider: %s", provider)

    if provider == "openai":
        return OpenAIProvider(settings)
    if provider == "grok":
        return GrokProvider(settings)
    if provider == "gemini":
        return GeminiProvider(settings)

    raise ValueError(
        f"Unsupported LLM_PROVIDER={provider!r}. "
        "Use one of: openai, grok, gemini."
    )
