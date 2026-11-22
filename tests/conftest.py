from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from tamilgpt.api.main import create_app
from tamilgpt.core.config import Settings
from tamilgpt.knowledge import get_knowledge_base, reset_knowledge_base
from tamilgpt.services.feedback import FEEDBACK
from tamilgpt.services.metrics import METRICS


@pytest.fixture(scope="session")
def client() -> TestClient:
    settings = Settings(rate_limit_per_minute=10_000, enable_docs=True)
    with TestClient(create_app(settings)) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def kb():
    reset_knowledge_base()
    return get_knowledge_base()


@pytest.fixture(autouse=True)
def _clean_state():
    METRICS.counters.clear()
    METRICS.durations_ms.clear()
    FEEDBACK.clear()
    yield
    FEEDBACK.clear()
