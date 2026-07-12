"""Health check endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/health", tags=["Health"])


class HealthResponse(BaseModel):
    """Health check response schema."""

    status: str = Field(..., description="Service health status.")
    service: str = Field(..., description="Service name.")


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return service health status.

    Returns:
        HealthResponse with status and service name.
    """
    return HealthResponse(status="UP", service="AI Debate Arena API")
