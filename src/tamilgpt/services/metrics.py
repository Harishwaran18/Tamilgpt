"""Process-local metrics for health checks and lightweight dashboards."""

from __future__ import annotations

import threading
from collections import Counter
from dataclasses import dataclass, field


@dataclass(slots=True)
class Metrics:
    counters: Counter[str] = field(default_factory=Counter)
    durations_ms: dict[str, list[float]] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def inc(self, name: str, value: int = 1) -> None:
        with self._lock:
            self.counters[name] += value

    def observe(self, name: str, duration_ms: float) -> None:
        with self._lock:
            series = self.durations_ms.setdefault(name, [])
            series.append(round(duration_ms, 2))
            if len(series) > 500:
                del series[:250]

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            summary = {}
            for name, series in self.durations_ms.items():
                if not series:
                    continue
                ordered = sorted(series)
                summary[name] = {
                    "count": len(series),
                    "avg_ms": round(sum(series) / len(series), 2),
                    "p95_ms": ordered[int(len(ordered) * 0.95) - 1],
                    "max_ms": ordered[-1],
                }
            return {"counters": dict(self.counters), "latency": summary}


METRICS = Metrics()
