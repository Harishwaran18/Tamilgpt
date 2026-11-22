"""Non-diagnostic symptom triage with explicit red-flag escalation."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from tamilgpt.knowledge import HealthTopic, KnowledgeBase, get_knowledge_base
from tamilgpt.nlp.language import Language
from tamilgpt.nlp.normalize import normalize_for_match

_EMERGENCY_TERMS = (
    "மயக்கம்", "மூச்சுத் திணறல்", "மூச்சு விட முடிய", "நெஞ்சு வலி", "இரத்தப்போக்கு",
    "வலிப்பு", "உணர்வு இல்லை", "சுயநினைவு இல்லை", "விஷம்", "தற்கொலை",
    "unconscious", "not breathing", "breathless", "severe chest pain", "chest pain",
    "heavy bleeding", "bleeding", "seizure", "convulsion", "overdose", "suicide",
    "stroke", "paralysis", "fainted",
)

_RED_FLAG_HINTS = {
    "fever": ("3 நாட்கள்", "3 days", "102", "more than 3"),
    "dengue": ("bleeding", "இரத்தம்", "vomit", "வாந்தி", "abdominal", "வயிறு"),
    "chest-pain": ("15", "minutes", "நிமிடம்"),
    "pregnancy-danger": ("bleeding", "இரத்த", "headache", "தலைவலி", "vision", "பார்வை"),
}
_DURATION_RE = re.compile(r"(\d+)\s*(?:days?|நாட்கள்|நாள்)", re.IGNORECASE)


@dataclass(slots=True)
class HealthTriage:
    topic: HealthTopic | None
    emergency: bool
    urgent: bool = False
    matched_terms: tuple[str, ...] = ()
    helplines: tuple[str, ...] = ("104", "108")
    notes_ta: list[str] = field(default_factory=list)
    notes_en: list[str] = field(default_factory=list)

    def to_dict(self, language: str = "ta") -> dict[str, object]:
        is_ta = language == "ta"
        topic = self.topic
        if topic is None:
            return {
                "topic": None,
                "emergency": self.emergency,
                "urgent": self.urgent,
                "matched_terms": list(self.matched_terms),
                "helplines": list(self.helplines),
                "notes": self.notes_ta if is_ta else self.notes_en,
                "advice": None,
                "red_flags": [],
            }
        return {
            "topic": topic.id,
            "title": topic.title_ta if is_ta else topic.title_en,
            "title_ta": topic.title_ta,
            "title_en": topic.title_en,
            "emergency": self.emergency,
            "urgent": self.urgent,
            "matched_terms": list(self.matched_terms),
            "symptoms": list(topic.symptoms_ta if is_ta else topic.symptoms_en),
            "red_flags": list(topic.red_flags_ta if is_ta else topic.red_flags_en),
            "advice": topic.advice_ta if is_ta else topic.advice_en,
            "specialist": topic.specialist_ta if is_ta else topic.specialist_en,
            "helplines": list(self.helplines),
            "notes": self.notes_ta if is_ta else self.notes_en,
            "source_url": topic.source_url,
        }


def triage(
    text: str,
    *,
    language: Language | str = Language.TAMIL,
    kb: KnowledgeBase | None = None,
) -> HealthTriage:
    base = kb or get_knowledge_base()
    normalized = normalize_for_match(text)

    emergency = any(term in normalized for term in _EMERGENCY_TERMS)
    urgent = False
    hits = base.search_health(text, top_k=3)
    topic = hits[0].item if hits and hits[0].score >= 2.0 else None
    if topic is not None and topic.id == "child-fever" and not any(
        term in normalized for term in ("குழந்தை", "கைக்குழந்தை", "child", "baby", "infant")
    ):
        topic = next((item for item in base.health_topics if item.id == "fever"), topic)

    notes_ta: list[str] = []
    notes_en: list[str] = []
    if emergency:
        notes_ta.append("இவை அவசர அறிகுறிகளாக இருக்கலாம். உடனடியாக 108 என்று அழையுங்கள்.")
        notes_en.append("These may be emergency signs. Call 108 immediately.")
    if topic is not None:
        hints = _RED_FLAG_HINTS.get(topic.id, ())
        if any(hint in normalized for hint in hints):
            emergency = True
            notes_ta.append("நீங்கள் குறிப்பிட்ட அறிகுறி ஆபத்தானதாக இருக்கலாம்; மருத்துவரை உடனடியாக அணுகுங்கள்.")
            notes_en.append("The symptom you mentioned can be a warning sign; seek medical care promptly.")
        duration = _DURATION_RE.search(normalized)
        if topic.id == "fever" and duration and int(duration.group(1)) >= 3:
            urgent = True
            notes_ta.append("மூன்று நாட்களுக்கு மேல் காய்ச்சல் தொடர்வது மருத்துவப் பரிசோதனைக்குரியது.")
            notes_en.append("Fever lasting more than three days needs medical assessment.")
    if topic is None and not emergency:
        notes_ta.append("தயவுசெய்து அறிகுறிகளை இன்னும் விரிவாகக் கூறுங்கள் (எ.கா. காய்ச்சல், இருமல், வயிற்று வலி).")
        notes_en.append("Please describe the symptoms in more detail (for example fever, cough or stomach pain).")

    return HealthTriage(
        topic=topic,
        emergency=emergency,
        urgent=urgent,
        matched_terms=tuple(hits[0].matched_terms) if hits else (),
        notes_ta=notes_ta,
        notes_en=notes_en,
    )


def health_topics(*, kb: KnowledgeBase | None = None) -> list[HealthTopic]:
    return list((kb or get_knowledge_base()).health_topics)
