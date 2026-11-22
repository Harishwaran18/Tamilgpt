"""Career discovery and matching endpoints."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Query

from tamilgpt.api.schemas import CareerMatchRequest
from tamilgpt.api.serializers import career_to_dict
from tamilgpt.services.careers import find_careers, match_careers
from tamilgpt.services.profile import Profile

router = APIRouter(prefix="/careers", tags=["careers"])


@router.get("", summary="List or search careers")
def list_careers(
    q: str = Query(default="", max_length=200),
    limit: int = Query(default=30, ge=1, le=100),
    language: Literal["ta", "en"] = "ta",
) -> list[dict[str, object]]:
    return [career_to_dict(career, language) for career in find_careers(q, limit=limit)]


@router.post("/match", summary="Match careers to interests and education")
def match(payload: CareerMatchRequest, language: Literal["ta", "en"] = "ta") -> list[dict[str, object]]:
    profile = Profile.from_mapping(payload.model_dump(exclude={"limit"}))
    return [match.to_dict(language) for match in match_careers(profile, limit=payload.limit)]
