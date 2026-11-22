"""Answer feedback endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from tamilgpt.api.schemas import FeedbackRequest
from tamilgpt.services.feedback import FEEDBACK

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", summary="Rate an answer")
def submit(payload: FeedbackRequest) -> dict[str, object]:
    record = FEEDBACK.add(
        rating=payload.rating,
        comment=payload.comment,
        sector=payload.sector,
        language=payload.language,
        message_id=payload.message_id,
    )
    return {"ok": True, "record": record, "summary": FEEDBACK.summary()}


@router.get("/summary", summary="Aggregate feedback")
def summary() -> dict[str, object]:
    return FEEDBACK.summary()
