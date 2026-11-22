"""Bounded in-memory feedback store.

The store is intentionally small and dependency-free. Production deployments
should forward these records to their analytics pipeline; the interface stays
the same.
"""

from __future__ import annotations

import threading
from collections import Counter, deque
from datetime import UTC, datetime
from typing import Any

from tamilgpt.services.safety import redact_pii

_MAX_ITEMS = 500


class FeedbackStore:
    def __init__(self, max_items: int = _MAX_ITEMS) -> None:
        self._items: deque[dict[str, Any]] = deque(maxlen=max_items)
        self._lock = threading.Lock()

    def add(
        self,
        *,
        rating: int,
        comment: str | None = None,
        sector: str | None = None,
        language: str | None = None,
        message_id: str | None = None,
    ) -> dict[str, Any]:
        record = {
            "rating": rating,
            "comment": redact_pii(comment) if comment else None,
            "sector": sector,
            "language": language,
            "message_id": message_id,
            "created_at": datetime.now(UTC).isoformat(),
        }
        with self._lock:
            self._items.append(record)
        return record

    def summary(self) -> dict[str, Any]:
        with self._lock:
            items = list(self._items)
        ratings = [item["rating"] for item in items]
        distribution = Counter(ratings)
        return {
            "count": len(items),
            "average": round(sum(ratings) / len(ratings), 2) if ratings else None,
            "distribution": {str(score): distribution.get(score, 0) for score in range(1, 6)},
        }

    def clear(self) -> None:
        with self._lock:
            self._items.clear()


FEEDBACK = FeedbackStore()
