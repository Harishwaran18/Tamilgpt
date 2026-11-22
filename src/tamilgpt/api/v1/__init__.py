"""API v1 router aggregation."""

from fastapi import APIRouter

from tamilgpt.api.v1.careers import router as careers_router
from tamilgpt.api.v1.chat import router as chat_router
from tamilgpt.api.v1.feedback import router as feedback_router
from tamilgpt.api.v1.finance import router as finance_router
from tamilgpt.api.v1.health import router as health_router
from tamilgpt.api.v1.helplines import router as helplines_router
from tamilgpt.api.v1.meta import router as meta_router
from tamilgpt.api.v1.metrics import router as metrics_router
from tamilgpt.api.v1.nearby import router as nearby_router
from tamilgpt.api.v1.schemes import router as schemes_router
from tamilgpt.api.v1.sectors import router as sectors_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(chat_router)
api_router.include_router(schemes_router)
api_router.include_router(careers_router)
api_router.include_router(finance_router)
api_router.include_router(health_router)
api_router.include_router(nearby_router)
api_router.include_router(helplines_router)
api_router.include_router(sectors_router)
api_router.include_router(meta_router)
api_router.include_router(feedback_router)
api_router.include_router(metrics_router)

__all__ = ["api_router"]
