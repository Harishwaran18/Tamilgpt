"""BM25 retrieval over bilingual records with Tamil romanisation expansion.

Every record is indexed twice: once in its original script and once romanised.
That lets ``kalvi kadan`` match Tamil documents about education loans without a
translation model, while keeping scoring explainable and dependency-free.
"""

from __future__ import annotations

import math
from bisect import bisect_left
from collections import Counter, defaultdict
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from tamilgpt.nlp.normalize import normalize_for_match
from tamilgpt.nlp.tokenize import STOPWORDS, ngrams, stem, tokenize
from tamilgpt.nlp.transliterate import phonetic_key, romanize, skeleton_key

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class SearchHit(Generic[T]):
    item: T
    score: float
    matched_terms: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {"score": round(self.score, 4), "matched_terms": list(self.matched_terms)}


def index_tokens(text: str) -> list[str]:
    """Tokens used for both documents and queries, with phonetic variants."""
    tokens: list[str] = []
    for token in tokenize(text) + tokenize(romanize(text)):
        if token in STOPWORDS or len(token) == 1:
            continue
        root = stem(token)
        tokens.append(root)
        if root.isascii() and len(root) >= 3:
            tokens.append(phonetic_key(root))
            skeleton = skeleton_key(root)
            if skeleton and len(skeleton) >= 4:
                tokens.append(skeleton)
    return tokens


class BM25Index(Generic[T]):
    """Okapi BM25 with title and phrase boosts."""

    def __init__(
        self,
        items: Iterable[T],
        text_getter: Callable[[T], str],
        *,
        title_getter: Callable[[T], str] | None = None,
        k1: float = 1.5,
        b: float = 0.75,
    ) -> None:
        self._items: list[T] = list(items)
        self._k1 = k1
        self._b = b
        self._term_freqs: list[Counter[str]] = []
        self._doc_lens: list[int] = []
        self._postings: dict[str, list[tuple[int, int]]] = defaultdict(list)
        self._normalized_texts: list[str] = []
        self._title_tokens: list[set[str]] = []

        for idx, item in enumerate(self._items):
            tokens = index_tokens(text_getter(item))
            freqs = Counter(tokens)
            self._term_freqs.append(freqs)
            self._doc_lens.append(len(tokens))
            self._normalized_texts.append(normalize_for_match(text_getter(item)))
            title = title_getter(item) if title_getter else ""
            self._title_tokens.append(set(index_tokens(title)))
            for term, count in freqs.items():
                self._postings[term].append((idx, count))

        self._avgdl = (sum(self._doc_lens) / len(self._doc_lens)) if self._doc_lens else 0.0
        self._n = len(self._items)
        self._terms = tuple(sorted(self._postings))

    def _prefix_matches(self, term: str, limit: int = 8) -> tuple[str, ...]:
        """Recover inflected forms such as ``kalvik`` from a query term ``kalvi``."""
        if len(term) < 4:
            return ()
        start = bisect_left(self._terms, term)
        matches: list[str] = []
        for candidate in self._terms[start:]:
            if not candidate.startswith(term):
                break
            matches.append(candidate)
            if len(matches) >= limit:
                break
        return tuple(matches)

    def __len__(self) -> int:
        return self._n

    def _idf(self, term: str) -> float:
        df = len(self._postings.get(term, ()))
        if df == 0:
            return 0.0
        return math.log(1 + (self._n - df + 0.5) / (df + 0.5))

    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        filter_fn: Callable[[T], bool] | None = None,
        min_score: float = 0.0,
    ) -> list[SearchHit[T]]:
        query_tokens = index_tokens(query)
        if not query_tokens or not self._items:
            return []

        scores: dict[int, float] = defaultdict(float)
        matched: dict[int, set[str]] = defaultdict(set)

        expanded_seen: set[str] = set()
        for term in set(query_tokens):
            candidates: tuple[str, ...] = (term, *self._prefix_matches(term, limit=4))
            for candidate in candidates:
                if candidate not in self._postings:
                    continue
                if candidate in expanded_seen:
                    continue
                expanded_seen.add(candidate)
                postings = self._postings[candidate]
                idf = self._idf(candidate)
                for idx, tf in postings:
                    doc_len = self._doc_lens[idx] or 1
                    denominator = tf + self._k1 * (
                        1 - self._b + self._b * doc_len / (self._avgdl or 1)
                    )
                    scores[idx] += idf * (tf * (self._k1 + 1)) / denominator
                    matched[idx].add(candidate)

        normalized_query = normalize_for_match(query)
        raw_query_tokens = tokenize(normalized_query)
        for idx in list(scores):
            title_hits = len(set(query_tokens) & self._title_tokens[idx])
            scores[idx] += 0.35 * title_hits
            if len(raw_query_tokens) >= 2:
                for gram in ngrams(raw_query_tokens, 2):
                    phrase = " ".join(gram)
                    if phrase in self._normalized_texts[idx]:
                        scores[idx] += 1.25
                for gram in ngrams(raw_query_tokens, 3):
                    phrase = " ".join(gram)
                    if phrase in self._normalized_texts[idx]:
                        scores[idx] += 1.75

        hits: list[SearchHit[T]] = []
        for idx, score in scores.items():
            item = self._items[idx]
            if filter_fn is not None and not filter_fn(item):
                continue
            if score < min_score:
                continue
            hits.append(
                SearchHit(
                    item=item,
                    score=score,
                    matched_terms=tuple(sorted(matched[idx])),
                )
            )
        hits.sort(key=lambda hit: hit.score, reverse=True)
        return hits[:top_k]
