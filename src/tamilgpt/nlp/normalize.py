"""Text normalisation tuned for Tamil chat input.

Citizens type on mobile keyboards, mix scripts, use smart quotes and zero-width
joiners. Normalising once at the edge keeps every downstream component simple.
"""

from __future__ import annotations

import re
import unicodedata

from tamilgpt.nlp.script import TAMIL_DIGITS

_ZERO_WIDTH = dict.fromkeys(map(ord, "\u200b\u200c\u200d\u2060\ufeff"), None)
_QUOTES = str.maketrans({"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"'})
_WHITESPACE_RE = re.compile(r"\s+")
# Keep Tamil letters, Latin letters, digits and a few separators used by the matcher.
_MATCH_NOISE_RE = re.compile(r"[^\u0B80-\u0BFFA-Za-z0-9\s.,%/+\-₹]")

# Common chat abbreviations, expanded before matching.
_ABBREVIATIONS = {
    "tn": "tamil nadu",
    "govt": "government",
    "gov": "government",
    "schl": "scheme",
    "schemes": "scheme",
    "doc": "doctor",
    "hosp": "hospital",
    "bpl": "below poverty line",
    "apl": "above poverty line",
    "sc": "scheduled caste",
    "st": "scheduled tribe",
    "obc": "other backward class",
    "k": "000",
}


def normalize_text(text: str) -> str:
    """Canonical Unicode form with control characters and smart quotes removed."""
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = text.translate(_ZERO_WIDTH).translate(_QUOTES)
    text = "".join(TAMIL_DIGITS.get(ch, ch) for ch in text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = _WHITESPACE_RE.sub(" ", text)
    return text.strip()


def normalize_for_match(text: str) -> str:
    """Lowercase, punctuation-light form used for keyword matching."""
    text = normalize_text(text).lower()
    text = _MATCH_NOISE_RE.sub(" ", text)
    text = _WHITESPACE_RE.sub(" ", text)
    return text.strip()


def expand_abbreviations(text: str) -> str:
    """Expand a handful of high-signal chat abbreviations, token by token."""
    words = normalize_for_match(text).split()
    expanded: list[str] = []
    for word in words:
        replacement = _ABBREVIATIONS.get(word)
        if replacement is None:
            expanded.append(word)
        elif replacement == "000":
            # "50k" → "50000"; keep the number, drop the marker.
            if expanded and expanded[-1].isdigit():
                expanded[-1] = expanded[-1] + "000"
            else:
                expanded.append("000")
        else:
            expanded.extend(replacement.split())
    return " ".join(expanded)


def truncate(text: str, limit: int) -> str:
    """Hard-limit a string without splitting a Tamil grapheme cluster badly."""
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"
