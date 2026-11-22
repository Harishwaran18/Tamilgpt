"""Provider protocol shared by OpenAI, Gemini and Ollama adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class LLMMessage:
    role: str
    content: str


@runtime_checkable
class LLMProvider(Protocol):
    name: str

    async def complete(
        self,
        system: str,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.2,
        max_tokens: int = 700,
    ) -> str: ...
