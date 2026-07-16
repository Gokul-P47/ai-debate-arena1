"""Debate endpoints — blocking and streaming."""

import json
from collections.abc import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.debate_request import DebateRequest
from app.schemas.debate_response import DebateResponse
from app.services.debate_service import DebateService

router = APIRouter(prefix="/debates", tags=["Debates"])

_debate_service = DebateService()


@router.post("", response_model=DebateResponse, response_model_by_alias=True)
async def create_debate(request: DebateRequest) -> DebateResponse:
    """Run a multi-round debate and return the full transcript (blocking)."""
    return await _debate_service.create_debate(request)


def _format_sse(event: str, data: dict) -> str:
    payload = json.dumps(data, ensure_ascii=False, default=str)
    return f"event: {event}\ndata: {payload}\n\n"


@router.post("/stream")
async def stream_debate(request: DebateRequest) -> StreamingResponse:
    """Stream debate tokens and lifecycle events via Server-Sent Events.

    Events: debate_started, turn_started, token, message_completed,
    audio_ready, status, debate_completed, error.
    """

    async def event_generator() -> AsyncIterator[str]:
        async for item in _debate_service.stream_debate(request):
            yield _format_sse(item["event"], item["data"])

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
