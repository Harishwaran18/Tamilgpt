"""Tamil ⇄ Latin romanisation and a phonetic key for fuzzy matching.

The romanisation is intentionally *matching-oriented*: it favours the spellings
people actually type in chat (``vanakkam``, ``kalvi``, ``velai``) over scholarly
diacritics. ``phonetic_key`` collapses spelling variants so a Tanglish query can
retrieve Tamil knowledge without a translation model.
"""

from __future__ import annotations

import re

from tamilgpt.nlp.script import AYTHAM, PULLI, TAMIL_DIGITS

_VOWELS = {
    "அ": "a", "ஆ": "aa", "இ": "i", "ஈ": "ii", "உ": "u", "ஊ": "uu",
    "எ": "e", "ஏ": "ee", "ஐ": "ai", "ஒ": "o", "ஓ": "oo", "ஔ": "au",
}
_VOWEL_SIGNS = {
    "ா": "aa", "ி": "i", "ீ": "ii", "ு": "u", "ூ": "uu",
    "ெ": "e", "ே": "ee", "ை": "ai", "ொ": "o", "ோ": "oo", "ௌ": "au",
}
_CONSONANTS = {
    "க": "k", "ங": "ng", "ச": "ch", "ஞ": "nj", "ட": "t", "ண": "n",
    "த": "th", "ந": "n", "ப": "p", "ம": "m", "ய": "y", "ர": "r",
    "ல": "l", "வ": "v", "ழ": "zh", "ள": "l", "ற": "r", "ன": "n",
    "ஜ": "j", "ஷ": "sh", "ஸ": "s", "ஹ": "h", "ஶ": "sh",
}

# Tamil does not contrast voiced and unvoiced stops, so ``kadan``/``katan`` and
# ``velai``/``veelai`` must collapse to the same key for retrieval.
_PHONETIC_REPLACEMENTS = (
    ("zh", "l"), ("th", "t"), ("sh", "s"), ("ch", "s"), ("nj", "n"),
    ("ng", "n"), ("kh", "k"), ("gh", "g"), ("ph", "p"), ("bh", "b"),
    ("dh", "d"), ("jh", "j"), ("aa", "a"), ("ii", "i"), ("uu", "u"),
    ("ee", "e"), ("oo", "o"), ("d", "t"), ("b", "p"), ("g", "k"),
    ("w", "v"),
)
_DOUBLE_LETTER_RE = re.compile(r"(.)\1+")


def romanize(text: str) -> str:
    """Transliterate Tamil script to a chat-friendly Latin form.

    Latin characters and digits pass through unchanged, which makes this safe to
    call on mixed-script input.
    """
    out: list[str] = []
    chars = list(text)
    i = 0
    while i < len(chars):
        ch = chars[i]
        if ch in _VOWELS:
            out.append(_VOWELS[ch])
        elif ch in _CONSONANTS:
            consonant = _CONSONANTS[ch]
            nxt = chars[i + 1] if i + 1 < len(chars) else ""
            if nxt == PULLI:
                out.append(consonant)
                i += 1
            elif nxt in _VOWEL_SIGNS:
                out.append(consonant + _VOWEL_SIGNS[nxt])
                i += 1
            else:
                out.append(consonant + "a")
        elif ch == AYTHAM:
            out.append("h")
        elif ch in TAMIL_DIGITS:
            out.append(TAMIL_DIGITS[ch])
        elif ch == PULLI:
            pass
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def phonetic_key(text: str) -> str:
    """Collapse spelling variants into a stable key used for fuzzy matching."""
    key = romanize(text).lower()
    key = re.sub(r"[^a-z0-9]", "", key)
    for source, target in _PHONETIC_REPLACEMENTS:
        key = key.replace(source, target)
    key = _DOUBLE_LETTER_RE.sub(r"\1", key)
    return key


def skeleton_key(text: str) -> str:
    """Consonant skeleton used as a low-weight fallback match.

    ``sirukarai`` and ``sarkarai`` both reduce to ``srkr``, which rescues many
    vowel-spelling differences in Tanglish without affecting exact matches.
    """
    key = phonetic_key(text)
    skeleton = re.sub(r"[aeiou]", "", key)
    return skeleton if len(skeleton) >= 3 else ""


def variants(text: str) -> set[str]:
    """Return the raw, phonetic and skeleton spellings of a term."""
    return {text.lower(), romanize(text).lower(), phonetic_key(text), skeleton_key(text)}


# Minimal approximate Latin→Tamil used only for display of user-entered names.
_LATIN_TO_TAMIL = (
    ("zh", "ழ"), ("th", "த"), ("sh", "ஷ"), ("ch", "ச"), ("ng", "ங"),
    ("nj", "ஞ"), ("aa", "ஆ"), ("ee", "ஈ"), ("oo", "ஊ"), ("ai", "ஐ"),
    ("au", "ஔ"), ("kh", "க"), ("gh", "க"), ("ph", "ப"), ("bh", "ப"),
    ("dh", "த"), ("jh", "ஜ"), ("a", "அ"), ("i", "இ"), ("u", "உ"),
    ("e", "எ"), ("o", "ஒ"), ("k", "க"), ("g", "க"), ("c", "ச"),
    ("j", "ஜ"), ("t", "ட"), ("d", "ட"), ("n", "ந"), ("p", "ப"),
    ("b", "ப"), ("m", "ம"), ("y", "ய"), ("r", "ர"), ("l", "ல"),
    ("v", "வ"), ("s", "ஸ"), ("h", "ஹ"), ("f", "ஃப"),
)


def to_tamil(text: str) -> str:
    """Approximate Latin→Tamil transliteration.

    Tamil has no one-to-one Latin mapping, so this is a best-effort helper for
    echoing a user's name. It is never used for retrieval.
    """
    lowered = text.lower()
    out: list[str] = []
    i = 0
    while i < len(lowered):
        for latin, tamil in _LATIN_TO_TAMIL:
            if lowered.startswith(latin, i):
                out.append(tamil)
                i += len(latin)
                break
        else:
            out.append(lowered[i])
            i += 1
    return "".join(out)
