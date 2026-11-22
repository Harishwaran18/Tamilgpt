"""Domain errors with stable machine-readable codes."""

from __future__ import annotations

from typing import Any


class TamilGPTError(Exception):
    """Base class for all expected application errors."""

    code = "internal_error"
    status_code = 500

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        body: dict[str, Any] = {"error": {"code": self.code, "message": self.message}}
        if self.details:
            body["error"]["details"] = self.details
        return body


class ValidationFailed(TamilGPTError):
    code = "validation_failed"
    status_code = 422


class NotFoundError(TamilGPTError):
    code = "not_found"
    status_code = 404


class RateLimited(TamilGPTError):
    code = "rate_limited"
    status_code = 429


class ProviderUnavailable(TamilGPTError):
    code = "provider_unavailable"
    status_code = 503


class SafetyBlocked(TamilGPTError):
    code = "safety_blocked"
    status_code = 400
