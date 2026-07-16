import asyncio
import re
from typing import AsyncIterator

from google import genai
from google.genai import types

from app.core.config import Settings, get_settings
from app.providers.base_provider import BaseProvider
from app.utils.logger import get_logger

logger = get_logger(__name__)


def extract_retry_delay(error_msg: str) -> float | None:
    """Extract retry delay in seconds from the Gemini API error message."""
    # Match "Please retry in 44.42186453s" or "Please retry in 44s"
    match = re.search(r"Please retry in\s+(\d+\.?\d*)s", error_msg)
    if match:
        return float(match.group(1))

    # Match detail entry: "retryDelay': '44s'"
    match_detail = re.search(r"retryDelay':\s*['\"](\d+\.?\d*)s['\"]", error_msg)
    if match_detail:
        return float(match_detail.group(1))

    return None


class GeminiProvider(BaseProvider):
    """Gemini-backed language model provider with quota retry support."""

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
        """Generate a text completion using the Gemini API, retrying on rate limits."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = await self._client.aio.models.generate_content(
                    model=self._model,
                    contents=prompt,
                    config=types.GenerateContentConfig(system_instruction=system_prompt),
                )
                return response.text or ""
            except Exception as exc:
                err_msg = str(exc)
                if (
                    "RESOURCE_EXHAUSTED" in err_msg
                    or "Quota exceeded" in err_msg
                    or "429" in err_msg
                ):
                    delay = extract_retry_delay(err_msg)
                    if delay and attempt < max_retries - 1:
                        logger.warning(
                            "Gemini rate limit hit. Waiting %f seconds before retry (attempt %d/%d)...",
                            delay + 1.0,
                            attempt + 1,
                            max_retries,
                        )
                        await asyncio.sleep(delay + 1.0)
                        continue
                raise

    async def generate_stream(self, prompt: str, system_prompt: str) -> AsyncIterator[str]:
        """Stream a text completion using the Gemini API, retrying on rate limits."""
        max_retries = 3
        stream = None

        for attempt in range(max_retries):
            try:
                stream = await self._client.aio.models.generate_content_stream(
                    model=self._model,
                    contents=prompt,
                    config=types.GenerateContentConfig(system_instruction=system_prompt),
                )
                break
            except Exception as exc:
                err_msg = str(exc)
                if (
                    "RESOURCE_EXHAUSTED" in err_msg
                    or "Quota exceeded" in err_msg
                    or "429" in err_msg
                ):
                    delay = extract_retry_delay(err_msg)
                    if delay and attempt < max_retries - 1:
                        logger.warning(
                            "Gemini rate limit hit on stream. Waiting %f seconds before retry (attempt %d/%d)...",
                            delay + 1.0,
                            attempt + 1,
                            max_retries,
                        )
                        await asyncio.sleep(delay + 1.0)
                        continue
                raise

        if stream is not None:
            async for chunk in stream:
                if chunk.text:
                    yield chunk.text
