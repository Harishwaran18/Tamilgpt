"""Official helpline directory."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Query

from tamilgpt.api.serializers import helpline_to_dict
from tamilgpt.knowledge import get_knowledge_base

router = APIRouter(prefix="/helplines", tags=["helplines"])


@router.get("", summary="List helplines by category")
def helplines(
    category: str | None = Query(default=None, max_length=40),
    language: Literal["ta", "en"] = "ta",
) -> list[dict[str, object]]:
    lines = get_knowledge_base().helplines_for(category)
    return [helpline_to_dict(line, language) for line in lines]
