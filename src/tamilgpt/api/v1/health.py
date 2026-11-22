"""Health information endpoints. These never diagnose."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter

from tamilgpt.api.schemas import HealthTriageRequest
from tamilgpt.api.serializers import health_topic_to_dict
from tamilgpt.services.health import health_topics, triage

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/topics", summary="List health topics")
def topics(language: Literal["ta", "en"] = "ta") -> list[dict[str, object]]:
    return [health_topic_to_dict(topic, language) for topic in health_topics()]


@router.post("/triage", summary="Non-diagnostic symptom guidance")
def triage_symptoms(payload: HealthTriageRequest) -> dict[str, object]:
    result = triage(payload.text, language=payload.language)
    return result.to_dict(payload.language)
