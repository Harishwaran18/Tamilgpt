"""Weighted term matching shared by intent classification and retrieval.

The matcher understands four surface forms of the same idea: the literal word,
its stem, its Tamil→Latin romanisation, and its phonetic key. That is enough to
map ``kalvi``, ``கல்வி`` and ``கல்விக்கு`` onto the same concept without a model.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from tamilgpt.nlp.normalize import normalize_for_match
from tamilgpt.nlp.tokenize import stem, tokenize
from tamilgpt.nlp.transliterate import phonetic_key


@dataclass(slots=True)
class MatchResult:
    score: float = 0.0
    matched: list[str] = field(default_factory=list)

    @property
    def hit(self) -> bool:
        return bool(self.matched)


class TermMatcher:
    """Accumulates weighted terms and scores free text against them."""

    def __init__(self) -> None:
        self._phrases: dict[str, float] = {}
        self._words: dict[str, float] = {}
        self._stems: dict[str, float] = {}
        self._phonetic: dict[str, float] = {}
        self._display: dict[str, str] = {}

    def add(self, term: str, weight: float = 1.0) -> None:
        normalized = normalize_for_match(term)
        tokens = tokenize(normalized)
        if not tokens:
            return
        if len(tokens) > 1:
            if weight > self._phrases.get(normalized, 0.0):
                self._phrases[normalized] = weight
                self._display[normalized] = term
            return
        word = tokens[0]
        self._display.setdefault(word, term)
        if weight > self._words.get(word, 0.0):
            self._words[word] = weight
            self._stems[stem(word)] = max(weight, self._stems.get(stem(word), 0.0))
            if len(word) >= 3:
                self._phonetic[phonetic_key(word)] = max(
                    weight, self._phonetic.get(phonetic_key(word), 0.0)
                )

    def add_many(self, terms: tuple[str, ...] | list[str], weight: float = 1.0) -> None:
        for term in terms:
            self.add(term, weight)

    def __len__(self) -> int:
        return len(self._phrases) + len(self._words)

    def match(self, text: str) -> MatchResult:
        normalized = normalize_for_match(text)
        if not normalized:
            return MatchResult()

        tokens = set(tokenize(normalized))
        stems = {stem(token) for token in tokens}
        phonetics = {phonetic_key(token) for token in tokens}
        matched: list[str] = []
        score = 0.0

        for phrase, weight in self._phrases.items():
            if phrase in normalized:
                score += weight
                matched.append(self._display.get(phrase, phrase))

        for word, weight in self._words.items():
            if word in tokens or stem(word) in stems or (
                len(word) >= 3 and phonetic_key(word) in phonetics
            ):
                score += weight
                matched.append(self._display.get(word, word))

        return MatchResult(score=score, matched=matched)
