"""Debate request schema definitions."""

from enum import Enum

from pydantic import BaseModel, Field


class DebateMood(str, Enum):
    """Supported debate tone presets."""

    SERIOUS = "SERIOUS"


class DebateRequest(BaseModel):
    """Request payload for initiating a debate."""

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
        description="Number of debate rounds.",
        json_schema_extra={"example": 3},
    )
    mood: DebateMood = Field(
        ...,
        description="Tone and style of the debate.",
        json_schema_extra={"example": DebateMood.SERIOUS},
    )
