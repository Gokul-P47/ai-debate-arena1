"""Debate request schema definitions."""

from enum import Enum

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class DebateMood(str, Enum):
    """Supported debate tone presets."""

    SERIOUS = "SERIOUS"
    FUN = "FUN"
    MIXED = "MIXED"


class DebateRequest(BaseModel):
    """Request payload for initiating a talk-show debate."""

    model_config = ConfigDict(populate_by_name=True)

    topic: str = Field(
        ...,
        min_length=1,
        description="The debate topic or proposition.",
        json_schema_extra={"example": "Should AI replace teachers?"},
    )
    rounds: int = Field(
        ...,
        ge=1,
        le=10,
        description="Number of chat segments / rounds.",
        json_schema_extra={"example": 3},
    )
    mood: DebateMood = Field(
        ...,
        description="Tone and style of the talk show.",
        json_schema_extra={"example": DebateMood.MIXED},
    )
    language: str = Field(
        default="en",
        min_length=2,
        max_length=16,
        description="ISO-like language code for generated arguments.",
        json_schema_extra={"example": "en"},
    )
    turn_seconds: int = Field(
        default=45,
        ge=15,
        le=120,
        validation_alias=AliasChoices("turnSeconds", "turn_seconds"),
        serialization_alias="turnSeconds",
        description="Target spoken length for one guest turn (seconds).",
        json_schema_extra={"example": 45},
    )
    participant_count: int = Field(
        default=2,
        ge=2,
        le=4,
        validation_alias=AliasChoices("participantCount", "participant_count"),
        serialization_alias="participantCount",
        description="Number of guest participants (Host is extra). Max 4.",
        json_schema_extra={"example": 3},
    )
