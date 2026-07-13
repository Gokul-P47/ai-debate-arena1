"""Tests for configurable LLM provider factory."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings
from app.providers.factory import get_provider
from app.providers.gemini_provider import GeminiProvider
from app.providers.grok_provider import GrokProvider
from app.providers.openai_provider import OpenAIProvider


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_get_provider_openai() -> None:
    settings = Settings(
        llm_provider="openai",
        openai_api_key="sk-test",
        openai_model="gpt-4o",
    )
    provider = get_provider(settings)
    assert isinstance(provider, OpenAIProvider)


def test_get_provider_grok() -> None:
    settings = Settings(
        llm_provider="grok",
        grok_api_key="xai-test",
        grok_model="grok-3",
    )
    provider = get_provider(settings)
    assert isinstance(provider, GrokProvider)


def test_get_provider_gemini() -> None:
    settings = Settings(
        llm_provider="gemini",
        gemini_api_key="gem-test",
        gemini_model="gemini-3.1-flash-lite",
    )
    provider = get_provider(settings)
    assert isinstance(provider, GeminiProvider)


def test_get_provider_missing_key_raises() -> None:
    settings = Settings(llm_provider="openai", openai_api_key="")
    with pytest.raises(ValueError, match="API key is missing"):
        get_provider(settings)


def test_llm_provider_normalized_case() -> None:
    settings = Settings(llm_provider="GROK", grok_api_key="xai-test")
    assert settings.llm_provider == "grok"


def test_invalid_llm_provider_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(llm_provider="claude")
