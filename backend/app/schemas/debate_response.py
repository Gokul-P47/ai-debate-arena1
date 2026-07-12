"""Debate response schema definitions."""

from pydantic import BaseModel, Field


class DebateResponse(BaseModel):
    """Placeholder response model for debate generation."""

    message: str = Field(
        ...,
        description="Status or result message for the debate request.",
    )


class DebatePlaceholderResponse(BaseModel):
    """Temporary response returned until debate logic is implemented."""

    message: str = Field(
        default="Debate generation will be implemented in the next phase",
        description="Placeholder message indicating future implementation.",
    )
