"""Unicode ranges and regular expressions for the Tamil script."""

from __future__ import annotations

import re

TAMIL_BLOCK_START = 0x0B80
TAMIL_BLOCK_END = 0x0BFF

PULLI = "\u0BCD"
AYTHAM = "\u0B83"

TAMIL_CHAR_RE = re.compile(r"[\u0B80-\u0BFF]")
TAMIL_WORD_RE = re.compile(r"[\u0B80-\u0BFF]+")
LATIN_WORD_RE = re.compile(r"[A-Za-z]+")

# Tamil words must keep combining marks, so a word is any run inside the block.
WORD_RE = re.compile(r"[\u0B80-\u0BFF]+|[A-Za-z]+|\d+(?:[.,]\d+)?")

TAMIL_DIGITS = {
    "௦": "0", "௧": "1", "௨": "2", "௩": "3", "௪": "4",  # noqa: RUF001
    "௫": "5", "௬": "6", "௭": "7", "௮": "8", "௯": "9",
}


def has_tamil(text: str) -> bool:
    return bool(TAMIL_CHAR_RE.search(text))


def count_tamil(text: str) -> int:
    return len(TAMIL_CHAR_RE.findall(text))


def count_latin(text: str) -> int:
    return len(LATIN_WORD_RE.findall(text))
