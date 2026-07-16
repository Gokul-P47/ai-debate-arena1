"""Serve cached TTS audio clips."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from app.services.audio_cache import audio_cache

router = APIRouter(prefix="/audio", tags=["Audio"])


@router.get("/{audio_id}")
async def get_audio(audio_id: str) -> Response:
    """Return a previously synthesized debate speech clip."""
    item = audio_cache.get(audio_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Audio clip not found or expired")
    return Response(
        content=item.content,
        media_type=item.mime_type,
        headers={
            "Cache-Control": "private, max-age=3600",
            "Content-Disposition": f'inline; filename="{audio_id}.mp3"',
        },
    )
