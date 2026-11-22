"""Tokenisation, stop-word removal and light stemming for Tamil and English."""

from __future__ import annotations

from tamilgpt.nlp.normalize import normalize_for_match
from tamilgpt.nlp.script import WORD_RE, has_tamil

STOPWORDS: frozenset[str] = frozenset(
    {
        # Tamil function words
        "ஒரு", "மற்றும்", "ஆனால்", "என்பது", "என்று", "என்ன", "எப்படி", "ஏன்",
        "எங்கே", "எப்போது", "யார்", "எது", "நான்", "எனக்கு", "என்", "நீ", "உன்",
        "அவர்", "அவள்", "அது", "இது", "ஆகும்", "உள்ள", "உள்ளது", "வேண்டும்",
        "முடியும்", "செய்ய", "பற்றி", "குறித்து", "அதனால்", "அதாவது", "மிக",
        "மிகவும்", "சில", "எல்லாம்", "ஆக", "என", "என்ற", "கொண்டு", "இருந்து",
        "வரை", "மேல்", "கீழ்", "பின்", "முன்", "ஆகவே", "எனவே", "தான்", "கூட",
        "உம்", "இல்லை", "இருக்கிறது", "சொல்லுங்கள்", "கூறு", "தெரிய", "உதவி",
        # English function words
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "to", "of", "in", "on", "for", "and", "or", "but", "with", "about",
        "how", "what", "which", "who", "whom", "when", "where", "why", "can",
        "could", "should", "would", "do", "does", "did", "i", "me", "my", "we",
        "our", "you", "your", "it", "this", "that", "these", "those", "please",
        "tell", "know", "need", "want", "get", "will", "shall", "may", "might",
        "must", "from", "by", "at", "as", "if", "then", "than", "so", "not",
        "no", "yes", "am", "have", "has", "had", "there", "their", "them",
    }
)

_TAMIL_SUFFIXES = tuple(
    sorted(
        {
            "களுக்கு", "களில்", "களின்", "களால்", "களை", "கள்", "க்கான",
            "இலிருந்து", "ிலிருந்து", "இருந்து", "ிருக்கு", "ுக்கு", "க்கு",
            "யில்", "இல்", "ில்", "உடன்", "ுடன்", "ஆல்", "ால்", "ோடு",
            "உடைய", "ுடைய", "ஆக", "ாக", "இன்", "ின்", "ஐ", "ை", "ஏ", "ே",
            "உம்", "ும்", "ஆ", "ா",
        },
        key=len,
        reverse=True,
    )
)

_ENGLISH_SUFFIXES = ("ingly", "edly", "ing", "ers", "ies", "ed", "es", "s")


def tokenize(text: str) -> list[str]:
    """Split normalised text into Tamil/Latin/number tokens."""
    return WORD_RE.findall(normalize_for_match(text))


def stem(token: str) -> str:
    """Strip common inflectional suffixes, keeping a useful root."""
    if has_tamil(token):
        for suffix in _TAMIL_SUFFIXES:
            if token.endswith(suffix) and len(token) - len(suffix) >= 2:
                return token[: -len(suffix)]
        return token

    lowered = token.lower()
    for suffix in _ENGLISH_SUFFIXES:
        if lowered.endswith(suffix) and len(lowered) - len(suffix) >= 3:
            root = lowered[: -len(suffix)]
            if suffix == "ies":
                root += "y"
            return root
    return lowered


def content_tokens(text: str) -> list[str]:
    """Return stemmed, de-duplicated content tokens in first-seen order."""
    seen: set[str] = set()
    result: list[str] = []
    for token in tokenize(text):
        if token in STOPWORDS or len(token) == 1:
            continue
        root = stem(token)
        if root in STOPWORDS or not root:
            continue
        if root not in seen:
            seen.add(root)
            result.append(root)
    return result


def ngrams(tokens: list[str], n: int) -> list[tuple[str, ...]]:
    if n <= 0 or len(tokens) < n:
        return []
    return [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]
