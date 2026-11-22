"""Runtime metadata and knowledge-base statistics."""

from __future__ import annotations

from fastapi import APIRouter

from tamilgpt.core.config import get_settings
from tamilgpt.knowledge import get_knowledge_base
from tamilgpt.llm import get_llm_provider

router = APIRouter(tags=["meta"])


@router.get("/meta", summary="Version, provider and knowledge statistics")
def meta() -> dict[str, object]:
    settings = get_settings()
    stats = get_knowledge_base().stats()
    provider = get_llm_provider()
    return {
        "name": "TamilGPT 2.0",
        "version": settings.version,
        "languages": ["ta", "en", "tanglish"],
        "llm_provider": getattr(provider, "name", "offline"),
        "knowledge": {
            "documents": stats.documents,
            "schemes": stats.schemes,
            "careers": stats.careers,
            "health_topics": stats.health_topics,
            "services": stats.services,
            "helplines": stats.helplines,
            "sectors": list(stats.sectors),
        },
    }
