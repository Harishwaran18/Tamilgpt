"""Google Gemini generateContent adapter."""

from __future__ import annotations

import httpx

from tamilgpt.core.errors import ProviderUnavailable
from tamilgpt.core.logging import get_logger
from tamilgpt.llm.base import LLMMessage

logger = get_logger(__name__)


class GeminiProvider:
    name = "gemini"

    def __init__(
        self,
        api_key: str,
        *,
        model: str = "gemini-1.5-flash",
        timeout: float = 30.0,
    ) -> None:
        self._api_key = api_key
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
        contents = [
            {
                "role": "model" if message.role == "assistant" else "user",
                "parts": [{"text": message.content}],
            }
            for message in messages
        ]
        payload = {
            "system_instruction": {"parts": [{"text": system}]},
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
            },
        }
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self._model}:generateContent"
        )
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(
                    url, params={"key": self._api_key}, json=payload
                )
                response.raise_for_status()
                data = response.json()
            parts = data["candidates"][0]["content"]["parts"]
            return "".join(part.get("text", "") for part in parts).strip()
        except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
            logger.warning("gemini_completion_failed", extra={"error": str(exc)})
            raise ProviderUnavailable("LLM provider is unavailable") from exc
