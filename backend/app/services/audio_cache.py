"""In-memory cache for synthesized debate audio clips."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import Lock
from uuid import uuid4


@dataclass(frozen=True)
class CachedAudio:
    """One synthesized speech clip ready for HTTP delivery."""

    audio_id: str
    content: bytes
    mime_type: str
    created_at: datetime


class AudioCache:
    """Process-local store for short-lived TTS audio blobs."""

    def __init__(self, *, ttl_seconds: int = 3600) -> None:
        self._ttl = timedelta(seconds=ttl_seconds)
        self._items: dict[str, CachedAudio] = {}
        self._lock = Lock()

    def put(self, content: bytes, *, mime_type: str = "audio/mpeg") -> str:
        self._purge_expired()
        audio_id = str(uuid4())
        item = CachedAudio(
            audio_id=audio_id,
            content=content,
            mime_type=mime_type,
            created_at=datetime.now(timezone.utc),
        )
        with self._lock:
            self._items[audio_id] = item
        return audio_id

    def get(self, audio_id: str) -> CachedAudio | None:
        self._purge_expired()
        with self._lock:
            return self._items.get(audio_id)

    def _purge_expired(self) -> None:
        cutoff = datetime.now(timezone.utc) - self._ttl
        with self._lock:
            expired = [
                key
                for key, item in self._items.items()
                if item.created_at < cutoff
            ]
            for key in expired:
                del self._items[key]


audio_cache = AudioCache()
