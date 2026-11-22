from __future__ import annotations

import json
import logging

import pytest

from tamilgpt import __version__
from tamilgpt.__main__ import _chat_once, _repl, main
from tamilgpt.core.config import Settings, get_settings, reset_settings_cache
from tamilgpt.core.errors import (
    NotFoundError,
    ProviderUnavailable,
    RateLimited,
    SafetyBlocked,
    TamilGPTError,
    ValidationFailed,
)
from tamilgpt.core.logging import (
    HumanFormatter,
    JsonFormatter,
    configure_logging,
    get_logger,
    request_id_var,
)
from tamilgpt.core.ratelimit import SlidingWindowLimiter
from tamilgpt.llm.base import LLMMessage, LLMProvider
from tamilgpt.llm.factory import build_provider, get_llm_provider, reset_llm_provider
from tamilgpt.llm.gemini_provider import GeminiProvider
from tamilgpt.llm.ollama_provider import OllamaProvider
from tamilgpt.llm.openai_provider import OpenAIProvider


def test_settings_defaults(monkeypatch) -> None:
    reset_settings_cache()
    settings = Settings(_env_file=None)
    assert settings.version == "2.0.0"
    assert settings.port == 8000
    assert settings.log_level == "INFO"
    assert settings.allowed_origins_list == ["*"]
    assert settings.is_production is False
    assert settings.llm_enabled is False

    monkeypatch.setenv("TAMILGPT_PORT", "9000")
    monkeypatch.setenv("TAMILGPT_LOG_LEVEL", "debug")
    monkeypatch.setenv("TAMILGPT_ALLOWED_ORIGINS", "https://a.example, https://b.example")
    configured = Settings(_env_file=None)
    assert configured.port == 9000
    assert configured.log_level == "DEBUG"
    assert configured.allowed_origins_list == ["https://a.example", "https://b.example"]

    reset_settings_cache()
    assert get_settings().app_name == "TamilGPT 2.0"
    assert __version__ == "2.0.0"


def test_llm_enabled_rules() -> None:
    assert Settings(_env_file=None, llm_provider="openai", openai_api_key="key").llm_enabled
    assert not Settings(_env_file=None, llm_provider="openai").llm_enabled
    assert Settings(_env_file=None, llm_provider="gemini", gemini_api_key="key").llm_enabled
    assert not Settings(_env_file=None, llm_provider="gemini").llm_enabled
    assert Settings(_env_file=None, llm_provider="ollama").llm_enabled
    assert Settings(_env_file=None, env="production").is_production


def test_error_hierarchy() -> None:
    cases = [
        (ValidationFailed("bad"), "validation_failed", 422),
        (NotFoundError("missing"), "not_found", 404),
        (RateLimited("slow"), "rate_limited", 429),
        (ProviderUnavailable("down"), "provider_unavailable", 503),
        (SafetyBlocked("blocked"), "safety_blocked", 400),
        (TamilGPTError("boom"), "internal_error", 500),
    ]
    for error, code, status in cases:
        assert error.code == code
        assert error.status_code == status
        assert error.to_dict()["error"]["code"] == code
        assert error.to_dict()["error"]["message"]

    detailed = ValidationFailed("bad", details={"field": "age"})
    assert detailed.to_dict()["error"]["details"] == {"field": "age"}


def test_json_formatter() -> None:
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello %s",
        args=("world",),
        exc_info=None,
    )
    token = request_id_var.set("rid-1")
    try:
        payload = json.loads(formatter.format(record))
    finally:
        request_id_var.reset(token)
    assert payload["message"] == "hello world"
    assert payload["level"] == "INFO"
    assert payload["request_id"] == "rid-1"

    error_record = logging.LogRecord(
        name="test",
        level=logging.ERROR,
        pathname=__file__,
        lineno=1,
        msg="failed",
        args=(),
        exc_info=None,
    )
    error_record.custom = "value"
    payload = json.loads(formatter.format(error_record))
    assert payload["custom"] == "value"

    human = HumanFormatter("%(levelname)s %(message)s")
    token = request_id_var.set("rid-2")
    try:
        assert "[rid=rid-2]" in human.format(record)
    finally:
        request_id_var.reset(token)


def test_configure_logging() -> None:
    configure_logging("DEBUG", json_output=True)
    assert logging.getLogger().level == logging.DEBUG
    configure_logging("INFO", json_output=False)
    assert logging.getLogger().level == logging.INFO
    assert get_logger("x").name == "x"


def test_rate_limiter() -> None:
    limiter = SlidingWindowLimiter(limit=2, window_seconds=60)
    assert limiter.allow("user")
    assert limiter.allow("user")
    assert not limiter.allow("user")
    assert limiter.retry_after("user") >= 1
    assert limiter.retry_after("other") == 0
    assert limiter.allow("other")

    with pytest.raises(ValueError):
        SlidingWindowLimiter(limit=0)


def test_llm_factory() -> None:
    assert build_provider(Settings(_env_file=None)) is None
    openai = build_provider(
        Settings(_env_file=None, llm_provider="openai", openai_api_key="key")
    )
    assert isinstance(openai, OpenAIProvider)
    assert openai.name == "openai"
    assert isinstance(openai, LLMProvider)

    gemini = build_provider(
        Settings(_env_file=None, llm_provider="gemini", gemini_api_key="key")
    )
    assert isinstance(gemini, GeminiProvider)
    assert gemini.name == "gemini"

    ollama = build_provider(Settings(_env_file=None, llm_provider="ollama"))
    assert isinstance(ollama, OllamaProvider)
    assert ollama.name == "ollama"

    reset_llm_provider()
    assert get_llm_provider() is None


def test_llm_message() -> None:
    message = LLMMessage(role="user", content="hi")
    assert message.role == "user"
    assert message.content == "hi"


@pytest.mark.asyncio
async def test_chat_once(capsys) -> None:
    assert await _chat_once("hello", "en") == 0
    assert capsys.readouterr().out.strip()


def test_repl_exit(monkeypatch, capsys) -> None:
    monkeypatch.setattr("builtins.input", lambda prompt="": "exit")
    assert _repl("en") == 0
    assert "TamilGPT" in capsys.readouterr().out


def test_cli_validate_and_chat(capsys) -> None:
    assert main(["validate"]) == 0
    assert "Knowledge base OK" in capsys.readouterr().out
    assert main(["chat", "-m", "hello", "-l", "en"]) == 0
    assert capsys.readouterr().out.strip()

    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
