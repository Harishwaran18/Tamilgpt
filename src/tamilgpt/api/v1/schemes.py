"""Scheme discovery and eligibility endpoints."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from tamilgpt.api.schemas import SchemeMatchRequest
from tamilgpt.api.serializers import scheme_to_dict
from tamilgpt.knowledge import get_knowledge_base
from tamilgpt.services.profile import Profile
from tamilgpt.services.schemes import find_schemes, match_schemes

router = APIRouter(prefix="/schemes", tags=["schemes"])


@router.get("", summary="List or search schemes")
def list_schemes(
    q: str = Query(default="", max_length=200),
    category: str | None = Query(default=None, max_length=40),
    limit: int = Query(default=30, ge=1, le=100),
    language: Literal["ta", "en"] = "ta",
) -> list[dict[str, object]]:
    schemes = find_schemes(q, category=category, limit=limit)
    return [scheme_to_dict(scheme, language) for scheme in schemes]


@router.post("/match", summary="Rank schemes for a citizen profile")
def match(payload: SchemeMatchRequest, language: Literal["ta", "en"] = "ta") -> list[dict[str, object]]:
    profile = Profile.from_mapping(payload.model_dump(exclude={"query", "limit", "eligible_only"}))
    matches = match_schemes(
        profile,
        limit=payload.limit,
        eligible_only=payload.eligible_only,
    )
    return [match.to_dict(language) for match in matches]


@router.get("/{scheme_id}", summary="Get one scheme")
def get_scheme(scheme_id: str, language: Literal["ta", "en"] = "ta") -> dict[str, object]:
    scheme = get_knowledge_base().scheme_by_id(scheme_id)
    if scheme is None:
        raise HTTPException(status_code=404, detail="scheme not found")
    return scheme_to_dict(scheme, language)
