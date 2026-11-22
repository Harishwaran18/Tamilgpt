"""Tamil-aware natural language utilities (no external NLP models required)."""

from tamilgpt.nlp.entities import Entities, extract_entities
from tamilgpt.nlp.intent import IntentResult, classify
from tamilgpt.nlp.language import Language, detect_language
from tamilgpt.nlp.normalize import normalize_for_match, normalize_text
from tamilgpt.nlp.tokenize import content_tokens, stem, tokenize

__all__ = [
    "Entities",
    "IntentResult",
    "Language",
    "classify",
    "content_tokens",
    "detect_language",
    "extract_entities",
    "normalize_for_match",
    "normalize_text",
    "stem",
    "tokenize",
]
