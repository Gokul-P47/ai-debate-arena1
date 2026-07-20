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

    # TTS Configuration (optional — debates still stream text without a key)
    tts_enabled: bool = Field(
        default=True,
        description="When true and an API key is set, synthesize speech per turn",
    )
    tts_provider: Literal["elevenlabs", "openai"] = Field(
        default="elevenlabs",
        description="Active TTS provider: elevenlabs | openai",
    )

    # ElevenLabs TTS Settings
    elevenlabs_api_key: str = Field(default="", description="ElevenLabs API key")
    elevenlabs_model: str = Field(
        default="eleven_flash_v2_5",
        description="ElevenLabs TTS model id (flash for low-latency live debates)",
    )
    elevenlabs_voice_host: str = Field(
        default="JBFqnCBsd6RMkjVDRZzb",
        description="ElevenLabs voice id for the Host",
    )
    elevenlabs_voice_support: str = Field(
        default="EXAVITQu4vr4xnSDxMaL",
        description="ElevenLabs voice id for Support",
    )
    elevenlabs_voice_opposition: str = Field(
        default="pNInz6obpgDQGcFmaJgB",
        description="ElevenLabs voice id for Friendly Critic (guest 2)",
    )
    elevenlabs_voice_guest3: str = Field(
        default="VR6AewLTigWG4xSOukaG",
        description="ElevenLabs voice id for Pragmatist (guest 3)",
    )
    elevenlabs_voice_guest4: str = Field(
        default="TxGEqnHWrfWFTfGW9XjX",
        description="ElevenLabs voice id for Wild Card (guest 4)",
    )

    # OpenAI TTS Settings
    openai_tts_model: str = Field(
        default="tts-1",
        description="OpenAI TTS model id: tts-1 | tts-1-hd",
    )
    openai_voice_host: str = Field(
        default="alloy",
        description="OpenAI voice for the Host: alloy | echo | fable | onyx | nova | shimmer",
    )
    openai_voice_support: str = Field(
        default="echo",
        description="OpenAI voice for Support debater",
    )
    openai_voice_opposition: str = Field(
        default="nova",
        description="OpenAI voice for Opposition debater",
    )
    openai_voice_guest3: str = Field(
        default="onyx",
        description="OpenAI voice for Guest 3",
    )
    openai_voice_guest4: str = Field(
        default="shimmer",
        description="OpenAI voice for Guest 4",
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
