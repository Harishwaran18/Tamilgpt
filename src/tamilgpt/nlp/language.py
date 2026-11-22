"""Script-aware language detection for Tamil, English and Tanglish."""

from __future__ import annotations

from enum import StrEnum

from tamilgpt.nlp.normalize import normalize_for_match
from tamilgpt.nlp.script import count_latin, count_tamil
from tamilgpt.nlp.tokenize import tokenize
from tamilgpt.nlp.transliterate import phonetic_key


class Language(StrEnum):
    TAMIL = "ta"
    ENGLISH = "en"
    TANGLISH = "tanglish"
    MIXED = "mixed"
    UNKNOWN = "unknown"


# High-frequency Romanised Tamil words that clearly signal Tanglish input.
_TANGLISH_LEXICON = frozenset(
    phonetic_key(word)
    for word in (
        "vanakkam", "nandri", "enna", "epdi", "eppadi", "yaaru", "ethu", "ethuku",
        "kalvi", "palli", "kalluri", "padipu", "thervu", "velai", "vElai", "sambalam",
        "kadan", "kadai", "thozhil", "vivasayam", "payir", "nel", "urum", "poochi",
        "maruthuvam", "maruthuvar", "noi", "kaichal", "vali", "sirukarai", "udanal",
        "thittam", "thittangal", "arasu", "maniyam", "udhavi", "sattam", "vazhakku",
        "vakkil", "pugar", "urimai", "panam", "semippu", "vatti", "mosadi", "nidhi",
        "magalir", "pengal", "mudhiyor", "oyvuudhiyam", "vidhavai", "karppam",
        "mananalam", "kavalai", "bayam", "thookaminmai", "vedhanai", "thanimai",
        "enakku", "ungalukku", "avasiyam", "sollunga", "theriyum", "puriyala",
        "epdi", "enge", "eppo", "evlo", "evvalavu", "yaar", "enna", "illa",
    )
)


def detect_language(text: str) -> Language:
    """Classify input by script and vocabulary."""
    normalized = normalize_for_match(text)
    if not normalized:
        return Language.UNKNOWN

    tamil = count_tamil(normalized)
    latin = count_latin(normalized)

    if tamil and latin:
        ratio = min(tamil, latin) / max(tamil, latin)
        return Language.MIXED if ratio >= 0.15 else (Language.TAMIL if tamil > latin else Language.ENGLISH)
    if tamil:
        return Language.TAMIL
    if not latin:
        return Language.UNKNOWN

    tokens = tokenize(normalized)
    tanglish_hits = sum(1 for token in tokens if phonetic_key(token) in _TANGLISH_LEXICON)
    if tanglish_hits and tanglish_hits / max(1, len(tokens)) >= 0.2:
        return Language.TANGLISH
    return Language.ENGLISH


def reply_language(requested: str | None, detected: Language) -> Language:
    """Resolve the reply language from an explicit request or the detected script."""
    if requested in {"ta", "en"}:
        return Language(requested)
    if detected is Language.ENGLISH:
        return Language.ENGLISH
    return Language.TAMIL
