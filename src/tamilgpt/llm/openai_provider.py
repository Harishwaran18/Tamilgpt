"""OpenAI-compatible chat completions (OpenAI, Azure, vLLM, Groq, LM Studio)."""

from __future__ import annotations

import httpx

from tamilgpt.core.errors import ProviderUnavailable
from tamilgpt.core.logging import get_logger
from tamilgpt.llm.base import LLMMessage

logger = get_logger(__name__)


class OpenAIProvider:
    name = "openai"

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-4o-mini",
        timeout: float = 30.0,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout

    async def complete(
        self,
        system: str,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int = 700,
    ) -> str:
        payload = {
            "model": self._model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [{"role": "system", "content": system}]
            + [{"role": message.role, "content": message.content} for message in messages],
        }
        headers = {"Authorization": f"Bearer {self._api_key}"}
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    f"{self._base_url}/chat/completions", json=payload, headers=headers
                )
                response.raise_for_status()
                data = response.json()
            return str(data["choices"][0]["message"]["content"]).strip()
        except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
            logger.warning("openai_completion_failed", extra={"error": str(exc)})
            raise ProviderUnavailable("LLM provider is unavailable") from exc
