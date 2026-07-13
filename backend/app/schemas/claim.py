"""Structured debate claim models for claim-based memory."""

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.roles import SpeakerRole


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ClaimStatus(str, Enum):
    """Lifecycle status of a debate claim."""

    ACTIVE = "ACTIVE"
    CONTRADICTED = "CONTRADICTED"
    DEFENDED = "DEFENDED"
    RESOLVED = "RESOLVED"


class DebateClaim(BaseModel):
    """One important argument extracted from an agent response."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., description="Stable claim identifier, e.g. claim-001.")
    claim: str = Field(..., description="Concise core argument text.")
    category: str = Field(
        default="General",
        description="Claim category, e.g. Economics, Ethics, Feasibility.",
    )
    confidence: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Extractor confidence that this is a real core claim.",
    )
    importance: float = Field(default=0.7, ge=0.0, le=1.0)
    round: int = Field(..., ge=1, description="Round in which the claim was introduced.")
    status: ClaimStatus = Field(default=ClaimStatus.ACTIVE)
    contradicted_by: list[str] = Field(
        default_factory=list,
        serialization_alias="contradictedBy",
    )
    defended_by: list[str] = Field(
        default_factory=list,
        serialization_alias="defendedBy",
    )
    timestamp: datetime = Field(default_factory=_utc_now)
    owner: SpeakerRole = Field(..., description="Which agent owns this claim.")


class AgentClaimMemory(BaseModel):
    """Claim memory owned by a single debate side."""

    model_config = ConfigDict(populate_by_name=True)

    role: SpeakerRole
    claims: list[DebateClaim] = Field(default_factory=list)

    def active_claims(self) -> list[DebateClaim]:
        return [c for c in self.claims if c.status == ClaimStatus.ACTIVE]

    def contradicted_claims(self) -> list[DebateClaim]:
        return [c for c in self.claims if c.status == ClaimStatus.CONTRADICTED]

    def open_claims(self) -> list[DebateClaim]:
        """Claims that still need engagement (active, contradicted, or defended)."""
        return [
            c
            for c in self.claims
            if c.status
            in {ClaimStatus.ACTIVE, ClaimStatus.CONTRADICTED, ClaimStatus.DEFENDED}
        ]


class DebateState(BaseModel):
    """Central structured state for one debate session."""

    model_config = ConfigDict(populate_by_name=True)

    debate_id: str = Field(..., serialization_alias="debateId")
    topic: str
    language: str
    mood: str
    support_memory: AgentClaimMemory = Field(..., serialization_alias="supportMemory")
    opposition_memory: AgentClaimMemory = Field(
        ...,
        serialization_alias="oppositionMemory",
    )
    current_round: int = Field(default=0, serialization_alias="currentRound")

    def memory_for(self, role: SpeakerRole) -> AgentClaimMemory:
        if role == SpeakerRole.SUPPORT:
            return self.support_memory
        return self.opposition_memory
