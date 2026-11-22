"""Rule-based entity extraction for calculators and personalisation.

The extractors read numbers and a curated vocabulary (districts, crops, education
levels). They never guess: a missing value stays ``None`` so the UI can ask for it.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field

from tamilgpt.nlp.normalize import normalize_for_match
from tamilgpt.nlp.tokenize import tokenize

_MONEY = re.compile(
    r"(?:₹|rs\.?|ரூ\.?|ரூபாய்|rupees?)\s*([\d][\d,]*(?:\.\d+)?)\s*"
    r"(லட்சம்|இலட்சம்|lakhs?|lacs?|கோடி|crores?|thousand|ஆயிரம்|k)?"
)
_NUMBER_UNIT = re.compile(
    r"([\d][\d,]*(?:\.\d+)?)\s*(லட்சம்|இலட்சம்|lakhs?|lacs?|கோடி|crores?|thousand|ஆயிரம்)"
)
_AGE = re.compile(
    r"(\d{1,3})\s*(?:வயது|வயசு|vayasu|vayathu|years?\s*old|yrs?\s*old|y/o)(?=\s|$|[,.])"
    r"|\b(?:age|i\s*am|i'm|im)\s*(?:is|:)?\s*(\d{1,3})\b"
    r"|(\d{1,3})\s*(?:years?|yrs?)(?=\s|$|[,.])"
)
_FAMILY = re.compile(
    r"(\d{1,2})\s*(?:பேர்|members?|persons?)(?=\s|$|[,.])|\bfamily\s+of\s+(\d{1,2})\b"
)
_LAND = re.compile(
    r"([\d.]+)\s*(ஏக்கர்|ஏக்கரில்|acres?|acre|சென்ட்|cents?)(?=\s|$|[,.])"
)
_STANDALONE_NUMBER = re.compile(r"\b(\d{4,9})\b")

_UNIT_MULTIPLIERS = {
    "லட்சம்": 100_000, "இலட்சம்": 100_000, "lakh": 100_000, "lakhs": 100_000,
    "lac": 100_000, "lacs": 100_000, "கோடி": 10_000_000, "crore": 10_000_000,
    "crores": 10_000_000, "thousand": 1_000, "ஆயிரம்": 1_000, "k": 1_000,
}

_INCOME_WORDS = (
    "வருமானம்", "வருமான", "சம்பளம்", "சம்பள", "மாத வருமானம்", "மாதம்", "income",
    "monthly", "salary", "earn", "earning", "wage", "kooli", "sambalam",
    "varumanam", "maatham",
)

_EDUCATION_MAP = {
    "10th": "10th", "tenth": "10th", "பத்தாம் வகுப்பு": "10th", "10 ஆம் வகுப்பு": "10th",
    "12th": "12th", "twelfth": "12th", "பன்னிரண்டாம் வகுப்பு": "12th",
    "plus two": "12th", "+2": "12th", "hsc": "12th", "sslc": "10th",
    "iti": "ITI", "ஐடிஐ": "ITI", "diploma": "Diploma", "டிப்ளமோ": "Diploma",
    "degree": "Degree", "பட்டம்": "Degree", "b.sc": "Degree", "bsc": "Degree",
    "b.com": "Degree", "bcom": "Degree", "pg": "Postgraduate",
    "postgraduate": "Postgraduate", "m.sc": "Postgraduate", "msc": "Postgraduate",
    "engineering": "Engineering", "இன்ஜினியரிங்": "Engineering",
    "b.tech": "Engineering", "btech": "Engineering", "medical": "Medical",
    "மருத்துவம்": "Medical", "mbbs": "Medical", "nursing": "Nursing",
    "nurse": "Nursing", "செவிலியர்": "Nursing", "illiterate": "No formal schooling",
    "படிக்கவில்லை": "No formal schooling",
}

_DISTRICTS = (
    "Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore", "Dharmapuri",
    "Dindigul", "Erode", "Kallakurichi", "Kancheepuram", "Kanyakumari", "Karur",
    "Krishnagiri", "Madurai", "Mayiladuthurai", "Nagapattinam", "Namakkal",
    "Nilgiris", "Perambalur", "Pudukkottai", "Ramanathapuram", "Ranipet",
    "Salem", "Sivaganga", "Tenkasi", "Thanjavur", "Theni", "Thoothukudi",
    "Tiruchirappalli", "Tirunelveli", "Tirupathur", "Tiruppur", "Tiruvallur",
    "Tiruvannamalai", "Tiruvarur", "Vellore", "Viluppuram", "Virudhunagar",
    "அரியலூர்", "செங்கல்பட்டு", "சென்னை", "கோயம்புத்தூர்", "கடலூர்",
    "தர்மபுரி", "திண்டுக்கல்", "ஈரோடு", "கள்ளக்குறிச்சி", "காஞ்சிபுரம்",
    "கன்னியாகுமரி", "கரூர்", "கிருஷ்ணகிரி", "மதுரை", "மயிலாடுதுறை",
    "நாகப்பட்டினம்", "நாமக்கல்", "நீலகிரி", "பெரம்பலூர்", "புதுக்கோட்டை",
    "ராமநாதபுரம்", "ராணிப்பேட்டை", "சேலம்", "சிவகங்கை", "தென்காசி",
    "தஞ்சாவூர்", "தேனி", "தூத்துக்குடி", "திருச்சிராப்பள்ளி", "திருநெல்வேலி",
    "திருப்பத்தூர்", "திருப்பூர்", "திருவள்ளூர்", "திருவண்ணாமலை", "திருவாரூர்",
    "வேலூர்", "விழுப்புரம்", "விருதுநகர்",
)

_CROPS = (
    "நெல்", "கரும்பு", "மக்காச்சோளம்", "பருத்தி", "கோதுமை", "சோளம்", "கேழ்வரகு",
    "உளுந்து", "துவரை", "கடலை", "எள்", "நிலக்கடலை", "சூரியகாந்தி", "தென்னை",
    "வாழை", "மாமரம்", "மா", "தக்காளி", "வெங்காயம்", "உருளைக்கிழங்கு", "கத்தரி",
    "வெண்டை", "பாகற்காய்", "மிளகாய்", "மஞ்சள்", "இஞ்சி", "பூண்டு", "மல்லி",
    "paddy", "rice", "sugarcane", "maize", "cotton", "wheat", "ragi", "millet",
    "urad", "pulses", "groundnut", "coconut", "banana", "mango", "tomato",
    "onion", "potato", "brinjal", "lady finger", "bitter gourd", "chilli",
    "turmeric", "ginger", "garlic",
)

_LOAN_PURPOSE = {
    "business": ("தொழில்", "வியாபாரம்", "கடை", "business", "shop", "msme", "startup"),
    "education": ("கல்வி", "படிப்பு", "college", "education", "school"),
    "home": ("வீடு", "வீட்டு", "home", "house", "housing"),
    "vehicle": ("வாகனம்", "கார்", "பைக்", "vehicle", "car", "bike"),
    "agriculture": ("விவசாய", "பயிர்", "farm", "agriculture", "crop"),
    "gold": ("நகை", "தங்க", "gold"),
    "personal": ("தனிநபர்", "personal"),
}

_OCCUPATION_MAP = {
    "farmer": ("விவசாயி", "விவசாயம்", "farmer", "farming", "vivasayam", "vivasaayi"),
    "tailor": ("தையல்", "தையலர்", "tailor", "stitching", "thaiyal", "thaiyalar"),
    "teacher": ("ஆசிரியர்", "ஆசிரியை", "teacher", "teaching", "aasiriyar"),
    "nurse": ("செவிலியர்", "nurse", "nursing", "seviliyar"),
    "driver": ("ஓட்டுநர்", "driver", "driving", "ottunar"),
    "student": (
        "மாணவர்", "மாணவி", "student", "படிக்கிறேன்", "படித்திருக்கேன்",
        "padikkiren", "padithiruken", "padithirukken",
    ),
    "vendor": ("வியாபாரி", "தெரு வியாபாரி", "vendor", "hawker", "viyabari"),
    "shop_owner": ("கடை", "shop", "store"),
    "worker": ("தொழிலாளி", "worker", "labour", "labor", "coolie", "kooli"),
    "engineer": ("பொறியாளர்", "engineer"),
    "accountant": ("கணக்காளர்", "accountant"),
    "homemaker": ("இல்லத்தரசி", "homemaker", "housewife"),
    "business": ("தொழில்", "வணிகம்", "business", "entrepreneur", "msme", "thozhil"),
}


@dataclass(slots=True)
class Entities:
    money_amounts: list[int] = field(default_factory=list)
    monthly_income: int | None = None
    age: int | None = None
    family_size: int | None = None
    gender: str | None = None
    education: str | None = None
    district: str | None = None
    crop: str | None = None
    land_acres: float | None = None
    loan_purpose: str | None = None
    occupation: str | None = None
    marital_status: str | None = None

    def as_dict(self) -> dict[str, object]:
        return {key: value for key, value in asdict(self).items() if value not in (None, [], "")}


def _contains_term(normalized: str, tokens: set[str], term: str) -> bool:
    if " " in term or any(char in term for char in ".+-"):
        return term in normalized
    if term.isascii():
        return term in tokens
    return term in tokens or (len(term) >= 3 and any(t.startswith(term) for t in tokens))


def _parse_amount(raw: str, unit: str | None) -> int | None:
    try:
        value = float(raw.replace(",", ""))
    except ValueError:
        return None
    multiplier = _UNIT_MULTIPLIERS.get((unit or "").strip().lower(), 1)
    return int(value * multiplier)


def extract_entities(text: str) -> Entities:
    """Extract numeric and vocabulary entities from a citizen message."""
    normalized = normalize_for_match(text)
    entities = Entities()

    for match in _MONEY.finditer(normalized):
        amount = _parse_amount(match.group(1), match.group(2))
        if amount:
            entities.money_amounts.append(amount)

    for match in _NUMBER_UNIT.finditer(normalized):
        amount = _parse_amount(match.group(1), match.group(2))
        if amount and amount not in entities.money_amounts:
            entities.money_amounts.append(amount)

    age_match = _AGE.search(normalized)
    if age_match:
        raw = next((group for group in age_match.groups() if group), None)
        if raw:
            entities.age = int(raw)

    family_match = _FAMILY.search(normalized)
    if family_match:
        raw = family_match.group(1) or family_match.group(2)
        if raw:
            entities.family_size = int(raw)

    land_match = _LAND.search(normalized)
    if land_match:
        try:
            value = float(land_match.group(1))
        except ValueError:
            value = 0.0
        unit = land_match.group(2)
        entities.land_acres = round(value / 100, 2) if unit in {"சென்ட்", "cents"} else value

    if any(word in normalized for word in _INCOME_WORDS):
        candidates = list(entities.money_amounts)
        candidates.extend(int(raw) for raw in _STANDALONE_NUMBER.findall(normalized))
        if candidates:
            entities.monthly_income = max(candidates)

    if any(
        word in normalized
        for word in ("பெண்", "மகளிர்", "விதவை", "woman", "women", "female", "girl", "widow", "vidhavai", "penn", "ponnu")
    ):
        entities.gender = "female"
    elif re.search(r"\b(?:male|man|boy|aan|aambala|aambalai)\b", normalized):
        entities.gender = "male"

    tokens = set(tokenize(normalized))

    for term, level in sorted(_EDUCATION_MAP.items(), key=lambda item: len(item[0]), reverse=True):
        if _contains_term(normalized, tokens, term):
            entities.education = level
            break

    for district in sorted(_DISTRICTS, key=len, reverse=True):
        if _contains_term(normalized, tokens, district.lower()):
            entities.district = district
            break

    for crop in sorted(_CROPS, key=len, reverse=True):
        if _contains_term(normalized, tokens, crop):
            entities.crop = crop
            break

    for purpose, terms in _LOAN_PURPOSE.items():
        if any(term in normalized for term in terms):
            entities.loan_purpose = purpose
            break

    for occupation, terms in _OCCUPATION_MAP.items():
        if any(term in normalized for term in terms):
            entities.occupation = occupation
            break

    if any(term in normalized for term in ("விதவை", "widow", "widowed", "vidhavai")):
        entities.marital_status = "widow"
    elif any(term in normalized for term in ("திருமணமாகவில்லை", "unmarried", "single woman")):
        entities.marital_status = "unmarried"
    elif any(term in normalized for term in ("திருமணம் ஆகி", "married", "திருமணமான")):
        entities.marital_status = "married"

    return entities
