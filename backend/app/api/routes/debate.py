"""Debate endpoint — placeholder for future implementation."""

from fastapi import APIRouter

from app.schemas.debate_request import DebateRequest
from app.schemas.debate_response import DebatePlaceholderResponse
from app.services.debate_service import DebateService

router = APIRouter(prefix="/debates", tags=["Debates"])

_debate_service = DebateService()


@router.post("", response_model=DebatePlaceholderResponse)
async def create_debate(request: DebateRequest) -> DebatePlaceholderResponse:
    """Accept a debate request and return a placeholder response.

    Args:
        request: Validated debate request payload.

    Returns:
        Placeholder message until debate generation is implemented.
    """
    return await _debate_service.create_debate(request)
