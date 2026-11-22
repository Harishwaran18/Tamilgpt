"""Conversational endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Request

from tamilgpt.api.schemas import ChatRequest, ChatResponse
from tamilgpt.services import chat as chat_service
from tamilgpt.services.metrics import METRICS

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse, summary="Ask TamilGPT a question")
async def chat(payload: ChatRequest, request: Request) -> ChatResponse:
    profile_data = payload.profile.model_dump() if payload.profile else None
    result = await chat_service.answer(
        payload.message,
        language=payload.language,
        history=[message.model_dump() for message in payload.history],
        profile_data=profile_data,
    )
    METRICS.inc(f"chat_sector_{result.intent.get('sector', 'unknown')}")
    if result.crisis:
        METRICS.inc("chat_crisis_total")
    return ChatResponse(
        **result.to_dict(),
        request_id=getattr(request.state, "request_id", None),
    )
