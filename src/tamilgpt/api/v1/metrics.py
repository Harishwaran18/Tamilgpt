"""Lightweight metrics endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from tamilgpt.services.metrics import METRICS

router = APIRouter(tags=["metrics"])


@router.get("/metrics", summary="Process metrics")
def metrics() -> dict[str, object]:
    return METRICS.snapshot()
