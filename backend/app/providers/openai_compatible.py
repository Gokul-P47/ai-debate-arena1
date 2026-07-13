"""Shared OpenAI-compatible chat completions provider."""

from typing import AsyncIterator

from openai import AsyncOpenAI

from app.providers.base_provider import BaseProvider
from app.utils.logger import get_logger

logger = get_logger(__name__)


class OpenAICompatibleProvider(BaseProvider):
    """LLM provider using the OpenAI Chat Completions API shape.

    Works with OpenAI and OpenAI-compatible endpoints (e.g. xAI Grok).
    """

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        provider_name: str,
        base_url: str | None = None,
    ) -> None:
        if not api_key:
            raise ValueError(
                f"{provider_name} API key is missing. "
                f"Set the corresponding key in backend/.env for LLM_PROVIDER={provider_name}."
            )

        self._model = model
        self._provider_name = provider_name
        client_kwargs: dict[str, str] = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        self._client = AsyncOpenAI(**client_kwargs)
        logger.info(
            "%s provider initialized with model: %s",
            provider_name,
            model,
        )

    async def generate(self, prompt: str, system_prompt: str) -> str:
        """Generate a text completion via chat.completions."""
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        )
        content = response.choices[0].message.content
        return content or ""

    async def generate_stream(self, prompt: str, system_prompt: str) -> AsyncIterator[str]:
        """Stream a text completion via chat.completions."""
        stream = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
