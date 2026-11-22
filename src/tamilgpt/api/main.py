"""FastAPI application factory."""

from __future__ import annotations

import time
import uuid
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from tamilgpt.api.v1 import api_router
from tamilgpt.core.config import Settings, get_settings
from tamilgpt.core.errors import TamilGPTError
from tamilgpt.core.logging import configure_logging, get_logger, request_id_var
from tamilgpt.core.ratelimit import SlidingWindowLimiter
from tamilgpt.knowledge import get_knowledge_base
from tamilgpt.services.metrics import METRICS

logger = get_logger("tamilgpt.api")
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

_PUBLIC_PREFIXES = ("/healthz", "/readyz", "/static", "/docs", "/redoc", "/openapi.json", "/")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level, json_output=settings.is_production)
    kb = get_knowledge_base()
    stats = kb.stats()
    logger.info(
        "startup",
        extra={
            "version": settings.version,
            "documents": stats.documents,
            "schemes": stats.schemes,
            "env": settings.env,
        },
    )
    yield
    logger.info("shutdown")


def _client_key(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _is_public(path: str) -> bool:
    if path == "/api/v1/meta":
        return True
    return any(path == prefix or path.startswith(prefix + "/") for prefix in _PUBLIC_PREFIXES)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    docs_enabled = settings.enable_docs
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description=(
            "Tamil-first guidance API for schemes, careers, finance, health, legal aid, "
            "agriculture and wellness. Offline-first with an optional LLM upgrade."
        ),
        lifespan=lifespan,
        docs_url="/docs" if docs_enabled else None,
        redoc_url="/redoc" if docs_enabled else None,
        openapi_url="/openapi.json" if docs_enabled else None,
    )
    limiter = SlidingWindowLimiter(settings.rate_limit_per_minute)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "X-API-Key", "Authorization", "X-Request-ID"],
        expose_headers=["X-Request-ID", "X-RateLimit-Remaining"],
    )

    @app.middleware("http")
    async def guard(request: Request, call_next):  # type: ignore[no-untyped-def]
        request_id = request.headers.get("X-Request-ID", "")
        if not request_id or len(request_id) > 64 or not request_id.replace("-", "").isalnum():
            request_id = uuid.uuid4().hex
        request.state.request_id = request_id
        token = request_id_var.set(request_id)
        started = time.perf_counter()
        path = request.url.path

        try:
            content_length = int(request.headers.get("content-length") or 0)
            if content_length > settings.max_body_bytes:
                return JSONResponse(
                    status_code=413,
                    content={"error": {"code": "payload_too_large", "message": "Request body is too large."}},
                    headers={"X-Request-ID": request_id},
                )

            if path.startswith("/api/") and not _is_public(path):
                if settings.api_key:
                    supplied = request.headers.get("X-API-Key") or ""
                    if not supplied:
                        auth = request.headers.get("Authorization", "")
                        supplied = auth.removeprefix("Bearer ").strip()
                    if supplied != settings.api_key:
                        return JSONResponse(
                            status_code=401,
                            content={"error": {"code": "unauthorized", "message": "A valid API key is required."}},
                            headers={"X-Request-ID": request_id},
                        )

                key = _client_key(request)
                if not limiter.allow(key):
                    return JSONResponse(
                        status_code=429,
                        content={"error": {"code": "rate_limited", "message": "Too many requests."}},
                        headers={
                            "X-Request-ID": request_id,
                            "Retry-After": str(limiter.retry_after(key)),
                        },
                    )

            response = await call_next(request)
        finally:
            request_id_var.reset(token)

        elapsed_ms = (time.perf_counter() - started) * 1000
        route = request.scope.get("route")
        label = getattr(route, "path", path)
        METRICS.inc("http_requests_total")
        METRICS.inc(f"http_status_{response.status_code}")
        METRICS.observe(f"http_latency:{label}", elapsed_ms)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=(self)"
        if not path.startswith("/docs") and not path.startswith("/redoc"):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; connect-src 'self' https:; font-src 'self'; "
                "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
            )
        return response

    @app.exception_handler(TamilGPTError)
    async def domain_error(request: Request, exc: TamilGPTError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_dict(),
            headers={"X-Request-ID": getattr(request.state, "request_id", "-")},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "validation_failed",
                    "message": "Request validation failed.",
                    "details": jsonable_encoder(exc.errors()),
                }
            },
            headers={"X-Request-ID": getattr(request.state, "request_id", "-")},
        )

    @app.exception_handler(Exception)
    async def unhandled_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_error", extra={"path": request.url.path})
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "internal_error",
                    "message": "Something went wrong. Please try again.",
                    "request_id": getattr(request.state, "request_id", None),
                }
            },
            headers={"X-Request-ID": getattr(request.state, "request_id", "-")},
        )

    app.include_router(api_router)

    @app.get("/healthz", tags=["ops"], summary="Liveness probe")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz", tags=["ops"], summary="Readiness probe")
    def readyz() -> JSONResponse:
        stats = get_knowledge_base().stats()
        ready = stats.documents > 0 and stats.schemes > 0
        return JSONResponse(
            status_code=200 if ready else 503,
            content={"status": "ready" if ready else "not_ready", "documents": stats.documents},
        )

    if STATIC_DIR.is_dir():
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
        index = STATIC_DIR / "index.html"

        @app.get("/", include_in_schema=False)
        def index_page() -> FileResponse:
            return FileResponse(index)

    return app


app = create_app()
