"""Safety layer: crisis response, disclaimers, PII redaction and injection guard."""

from __future__ import annotations

import re

from tamilgpt.nlp.language import Language
from tamilgpt.sectors import Sector

_HEALTH_DISCLAIMER = {
    "ta": "இது மருத்துவ ஆலோசனை அல்ல. அறிகுறிகள் தொடர்ந்தால் அல்லது தீவிரமாக இருந்தால் மருத்துவரை அணுகுங்கள். அவசரத்திற்கு 108.",
    "en": "This is not medical advice. Consult a doctor if symptoms continue or are severe. For emergencies call 108.",
}
_LEGAL_DISCLAIMER = {
    "ta": "இது சட்ட ஆலோசனை அல்ல. உங்கள் வழக்கின் தன்மையைப் பொறுத்து தகுதியான வழக்கறிஞரை அணுகுங்கள். இலவச சட்ட உதவிக்கு 15100.",
    "en": "This is not legal advice. Consult a qualified lawyer about your specific case. For free legal aid call 15100.",
}
_FINANCE_DISCLAIMER = {
    "ta": "இது நிதி ஆலோசனை அல்ல. கடன் அல்லது முதலீட்டு முடிவுக்கு முன் வங்கி/நிபுணரை அணுகி மொத்த செலவை ஒப்பிடுங்கள்.",
    "en": "This is not financial advice. Before borrowing or investing, compare the total cost with your bank or a qualified adviser.",
}
_SCHEME_DISCLAIMER = {
    "ta": "தகுதி மற்றும் தொகை அரசு அலுவலகத்தின் இறுதி முடிவைப் பொறுத்தது. அதிகாரப்பூர்வ இணையதளத்தில் தற்போதைய விவரங்களை உறுதிப்படுத்துங்கள்.",
    "en": "Final eligibility and amounts are decided by the implementing office. Confirm current details on the official portal.",
}
_WELLNESS_DISCLAIMER = {
    "ta": "நெருக்கடி நிலையில் உடனடியாக 14416 (டெலி-மனஸ்) அல்லது 112 என்று அழையுங்கள். நீங்கள் தனியாக இல்லை.",
    "en": "In a crisis, call 14416 (Tele-MANAS) or 112 immediately. You are not alone.",
}

_DISCLAIMERS: dict[Sector, dict[str, str]] = {
    Sector.HEALTHCARE: _HEALTH_DISCLAIMER,
    Sector.LEGAL: _LEGAL_DISCLAIMER,
    Sector.FINANCE: _FINANCE_DISCLAIMER,
    Sector.BUSINESS: _FINANCE_DISCLAIMER,
    Sector.SCHEMES: _SCHEME_DISCLAIMER,
    Sector.WOMEN_ELDERLY: _SCHEME_DISCLAIMER,
    Sector.WELLNESS: _WELLNESS_DISCLAIMER,
}

_CRISIS_TEMPLATE = {
    "ta": (
        "நீங்கள் இப்போது மிகவும் கடினமான நேரத்தைக் கடந்து கொண்டிருக்கிறீர்கள். "
        "நீங்கள் தனியாக இல்லை; உதவி கிடைக்கும்.\n\n"
        "**உடனடி உதவி**\n"
        "- டெலி-மனஸ் மனநல ஆலோசனை: **14416** (24 மணி நேரம், இலவசம்)\n"
        "- அவசர எண்: **112**\n"
        "- பெண்கள் உதவி: **181** · குழந்தைகள் உதவி: **1098**\n\n"
        "உங்களைக் காயப்படுத்திக் கொள்ளும் எண்ணம் வந்தால், அருகிலுள்ள நம்பகமான ஒருவரை "
        "அழையுங்கள் அல்லது அருகிலுள்ள அவசர சிகிச்சைப் பிரிவுக்குச் செல்லுங்கள். "
        "நான் ஒரு மென்பொருள் உதவியாளர்; ஆனால் உங்களுக்கு உதவ நேரடி மனிதர்கள் காத்திருக்கிறார்கள். "
        "நீங்கள் முக்கியம்."
    ),
    "en": (
        "You are going through a very difficult moment. You are not alone, and help is available.\n\n"
        "**Immediate help**\n"
        "- Tele-MANAS mental health helpline: **14416** (24 hours, free)\n"
        "- Emergency: **112**\n"
        "- Women's helpline: **181** · Child helpline: **1098**\n\n"
        "If you are thinking of harming yourself, call someone you trust or go to the nearest "
        "emergency department. I am a software assistant, but trained people are ready to help you. "
        "You matter."
    ),
}


def _lang_key(language: Language | str) -> str:
    return "en" if str(language) in {"en", Language.ENGLISH.value} else "ta"


def crisis_reply(language: Language | str) -> str:
    return _CRISIS_TEMPLATE[_lang_key(language)]


def disclaimers_for(sector: Sector, language: Language | str) -> list[str]:
    entry = _DISCLAIMERS.get(sector)
    return [entry[_lang_key(language)]] if entry else []


_AADHAAR_RE = re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")
_PHONE_RE = re.compile(r"\b(?:\+91[\s-]?)?[6-9]\d{9}\b")
_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b")
_LONG_NUMBER_RE = re.compile(r"\b\d{11,18}\b")
_INJECTION_PATTERNS = (
    "ignore previous instructions", "ignore all previous", "system prompt",
    "reveal your prompt", "developer mode", "jailbreak", "act as an unfiltered",
    "forget your rules", "disregard your instructions",
)


def redact_pii(text: str) -> str:
    """Mask Aadhaar, phone, email and long account numbers before logging."""
    text = _EMAIL_RE.sub("[email hidden]", text)
    text = _AADHAAR_RE.sub("[Aadhaar hidden]", text)
    text = _PHONE_RE.sub("[phone hidden]", text)
    text = _LONG_NUMBER_RE.sub("[number hidden]", text)
    return text


def looks_like_prompt_injection(text: str) -> bool:
    lowered = text.lower()
    return any(pattern in lowered for pattern in _INJECTION_PATTERNS)
