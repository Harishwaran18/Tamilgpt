"""Small, dependency-free similarity primitives."""

from __future__ import annotations


def levenshtein(a: str, b: str, *, max_distance: int | None = None) -> int:
    """Edit distance with an optional early-exit bound."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    if len(a) < len(b):
        a, b = b, a
    if max_distance is not None and len(a) - len(b) > max_distance:
        return max_distance + 1

    previous = list(range(len(b) + 1))
    for i, char_a in enumerate(a, start=1):
        current = [i]
        row_min = i
        for j, char_b in enumerate(b, start=1):
            cost = 0 if char_a == char_b else 1
            value = min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + cost)
            current.append(value)
            row_min = min(row_min, value)
        if max_distance is not None and row_min > max_distance:
            return max_distance + 1
        previous = current
    return previous[-1]


def ratio(a: str, b: str) -> float:
    """Normalised similarity in ``[0, 1]``."""
    if not a and not b:
        return 1.0
    longest = max(len(a), len(b))
    return 1.0 - levenshtein(a, b) / longest


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def fuzzy_contains(haystack: str, needle: str, *, threshold: float = 0.82) -> bool:
    """True when ``needle`` appears in ``haystack`` allowing small typos."""
    if not needle:
        return False
    if needle in haystack:
        return True
    if len(needle) < 4:
        return False
    window = len(needle)
    for start in range(max(1, len(haystack) - window + 1)):
        if ratio(needle, haystack[start : start + window]) >= threshold:
            return True
    return False
