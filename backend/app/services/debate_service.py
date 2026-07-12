"""Debate orchestration service."""

from app.schemas.debate_request import DebateRequest
from app.schemas.debate_response import DebatePlaceholderResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DebateService:
    """Service layer for debate generation and orchestration.

    Placeholder for future debate logic implementation.
    """

    async def create_debate(self, request: DebateRequest) -> DebatePlaceholderResponse:
        """Handle a debate creation request.

        Args:
            request: Validated debate request payload.

        Returns:
            Placeholder response until debate generation is implemented.
        """
        logger.info(
            "Debate request received — topic=%r, rounds=%d, mood=%s",
            request.topic,
            request.rounds,
            request.mood.value,
        )
        return DebatePlaceholderResponse()
