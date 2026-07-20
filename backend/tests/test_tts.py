"""Tests for ElevenLabs TTS cache, audio route, and overlapped stream events."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.schemas.debate_request import DebateMood, DebateRequest
from app.schemas.debate_response import SpeakerRole
from app.services.audio_cache import AudioCache, audio_cache
from app.services.debate_service import DebateService
from app.services.tts_service import ElevenLabsTTSService, SynthesizedSpeech
from tests.test_debate import FakeProvider


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def stub_news_fetch(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _no_news(_query: str, max_results: int = 5):
        return [
            {
                "title": "People talk about the topic everywhere",
                "link": "https://example.com",
                "pub_date": "",
                "source": "Example News",
            }
        ]

    monkeypatch.setattr("app.utils.news.fetch_latest_news", _no_news)
    monkeypatch.setattr("app.services.news_browser.fetch_latest_news", _no_news)


class FakeTTS:
    """Deterministic TTS that stores tiny fake mp3 bytes."""

    def __init__(self) -> None:
        self.calls: list[tuple[SpeakerRole, str]] = []
        self.enabled = True
        self.delay_s = 0.0

    async def synthesize(
        self,
        *,
        text: str,
        role: SpeakerRole,
        language: str = "en",
    ) -> SynthesizedSpeech:
        self.calls.append((role, text))
        if self.delay_s:
            await asyncio.sleep(self.delay_s)
        audio_id = audio_cache.put(f"audio:{role.value}:{text[:24]}".encode(), mime_type="audio/mpeg")
        return SynthesizedSpeech(audio_id=audio_id)


def test_audio_cache_round_trip() -> None:
    cache = AudioCache(ttl_seconds=60)
    audio_id = cache.put(b"hello-mp3", mime_type="audio/mpeg")
    item = cache.get(audio_id)
    assert item is not None
    assert item.content == b"hello-mp3"
    assert cache.get("missing") is None


def test_audio_endpoint_serves_cached_clip() -> None:
    audio_id = audio_cache.put(b"fake-bytes", mime_type="audio/mpeg")
    client = TestClient(app)
    response = client.get(f"/api/v1/audio/{audio_id}")
    assert response.status_code == 200
    assert response.content == b"fake-bytes"
    assert response.headers["content-type"].startswith("audio/mpeg")


def test_audio_endpoint_404_for_unknown() -> None:
    client = TestClient(app)
    response = client.get("/api/v1/audio/does-not-exist")
    assert response.status_code == 404


def test_stream_emits_audio_ready_with_fake_tts() -> None:
    provider = FakeProvider()
    tts = FakeTTS()
    service = DebateService(provider=provider, tts=tts)  # type: ignore[arg-type]
    request = DebateRequest(
        topic="AI should be regulated",
        rounds=1,
        mood=DebateMood.SERIOUS,
        language="en",
    )

    async def _collect() -> list[dict]:
        return [item async for item in service.stream_debate(request)]

    events = asyncio.run(_collect())
    names = [item["event"] for item in events]
    assert "debate_started" in names
    assert "audio_ready" in names
    assert names[-1] == "debate_completed"
    started = next(item for item in events if item["event"] == "debate_started")
    assert started["data"]["ttsEnabled"] is True

    audio_events = [item for item in events if item["event"] == "audio_ready"]
    # opening host + support + opposition + closing host = 4
    assert len(audio_events) == 4
    assert all("audioUrl" in item["data"] for item in audio_events)
    assert tts.calls  # synthesized for each speaking turn


def test_tts_overlaps_with_next_llm_turn() -> None:
    """Support TTS should still be in flight when Opposition tokens start."""
    provider = FakeProvider()
    tts = FakeTTS()
    tts.delay_s = 0.15
    service = DebateService(provider=provider, tts=tts)  # type: ignore[arg-type]
    request = DebateRequest(
        topic="AI should be regulated",
        rounds=1,
        mood=DebateMood.SERIOUS,
        language="en",
    )

    async def _collect() -> list[str]:
        order: list[str] = []
        async for item in service.stream_debate(request):
            if item["event"] == "turn_started" and item["data"]["role"] == "opposition":
                order.append("opposition_started")
            if item["event"] == "audio_ready" and item["data"]["role"] == "support":
                order.append("support_audio")
        return order

    order = asyncio.run(_collect())
    assert "opposition_started" in order
    assert "support_audio" in order
    # Overlap: Opposition turn begins before (or without waiting solely for) Support audio
    assert order.index("opposition_started") < order.index("support_audio")


def test_elevenlabs_service_disabled_without_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ELEVENLABS_API_KEY", "")
    monkeypatch.setenv("TTS_PROVIDER", "elevenlabs")
    monkeypatch.setenv("TTS_ENABLED", "true")
    get_settings.cache_clear()
    service = ElevenLabsTTSService()
    assert service.enabled is False
    result = asyncio.run(
        service.synthesize(text="Hello", role=SpeakerRole.HOST, language="en")
    )
    assert result is None


def test_elevenlabs_service_posts_and_caches(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
    monkeypatch.setenv("TTS_PROVIDER", "elevenlabs")
    monkeypatch.setenv("TTS_ENABLED", "true")
    get_settings.cache_clear()

    mock_response = MagicMock()
    mock_response.content = b"mp3-data"
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.post = AsyncMock(return_value=mock_response)

    monkeypatch.setattr("app.services.tts_service.httpx.AsyncClient", lambda **_: mock_client)

    service = ElevenLabsTTSService()
    assert service.enabled is True
    speech = asyncio.run(
        service.synthesize(text="Welcome to the debate", role=SpeakerRole.HOST, language="en")
    )
    assert speech is not None
    assert audio_cache.get(speech.audio_id) is not None
    mock_client.post.assert_awaited()


def test_openai_tts_service_posts_and_caches(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TTS_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("TTS_ENABLED", "true")
    get_settings.cache_clear()

    mock_response = MagicMock()
    mock_response.content = b"openai-mp3-data"
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock()
    mock_client.__aenter__.return_value = mock_client
    mock_client.__aexit__.return_value = None
    mock_client.post = AsyncMock(return_value=mock_response)

    monkeypatch.setattr("app.services.tts_service.httpx.AsyncClient", lambda **_: mock_client)

    service = ElevenLabsTTSService()
    assert service.enabled is True
    speech = asyncio.run(
        service.synthesize(text="Welcome to the show", role=SpeakerRole.HOST, language="en")
    )
    assert speech is not None
    cached = audio_cache.get(speech.audio_id)
    assert cached is not None
    assert cached.content == b"openai-mp3-data"
    mock_client.post.assert_awaited()

