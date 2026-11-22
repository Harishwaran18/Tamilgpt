"""Deterministic sector + action intent classification.

Two independent classifiers run over the same text:

* **sector** — one of the ten citizen-support domains (agriculture, health, …)
* **action** — what the citizen wants to do (understand, check eligibility,
  calculate, find a nearby office, apply, gather documents, or just chat)

Both are lexicon-driven, so they work offline, are fully explainable, and run in
microseconds. A crisis screen runs first and always wins.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum
from functools import lru_cache

from tamilgpt.nlp.language import Language, detect_language
from tamilgpt.nlp.matching import TermMatcher
from tamilgpt.nlp.normalize import normalize_for_match
from tamilgpt.sectors import SECTORS, Sector, SectorInfo


class Action(StrEnum):
    INFORMATION = "information"
    ELIGIBILITY = "eligibility"
    CALCULATION = "calculation"
    NEARBY = "nearby"
    APPLY = "apply"
    DOCUMENTS = "documents"
    SMALL_TALK = "small_talk"
    CRISIS = "crisis"


@dataclass(frozen=True, slots=True)
class IntentResult:
    sector: Sector
    action: Action
    confidence: float
    sector_scores: dict[str, float] = field(default_factory=dict)
    action_scores: dict[str, float] = field(default_factory=dict)
    matched: tuple[str, ...] = ()
    crisis: bool = False
    language: Language = Language.UNKNOWN

    def to_dict(self) -> dict[str, object]:
        return {
            "sector": self.sector.value,
            "action": self.action.value,
            "confidence": round(self.confidence, 3),
            "sector_scores": {k: round(v, 3) for k, v in self.sector_scores.items() if v},
            "action_scores": {k: round(v, 3) for k, v in self.action_scores.items() if v},
            "matched": list(self.matched),
            "crisis": self.crisis,
            "language": self.language.value,
        }


_CRISIS_PATTERNS = (
    "தற்கொலை", "தற்கொலை செய்", "சாக வேண்டும்", "சாகவேண்டும்", "செத்து விட",
    "செத்துவிட", "உயிரை மாய்த்த", "உயிர் மாய்த்த", "விஷம் குடி", "விஷம் குடிச்ச",
    "காயப்படுத்த", "தீங்கு செய்", "வாழ பிடிக்கவில்லை", "வாழ்க்கையில் அர்த்தம் இல்லை",
    "எல்லாம் முடிந்து விட்டது", "இனி வாழ முடியாது",
    "suicide", "suicidal", "kill myself", "kill my self", "killing myself",
    "end my life", "ending my life", "self harm", "self-harm", "hurt myself",
    "hurting myself", "want to die", "wanna die", "no reason to live",
    "better off dead", "tharkolai", "saaga vendum", "saga vendum", "sethu vidu",
    "uyirai", "visham kudi", "vaazha pidikkala", "vaazha pidikkavillai",
)

_CRISIS_RE = re.compile(
    r"\b(?:kill(?:ing)?\s+my\s*self|end(?:ing)?\s+my\s+life|self[- ]?harm|"
    r"hurt(?:ing)?\s+my\s*self|want\s+to\s+die|wanna\s+die|"
    r"better\s+off\s+dead|no\s+reason\s+to\s+live)\b",
    re.IGNORECASE,
)

_ACTION_TERMS: dict[Action, tuple[tuple[str, float], ...]] = {
    Action.ELIGIBILITY: (
        ("தகுதி", 1.6), ("தகுதிகள்", 1.6), ("யாருக்கு", 1.4), ("யாரெல்லாம்", 1.4),
        ("யாருக்கெல்லாம்", 1.4), ("கிடைக்குமா", 1.3), ("கிடைக்கும்", 1.3),
        ("எந்த திட்டம்", 1.5), ("which scheme", 1.5), ("what scheme", 1.5),
        ("விண்ணப்பிக்கலாமா", 1.3), ("eligible", 1.6), ("eligibility", 1.6),
        ("qualify", 1.4), ("who can", 1.4), ("am i eligible", 1.8),
        ("can i get", 1.4), ("kidaikuma", 1.4), ("thaguthi", 1.4),
    ),
    Action.CALCULATION: (
        ("கணக்கிடு", 1.6), ("கணக்கீடு", 1.6), ("எவ்வளவு", 1.2), ("தவணை", 1.3),
        ("வட்டி", 1.3), ("emi", 1.8), ("calculate", 1.6), ("calculator", 1.6),
        ("how much", 1.4), ("interest", 1.2), ("installment", 1.3),
        ("instalment", 1.3), ("budget", 1.4), ("kanakku", 1.4), ("evlo", 1.2),
    ),
    Action.NEARBY: (
        ("அருகில்", 1.8), ("அருகாமையில்", 1.8), ("அருகே", 1.6), ("எங்கே", 1.3),
        ("முகவரி", 1.6), ("இடம்", 1.1), ("தொலைவு", 1.2), ("nearby", 1.8),
        ("near me", 1.8), ("where is", 1.5), ("address", 1.6), ("locate", 1.4),
        ("map", 1.2), ("arugil", 1.6), ("enge", 1.2), ("mugavari", 1.4),
    ),
    Action.APPLY: (
        ("விண்ணப்ப", 1.7), ("விண்ணப்பம்", 1.7), ("விண்ணப்பிக்க", 1.7),
        ("பதிவு", 1.3), ("apply", 1.7), ("application", 1.5), ("how to apply", 1.9),
        ("register", 1.4), ("registration", 1.4), ("vinnappam", 1.6),
    ),
    Action.DOCUMENTS: (
        ("ஆவணம்", 1.7), ("ஆவணங்கள்", 1.7), ("சான்று", 1.6), ("சான்றிதழ்", 1.6),
        ("ஆதாரம்", 1.3), ("document", 1.7), ("documents", 1.7), ("certificate", 1.6),
        ("proof", 1.3), ("patta", 1.4), ("aadhaar", 1.2), ("ration card", 1.2),
    ),
    Action.SMALL_TALK: (
        ("வணக்கம்", 1.9), ("நன்றி", 1.9), ("hello", 1.8), ("hi", 1.5), ("hey", 1.4),
        ("thanks", 1.7), ("thank you", 1.8), ("who are you", 1.8), ("நீ யார்", 1.7),
        ("what can you do", 1.8), ("என்ன செய்ய முடியும்", 1.7), ("vanakkam", 1.7),
        ("nandri", 1.6), ("good morning", 1.5), ("bye", 1.3),
    ),
    Action.INFORMATION: (
        ("தகவல்", 1.4), ("விவரம்", 1.4), ("விளக்கம்", 1.4), ("என்ன", 0.8),
        ("எப்படி", 0.7), ("information", 1.4), ("details", 1.4), ("explain", 1.4),
        ("what is", 1.3), ("how does", 1.2), ("tell me", 1.1), ("thagaval", 1.2),
        ("vivaram", 1.2),
    ),
}


def is_crisis(text: str) -> bool:
    """True when the message suggests self-harm or suicide risk."""
    normalized = normalize_for_match(text)
    if any(term in normalized for term in _CRISIS_PATTERNS):
        return True
    return bool(_CRISIS_RE.search(normalized))


def _build_sector_matchers() -> dict[Sector, TermMatcher]:
    matchers: dict[Sector, TermMatcher] = {}
    for sector, info in SECTORS.items():
        matcher = TermMatcher()
        matcher.add(info.ta, 2.0)
        matcher.add(info.en, 2.0)
        matcher.add(sector.value.replace("_", " "), 1.5)
        matcher.add_many(info.keywords, 1.0)
        matchers[sector] = matcher
    return matchers


def _build_action_matchers() -> dict[Action, TermMatcher]:
    matchers: dict[Action, TermMatcher] = {}
    for action, terms in _ACTION_TERMS.items():
        matcher = TermMatcher()
        for term, weight in terms:
            matcher.add(term, weight)
        matchers[action] = matcher
    return matchers


@lru_cache(maxsize=1)
def _sector_matchers() -> dict[Sector, TermMatcher]:
    return _build_sector_matchers()


@lru_cache(maxsize=1)
def _action_matchers() -> dict[Action, TermMatcher]:
    return _build_action_matchers()


def _rank(
    scores: dict[str, float], *, minimum: float, default: str
) -> tuple[str, float, dict[str, float]]:
    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    top_key, top_score = ranked[0]
    second_score = ranked[1][1] if len(ranked) > 1 else 0.0
    if top_score < minimum:
        return default, 0.0, scores
    margin = (top_score - second_score) / top_score if top_score else 0.0
    absolute = top_score / (top_score + 2.5)
    confidence = absolute * (0.65 + 0.35 * margin)
    return top_key, min(0.99, confidence), scores


def classify(text: str, *, language: Language | None = None) -> IntentResult:
    """Classify a citizen message into a sector, action and confidence."""
    normalized = normalize_for_match(text)
    detected = language or detect_language(text)

    if is_crisis(normalized):
        return IntentResult(
            sector=Sector.WELLNESS,
            action=Action.CRISIS,
            confidence=0.99,
            matched=("crisis",),
            crisis=True,
            language=detected,
        )

    sector_scores: dict[str, float] = {}
    matched: list[str] = []
    for sector, matcher in _sector_matchers().items():
        result = matcher.match(normalized)
        sector_scores[sector.value] = result.score
        matched.extend(result.matched)

    action_scores: dict[str, float] = {}
    for action, matcher in _action_matchers().items():
        action_scores[action.value] = matcher.match(normalized).score

    sector_key, confidence, _ = _rank(
        sector_scores, minimum=0.75, default=Sector.GENERAL.value
    )
    action_key, _, _ = _rank(
        action_scores, minimum=1.0, default=Action.INFORMATION.value
    )

    employment_markers = ("job", "jobs", "career", "suit me", "வேலை", "உத்யோகம்", "velai")
    finance_markers = ("loan", "emi", "interest rate", "kadan", "credit", "கடன்")
    if (
        sector_key != Sector.EMPLOYMENT.value
        and any(marker in normalized for marker in employment_markers)
        and not any(marker in normalized for marker in finance_markers)
    ):
        sector_key = Sector.EMPLOYMENT.value
        confidence = max(confidence, 0.8)

    if sector_key == Sector.GENERAL.value and _looks_like_small_talk(normalized):
        action_key = Action.SMALL_TALK.value

    return IntentResult(
        sector=Sector(sector_key),
        action=Action(action_key),
        confidence=confidence,
        sector_scores=sector_scores,
        action_scores=action_scores,
        matched=tuple(dict.fromkeys(matched)),
        crisis=False,
        language=detected,
    )


def _looks_like_small_talk(normalized: str) -> bool:
    tokens = normalized.split()
    return len(tokens) <= 4 and any(
        term in normalized
        for term in ("vanakkam", "வணக்கம்", "hello", "hi", "hey", "nandri", "நன்றி")
    )


def sector_hints(sector: Sector) -> SectorInfo:
    """Convenience accessor for callers that only need the metadata."""
    return SECTORS[sector]
