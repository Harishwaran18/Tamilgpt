"""Nearby public services via OpenStreetMap."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Query

from tamilgpt.services.nearby import find_nearby

router = APIRouter(prefix="/nearby", tags=["nearby"])


@router.get("", summary="Find nearby hospitals, police stations and offices")
async def nearby(
    lat: float = Query(ge=-90, le=90),
    lon: float = Query(ge=-180, le=180),
    type: str = Query(min_length=2, max_length=40),
    radius: int = Query(default=3000, ge=100, le=10000),
    language: Literal["ta", "en"] = "ta",
) -> dict[str, object]:
    result = await find_nearby(lat, lon, type, radius_m=radius)
    return result.to_dict(language)
