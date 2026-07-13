"""Debate response schema definitions."""

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.claim import DebateState
from app.schemas.roles import SpeakerRole

__all__ = [
    "DebateMessage",
    "DebateMetadata",
    "DebateResponse",
    "DebateSummary",
    "DebateTurn",
    "SpeakerRole",
]


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DebateMessage(BaseModel):
    """A single spoken contribution in the debate transcript."""

    model_config = ConfigDict(populate_by_name=True)

    speaker: str = Field(..., description="Display name of the speaker.")
    role: SpeakerRole = Field(..., description="Debate side for this message.")
    content: str = Field(..., description="Argument text.")
    timestamp: datetime = Field(default_factory=_utc_now)
    round_number: int = Field(
        ...,
        ge=1,
        serialization_alias="roundNumber",
        description="1-based round this message belongs to.",
    )


class DebateTurn(BaseModel):
    """One complete round: support argument followed by opposition reply."""

    model_config = ConfigDict(populate_by_name=True)

    round_number: int = Field(..., ge=1, serialization_alias="roundNumber")
    support: DebateMessage
    opposition: DebateMessage


class DebateSummary(BaseModel):
    """Running or final summary of points raised in the debate."""

    model_config = ConfigDict(populate_by_name=True)

    text: str = Field(default="", description="Narrative summary of the debate so far.")
    support_points: list[str] = Field(
        default_factory=list,
        serialization_alias="supportPoints",
        description="Key support claims raised so far.",
    )
    opposition_points: list[str] = Field(
        default_factory=list,
        serialization_alias="oppositionPoints",
        description="Key opposition claims raised so far.",
    )


class DebateMetadata(BaseModel):
    """Operational metadata about how the debate was produced."""

    model_config = ConfigDict(populate_by_name=True)

    provider: str = Field(..., description="Active LLM provider name.")
    model: str = Field(..., description="Model identifier used for generation.")
    total_rounds: int = Field(..., ge=1, serialization_alias="totalRounds")
    created_at: datetime = Field(
        default_factory=_utc_now,
        serialization_alias="createdAt",
    )
    completed_at: datetime | None = Field(
        default=None,
        serialization_alias="completedAt",
    )
    extra: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional additional metadata.",
    )


class DebateResponse(BaseModel):
    """Full response for a completed (or in-progress) debate."""

    model_config = ConfigDict(populate_by_name=True)

    debate_id: str = Field(..., serialization_alias="debateId")
    topic: str
    language: str
    mood: str
    current_round: int = Field(..., ge=0, serialization_alias="currentRound")
    transcript: list[DebateMessage] = Field(default_factory=list)
    turns: list[DebateTurn] = Field(default_factory=list)
    summary: DebateSummary | None = None
    claim_memory: DebateState | None = Field(
        default=None,
        serialization_alias="claimMemory",
        description="Structured per-agent claim memories for this debate.",
    )
    metadata: DebateMetadata
