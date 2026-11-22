"""Typed application configuration.

Every setting is optional: TamilGPT runs fully offline with zero credentials.
Provider credentials only switch on an optional LLM upgrade layer.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["development", "test", "production"]
Provider = Literal["offline", "openai", "gemini", "ollama"]


class Settings(BaseSettings):
    """Runtime settings, loaded from ``TAMILGPT_*`` environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="TAMILGPT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    env: Environment = "development"
    version: str = "2.0.0"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    app_name: str = "TamilGPT 2.0"
    api_key: str | None = None
    enable_docs: bool = True
    max_body_bytes: int = Field(default=64_000, ge=1_000, le=5_000_000)

    llm_provider: Provider = "offline"
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-1.5-flash"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    rate_limit_per_minute: int = Field(default=60, ge=1, le=10_000)
    max_question_chars: int = Field(default=1200, ge=32, le=20_000)
    max_history_turns: int = Field(default=8, ge=0, le=50)
    allowed_origins: str = "*"
    request_timeout_seconds: float = Field(default=30.0, gt=0, le=120)

    @field_validator("log_level")
    @classmethod
    def _upper_log_level(cls, value: str) -> str:
        return value.upper()

    @property
    def allowed_origins_list(self) -> list[str]:
        raw = self.allowed_origins.strip()
        if raw == "*":
            return ["*"]
        return [origin.strip() for origin in raw.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.env == "production"

    @property
    def llm_enabled(self) -> bool:
        """True when a provider is selected *and* its credentials are present."""
        if self.llm_provider == "offline":
            return False
        if self.llm_provider == "openai":
            return bool(self.openai_api_key)
        if self.llm_provider == "gemini":
            return bool(self.gemini_api_key)
        if self.llm_provider == "ollama":
            return bool(self.ollama_base_url)
        return False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide settings singleton."""
    return Settings()


def reset_settings_cache() -> None:
    """Clear the settings cache (used by tests and the CLI)."""
    get_settings.cache_clear()
