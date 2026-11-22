"""Sector catalogue used by the UI."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter

from tamilgpt.sectors import SECTORS, Sector

router = APIRouter(prefix="/sectors", tags=["sectors"])


@router.get("", summary="List the ten citizen-support sectors")
def sectors(language: Literal["ta", "en"] = "ta") -> list[dict[str, object]]:
    items: list[dict[str, object]] = []
    for sector, info in SECTORS.items():
        if sector is Sector.GENERAL:
            continue
        items.append(
            {
                "id": sector.value,
                "name": info.ta if language == "ta" else info.en,
                "name_ta": info.ta,
                "name_en": info.en,
                "icon": info.icon,
                "summary": info.summary_ta if language == "ta" else info.summary_en,
                "questions": list(info.questions_ta if language == "ta" else info.questions_en),
            }
        )
    return items
