"""Text-to-speech for debate agents supporting ElevenLabs and OpenAI."""

from __future__ import annotations

from dataclasses import dataclass
import httpx

from app.core.config import Settings, get_settings
from app.schemas.debate_response import SpeakerRole
from app.services.audio_cache import audio_cache
from app.utils.logger import get_logger

logger = get_logger(__name__)

ELEVENLABS_TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"


@dataclass(frozen=True)
class SynthesizedSpeech:
    """Result of a successful TTS synthesis."""

    audio_id: str
    mime_type: str = "audio/mpeg"


class TTSService:
    """Generate per-role speech clips via ElevenLabs or OpenAI and cache the bytes."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    @property
    def enabled(self) -> bool:
        if not self._settings.tts_enabled:
            return False
        if self._settings.tts_provider == "openai":
            return bool(self._settings.openai_api_key.strip())
        return bool(self._settings.elevenlabs_api_key.strip())

    def voice_for(self, role: SpeakerRole) -> str:
        if self._settings.tts_provider == "openai":
            if role == SpeakerRole.HOST:
                return self._settings.openai_voice_host
            if role == SpeakerRole.SUPPORT:
                return self._settings.openai_voice_support
            if role == SpeakerRole.OPPOSITION:
                return self._settings.openai_voice_opposition
            if role == SpeakerRole.GUEST3:
                return self._settings.openai_voice_guest3
            if role == SpeakerRole.GUEST4:
                return self._settings.openai_voice_guest4
            return self._settings.openai_voice_support
        else:
            if role == SpeakerRole.HOST:
                return self._settings.elevenlabs_voice_host
            if role == SpeakerRole.SUPPORT:
                return self._settings.elevenlabs_voice_support
            if role == SpeakerRole.OPPOSITION:
                return self._settings.elevenlabs_voice_opposition
            if role == SpeakerRole.GUEST3:
                return self._settings.elevenlabs_voice_guest3
            if role == SpeakerRole.GUEST4:
                return self._settings.elevenlabs_voice_guest4
            return self._settings.elevenlabs_voice_support

    async def synthesize(
        self,
        *,
        text: str,
        role: SpeakerRole,
        language: str = "en",
    ) -> SynthesizedSpeech | None:
        """Synthesize speech and store it in the audio cache.

        Returns ``None`` when TTS is disabled or the text is empty.
        """
        cleaned = text.strip()
        if not cleaned or not self.enabled:
            return None

        if self._settings.tts_provider == "openai":
            return await self._synthesize_openai(cleaned, role)
        else:
            return await self._synthesize_elevenlabs(cleaned, role, language)

    async def _synthesize_openai(
        self,
        text: str,
        role: SpeakerRole,
    ) -> SynthesizedSpeech:
        url = "https://api.openai.com/v1/audio/speech"
        voice = self.voice_for(role)
        payload = {
            "model": self._settings.openai_tts_model,
            "input": text,
            "voice": voice,
        }
        headers = {
            "Authorization": f"Bearer {self._settings.openai_api_key}",
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }

        logger.info(
            "OpenAI TTS role=%s voice=%s chars=%d",
            role.value,
            voice,
            len(text),
        )

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            audio_bytes = response.content

        if not audio_bytes:
            raise RuntimeError("OpenAI TTS returned empty audio")

        audio_id = audio_cache.put(audio_bytes, mime_type="audio/mpeg")
        return SynthesizedSpeech(audio_id=audio_id, mime_type="audio/mpeg")

    async def _synthesize_elevenlabs(
        self,
        text: str,
        role: SpeakerRole,
        language: str = "en",
    ) -> SynthesizedSpeech:
        voice_id = self.voice_for(role)
        url = ELEVENLABS_TTS_URL.format(voice_id=voice_id)
        payload: dict[str, object] = {
            "text": text,
            "model_id": self._settings.elevenlabs_model,
        }
        if language and self._settings.elevenlabs_model != "eleven_multilingual_v2":
            payload["language_code"] = language

        headers = {
            "xi-api-key": self._settings.elevenlabs_api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg",
        }

        logger.info(
            "ElevenLabs TTS role=%s voice=%s chars=%d",
            role.value,
            voice_id,
            len(text),
        )

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            audio_bytes = response.content

        if not audio_bytes:
            raise RuntimeError("ElevenLabs returned empty audio")

        audio_id = audio_cache.put(audio_bytes, mime_type="audio/mpeg")
        return SynthesizedSpeech(audio_id=audio_id, mime_type="audio/mpeg")


# Backward compatibility alias
ElevenLabsTTSService = TTSService
