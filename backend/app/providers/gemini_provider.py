"""Google Gemini LLM provider implementation."""

from typing import AsyncIterator

from google import genai
from google.genai import types

from app.core.config import Settings, get_settings
from app.providers.base_provider import BaseProvider
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GeminiProvider(BaseProvider):
    """Gemini-backed language model provider."""

    def __init__(self, settings: Settings | None = None) -> None:
        settings = settings or get_settings()
        if not settings.gemini_api_key:
            raise ValueError(
                "gemini API key is missing. "
                "Set GEMINI_API_KEY in backend/.env for LLM_PROVIDER=gemini."
            )

        self._model = settings.gemini_model
        self._client = genai.Client(api_key=settings.gemini_api_key)
        logger.info("gemini provider initialized with model: %s", self._model)

    async def generate(self, prompt: str, system_prompt: str) -> str:
        """Generate a text completion using the Gemini API."""
        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=system_prompt),
        )
        return response.text or ""

    async def generate_stream(self, prompt: str, system_prompt: str) -> AsyncIterator[str]:
        """Stream a text completion using the Gemini API."""
        stream = await self._client.aio.models.generate_content_stream(
            model=self._model,
            contents=prompt,
            config=types.GenerateContentConfig(system_instruction=system_prompt),
        )
        async for chunk in stream:
            if chunk.text:
                yield chunk.text
