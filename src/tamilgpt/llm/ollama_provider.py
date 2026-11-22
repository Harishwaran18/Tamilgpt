"""Local Ollama adapter for fully self-hosted deployments."""

from __future__ import annotations

import httpx

from tamilgpt.core.errors import ProviderUnavailable
from tamilgpt.core.logging import get_logger
from tamilgpt.llm.base import LLMMessage

logger = get_logger(__name__)


class OllamaProvider:
    name = "ollama"

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        *,
        model: str = "llama3.1",
        timeout: float = 60.0,
    ) -> None:
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
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
            "messages": [{"role": "system", "content": system}]
            + [{"role": message.role, "content": message.content} for message in messages],
        }
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(f"{self._base_url}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
            return str(data["message"]["content"]).strip()
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            logger.warning("ollama_completion_failed", extra={"error": str(exc)})
            raise ProviderUnavailable("LLM provider is unavailable") from exc
