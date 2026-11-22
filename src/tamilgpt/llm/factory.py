"""Select an LLM provider from settings, or ``None`` for offline mode."""

from __future__ import annotations

from functools import lru_cache

from tamilgpt.core.config import Settings, get_settings
from tamilgpt.llm.base import LLMProvider
from tamilgpt.llm.gemini_provider import GeminiProvider
from tamilgpt.llm.ollama_provider import OllamaProvider
from tamilgpt.llm.openai_provider import OpenAIProvider


def build_provider(settings: Settings) -> LLMProvider | None:
    if not settings.llm_enabled:
        return None
    timeout = settings.request_timeout_seconds
    if settings.llm_provider == "openai" and settings.openai_api_key:
        return OpenAIProvider(
            settings.openai_api_key,
            base_url=settings.openai_base_url,
            model=settings.openai_model,
            timeout=timeout,
        )
    if settings.llm_provider == "gemini" and settings.gemini_api_key:
        return GeminiProvider(
            settings.gemini_api_key, model=settings.gemini_model, timeout=timeout
        )
    if settings.llm_provider == "ollama":
        return OllamaProvider(
            settings.ollama_base_url, model=settings.ollama_model, timeout=timeout
        )
    return None


@lru_cache(maxsize=1)
def get_llm_provider() -> LLMProvider | None:
    return build_provider(get_settings())


def reset_llm_provider() -> None:
    get_llm_provider.cache_clear()
