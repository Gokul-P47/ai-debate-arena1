"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

LLMProviderName = Literal["openai", "grok", "gemini"]


class Settings(BaseSettings):
    """Pydantic settings for the AI Debate Arena API."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    llm_provider: LLMProviderName = Field(
        default="openai",
        description="Active LLM provider: openai | grok | gemini",
    )

    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(default="gpt-4o", description="OpenAI model identifier")

    grok_api_key: str = Field(default="", description="xAI Grok API key")
    grok_model: str = Field(default="grok-3", description="Grok model identifier")
    grok_base_url: str = Field(
        default="https://api.x.ai/v1",
        description="xAI OpenAI-compatible API base URL",
    )

    gemini_api_key: str = Field(default="", description="Google Gemini API key")
    gemini_model: str = Field(
        default="gemini-3.1-flash-lite",
        description="Gemini model identifier",
    )

    summary_interval_turns: int = Field(
        default=2,
        ge=1,
        le=10,
        description="Refresh LLM running summary every N completed turns",
    )
    recent_message_limit: int = Field(
        default=4,
        ge=1,
        le=20,
        description="How many recent messages ContextBuilder includes in prompts",
    )

    @field_validator("llm_provider", mode="before")
    @classmethod
    def normalize_llm_provider(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower()
        return value


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance."""
    return Settings()
