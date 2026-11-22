"""The ten citizen-support sectors that TamilGPT covers.

This module is the single source of truth for sector identifiers, bilingual
labels, and the vocabulary used by the intent classifier and the knowledge base.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class Sector(StrEnum):
    AGRICULTURE = "agriculture"
    EDUCATION = "education"
    EMPLOYMENT = "employment"
    BUSINESS = "business"
    WOMEN_ELDERLY = "women_elderly"
    SCHEMES = "schemes"
    LEGAL = "legal"
    HEALTHCARE = "healthcare"
    WELLNESS = "wellness"
    FINANCE = "finance"
    GENERAL = "general"


@dataclass(frozen=True, slots=True)
class SectorInfo:
    id: Sector
    ta: str
    en: str
    icon: str
    summary_ta: str
    summary_en: str
    keywords: tuple[str, ...] = field(default_factory=tuple)
    questions_ta: tuple[str, ...] = field(default_factory=tuple)
    questions_en: tuple[str, ...] = field(default_factory=tuple)


SECTORS: dict[Sector, SectorInfo] = {
    Sector.AGRICULTURE: SectorInfo(
        id=Sector.AGRICULTURE,
        ta="விவசாயம்",
        en="Agriculture",
        icon="🌾",
        summary_ta="பயிர் தேர்வு, உரம், பூச்சி கட்டுப்பாடு, வானிலை, விவசாயக் கடன் மற்றும் மானியங்கள்.",
        summary_en="Crop choice, fertiliser, pest control, weather, farm credit and subsidies.",
        keywords=(
            "விவசாயம்", "விவசாயி", "உழவர்", "பயிர்", "நெல்", "கரும்பு", "மக்காச்சோளம்",
            "பருத்தி", "காய்கறி", "தென்னை", "வாழை", "மண்", "உரம்", "பூச்சி", "நோய்",
            "நீர்ப்பாசனம்", "விதை", "அறுவடை", "மழை", "வானிலை", "கால்நடை", "மாடு",
            "ஆடு", "கோழி", "மீன்", "தேன்", "farm", "farmer", "agriculture", "crop",
            "paddy", "rice", "sugarcane", "maize", "cotton", "vegetable", "coconut",
            "banana", "soil", "fertiliser", "fertilizer", "pest", "irrigation", "seed",
            "harvest", "weather", "rain", "cattle", "cow", "goat", "poultry", "fish",
            "vivasayam", "vivasaayam", "payir", "nel", "urum", "poochi", "mazhai",
        ),
        questions_ta=(
            "நெல்லுக்கு எந்த உரம் சரி?",
            "விவசாயக் கடன் எப்படி பெறுவது?",
            "பயிர் காப்பீட்டுத் திட்டம் என்ன?",
        ),
        questions_en=(
            "Which fertiliser is right for paddy?",
            "How do I get a farm loan?",
            "What is crop insurance?",
        ),
    ),
    Sector.EDUCATION: SectorInfo(
        id=Sector.EDUCATION,
        ta="கல்வி",
        en="Education",
        icon="🎓",
        summary_ta="பள்ளி சேர்க்கை, கல்லூரி தேர்வு, கல்விக் கடன், உதவித்தொகை மற்றும் திறன் பயிற்சி.",
        summary_en="School admission, college choice, education loans, scholarships and skilling.",
        keywords=(
            "கல்வி", "பள்ளி", "கல்லூரி", "படிப்பு", "மாணவர்", "மாணவி", "தேர்வு",
            "சேர்க்கை", "உதவித்தொகை", "கல்விக் கடன்", "பாடம்", "இன்ஜினியரிங்",
            "மருத்துவம்", "டிப்ளமோ", "ஐடிஐ", "பல்கலைக்கழகம்", "மேல்நிலை", "பத்தாம் வகுப்பு",
            "பன்னிரண்டாம் வகுப்பு", "வகுப்பு", "படிக்க", "12ஆம் வகுப்பு", "10ஆம் வகுப்பு",
            "நீட்", "கேட்", "scholarship", "education", "school",
            "college", "student", "exam", "admission", "course", "degree", "engineering",
            "medical", "diploma", "iti", "university", "neet", "gate", "study", "padipu",
            "kalvi", "palli", "kalluri", "thErvu", "thervu", "scholarship",
        ),
        questions_ta=(
            "12ஆம் வகுப்புக்குப் பிறகு என்ன படிக்கலாம்?",
            "கல்விக் கடன் எப்படி வாங்குவது?",
            "எந்த உதவித்தொகை எனக்குக் கிடைக்கும்?",
        ),
        questions_en=(
            "What can I study after class 12?",
            "How do I get an education loan?",
            "Which scholarship can I apply for?",
        ),
    ),
    Sector.EMPLOYMENT: SectorInfo(
        id=Sector.EMPLOYMENT,
        ta="வேலைவாய்ப்பு",
        en="Employment",
        icon="💼",
        summary_ta="வேலை தேடல், திறன் பயிற்சி, அரசு வேலை, நேர்காணல் தயாரிப்பு மற்றும் சுயதொழில்.",
        summary_en="Job search, skilling, government jobs, interview prep and self-employment.",
        keywords=(
            "வேலை", "வேலைவாய்ப்பு", "உத்யோகம்", "நேர்காணல்", "சம்பளம்", "திறன்",
            "பயிற்சி", "அரசு வேலை", "டிஎன்பிஎஸ்சி", "டிஆர்பி",
            "ரயில்வே", "வங்கி", "காவல்", "ஆசிரியர்", "சுயதொழில்", "ரெஸ்யூம்",
            "job", "employment", "career", "interview", "salary", "skill", "training",
            "government job", "tnpsc", "trb", "railway", "bank", "police", "teacher",
            "resume", "cv", "velai", "vElai", "udhyogam", "sambalam", "thiran",
            "nErkANal", "nerkanal", "career guidance",
        ),
        questions_ta=(
            "எனக்கு ஏற்ற வேலை எது?",
            "TNPSC தேர்வுக்கு எப்படி தயாராகலாம்?",
            "நேர்காணலில் என்ன பேச வேண்டும்?",
        ),
        questions_en=(
            "Which job suits me?",
            "How do I prepare for TNPSC?",
            "What should I say in an interview?",
        ),
    ),
    Sector.BUSINESS: SectorInfo(
        id=Sector.BUSINESS,
        ta="தொழில் & கடன்",
        en="Business & Loans",
        icon="🏪",
        summary_ta="சிறு தொழில் தொடங்குதல், கடன் தேர்வு, முதலீடு மற்றும் அரசு உதவி.",
        summary_en="Starting a small business, choosing credit, investment and government support.",
        keywords=(
            "தொழில்", "வியாபாரம்", "கடை", "நிறுவனம்", "கடன்", "முதலீடு", "லாபம்",
            "வணிகம்", "எம்எஸ்எம்இ", "ஸ்டார்ட்அப்", "உரிமை", "கூட்டாண்மை", "விற்பனை",
            "business", "shop", "company", "loan", "credit", "investment", "profit",
            "msme", "startup", "franchise", "partnership", "sales", "vyabaram",
            "thozhil", "kadan", "kadai", "mudhal", "mudhaleedu",
        ),
        questions_ta=(
            "சிறு தொழிலுக்கு எவ்வளவு கடன் கிடைக்கும்?",
            "கடை தொடங்க என்ன உரிமம் வேண்டும்?",
            "Mudra கடன் எப்படி விண்ணப்பிப்பது?",
        ),
        questions_en=(
            "How much loan can I get for a small business?",
            "What licence do I need to open a shop?",
            "How do I apply for a Mudra loan?",
        ),
    ),
    Sector.WOMEN_ELDERLY: SectorInfo(
        id=Sector.WOMEN_ELDERLY,
        ta="பெண்கள் & முதியோர்",
        en="Women & Elderly",
        icon="👩‍👧",
        summary_ta="பெண்கள் நலத்திட்டங்கள், மகப்பேறு உதவி, முதியோர் ஓய்வூதியம் மற்றும் பாதுகாப்பு.",
        summary_en="Women's welfare schemes, maternity support, senior pensions and safety.",
        keywords=(
            "பெண்", "பெண்கள்", "மகளிர்", "மகப்பேறு", "கர்ப்பம்", "முதியோர்",
            "முதியவர்", "ஓய்வூதியம்", "விதவை", "ஆதரவற்ற", "குழந்தை", "பாதுகாப்பு",
            "women", "woman", "maternity", "pregnancy", "elderly", "senior citizen",
            "pension", "widow", "girl", "child safety", "magalir", "pen", "pengal",
            "mudhiyor", "oyvuudhiyam", "vidhavai", "karppam",
        ),
        questions_ta=(
            "மகளிர் உரிமைத் தொகை யாருக்குக் கிடைக்கும்?",
            "முதியோர் ஓய்வூதியம் எப்படி பெறுவது?",
            "பெண்களுக்கான கல்வி உதவி என்ன?",
        ),
        questions_en=(
            "Who is eligible for the women's entitlement scheme?",
            "How do I get a senior citizen pension?",
            "What education support exists for girls?",
        ),
    ),
    Sector.SCHEMES: SectorInfo(
        id=Sector.SCHEMES,
        ta="அரசு திட்டங்கள்",
        en="Government Schemes",
        icon="📢",
        summary_ta="மத்திய & மாநில அரசு நலத்திட்டங்கள், தகுதி, ஆவணங்கள் மற்றும் விண்ணப்ப முறை.",
        summary_en="Central and state welfare schemes, eligibility, documents and how to apply.",
        keywords=(
            "திட்டம்", "திட்டங்கள்", "அரசு", "மானியம்", "நலத்திட்டம்", "உதவி",
            "சலுகை", "ரேஷன்", "அட்டை", "ஆதார்", "சான்று", "பட்டா", "விண்ணப்பம்",
            "scheme", "schemes", "government", "subsidy", "welfare", "benefit",
            "ration", "aadhaar", "certificate", "patta", "apply", "application",
            "thittam", "thittangal", "arasu", "maniyam", "nala thittam", "udhavi",
        ),
        questions_ta=(
            "எனக்கு எந்த அரசு திட்டங்கள் கிடைக்கும்?",
            "ரேஷன் அட்டை எப்படி விண்ணப்பிப்பது?",
            "தகுதி சான்றிதழ் எப்படி பெறுவது?",
        ),
        questions_en=(
            "Which government schemes am I eligible for?",
            "How do I apply for a ration card?",
            "How do I get a community certificate?",
        ),
    ),
    Sector.LEGAL: SectorInfo(
        id=Sector.LEGAL,
        ta="சட்ட உதவி",
        en="Legal Help",
        icon="⚖️",
        summary_ta="இலவச சட்ட உதவி, நுகர்வோர் பாதுகாப்பு, சொத்து, குடும்பம் மற்றும் தொழிலாளர் உரிமைகள்.",
        summary_en="Free legal aid, consumer protection, property, family and labour rights.",
        keywords=(
            "சட்டம்", "வழக்கு", "நீதிமன்றம்", "வக்கீல்", "வழக்கறிஞர்", "எஃப்ஐஆர்",
            "போலீஸ்", "புகார்", "நுகர்வோர்", "சொத்து", "பட்டா", "வாரிசு", "விவாகரத்து",
            "உரிமை", "தொழிலாளர்", "law", "legal", "case", "court", "lawyer", "advocate",
            "fir", "police", "complaint", "consumer", "property", "inheritance",
            "divorce", "rights", "labour", "labor", "sattam", "vazhakku", "vakkil",
            "pugar", "urimai",
        ),
        questions_ta=(
            "இலவச சட்ட உதவி எப்படி பெறுவது?",
            "நுகர்வோர் புகார் எங்கு அளிக்கலாம்?",
            "எஃப்ஐஆர் பதிவு செய்வது எப்படி?",
        ),
        questions_en=(
            "How do I get free legal aid?",
            "Where can I file a consumer complaint?",
            "How do I register an FIR?",
        ),
    ),
    Sector.HEALTHCARE: SectorInfo(
        id=Sector.HEALTHCARE,
        ta="மருத்துவம்",
        en="Healthcare",
        icon="🏥",
        summary_ta="அரசு மருத்துவமனை, மருத்துவக் காப்பீடு, அறிகுறி வழிகாட்டல் மற்றும் அவசர உதவி.",
        summary_en="Government hospitals, health insurance, symptom guidance and emergency care.",
        keywords=(
            "மருத்துவம்", "மருத்துவர்", "மருத்துவமனை", "நோய்", "காய்ச்சல்", "இருமல்",
            "வலி", "சர்க்கரை", "நீரிழிவு", "இரத்த அழுத்தம்", "மருந்து", "பரிசோதனை",
            "காப்பீடு", "அவசரம்", "ஆம்புலன்ஸ்", "108", "104", "உடல்நலம்", "சிகிச்சை",
            "health", "hospital", "doctor", "fever", "cough", "pain", "diabetes",
            "sugar", "blood pressure", "bp", "medicine", "test", "insurance",
            "emergency", "ambulance", "treatment", "maruthuvam", "maruthuvar",
            "noi", "kaichal", "vali", "sirukarai", "iru adaippu", "udanal",
        ),
        questions_ta=(
            "அரசு மருத்துவமனையில் இலவச சிகிச்சை எப்படி?",
            "காய்ச்சல் இருந்தால் என்ன செய்ய வேண்டும்?",
            "முதலமைச்சர் காப்பீட்டுத் திட்டம் என்ன?",
        ),
        questions_en=(
            "How do I get free treatment at a government hospital?",
            "What should I do if I have a fever?",
            "What is the Chief Minister's health insurance scheme?",
        ),
    ),
    Sector.WELLNESS: SectorInfo(
        id=Sector.WELLNESS,
        ta="மனநலம்",
        en="Mental Wellness",
        icon="💚",
        summary_ta="மன அழுத்தம், கவலை, தூக்கம் மற்றும் உணர்வு ஆதரவு — அவசர உதவி எண்களுடன்.",
        summary_en="Stress, anxiety, sleep and emotional support — with crisis helplines.",
        keywords=(
            "மனநலம்", "மன அழுத்தம்", "கவலை", "பயம்", "தூக்கமின்மை", "மனச்சோர்வு",
            "வேதனை", "தனிமை", "உணர்வு", "பதற்றம்", "ஆதரவு", "ஆலோசனை",
            "stress", "anxiety", "depression", "sad", "lonely", "sleep", "mental",
            "wellness", "counselling", "counseling", "panic", "emotion", "mananalam",
            "manakashtam", "kavalai", "bayam", "thookaminmai", "vedhanai", "thanimai",
        ),
        questions_ta=(
            "மன அழுத்தம் குறைய என்ன செய்யலாம்?",
            "தூக்கம் வரவில்லை, என்ன செய்வது?",
            "யாரிடம் மனநல ஆலோசனை பெறலாம்?",
        ),
        questions_en=(
            "How can I reduce stress?",
            "I cannot sleep, what should I do?",
            "Where can I get mental health counselling?",
        ),
    ),
    Sector.FINANCE: SectorInfo(
        id=Sector.FINANCE,
        ta="நிதி வழிகாட்டல்",
        en="Financial Guidance",
        icon="💰",
        summary_ta="சேமிப்பு, பட்ஜெட், கடன் திருப்பிச் செலுத்தல், காப்பீடு மற்றும் மோசடி பாதுகாப்பு.",
        summary_en="Savings, budgeting, debt repayment, insurance and fraud protection.",
        keywords=(
            "பணம்", "சேமிப்பு", "பட்ஜெட்", "வரி", "காப்பீடு", "மியூச்சுவல் ஃபண்ட்",
            "பங்கு", "தங்கம்", "வட்டி", "கடன்", "பற்று", "மோசடி", "ஏமாற்று",
            "பென்ஷன்", "நிதி", "money", "savings", "budget", "tax", "insurance",
            "mutual fund", "share", "stock", "gold", "interest", "interest rate",
            "debt", "fraud", "emi",
            "scam", "pension", "finance", "panam", "sEmippu", "semippu", "pattu",
            "vatti", "mosadi", "nidhi",
        ),
        questions_ta=(
            "மாதம் எவ்வளவு சேமிக்கலாம்?",
            "கடன் வட்டியை எப்படி குறைப்பது?",
            "நிதி மோசடியிலிருந்து எப்படி தப்பிப்பது?",
        ),
        questions_en=(
            "How much should I save each month?",
            "How do I reduce loan interest?",
            "How do I avoid financial fraud?",
        ),
    ),
    Sector.GENERAL: SectorInfo(
        id=Sector.GENERAL,
        ta="பொது உதவி",
        en="General Help",
        icon="🧭",
        summary_ta="TamilGPT பற்றிய கேள்விகள், பொது வழிகாட்டல் மற்றும் சரியான பிரிவுக்கான பரிந்துரை.",
        summary_en="Questions about TamilGPT, general guidance and sector routing.",
        keywords=("tamilgpt", "tamil gpt", "help", "உதவி", "வணக்கம்", "vanakkam"),
        questions_ta=("நீங்கள் என்ன செய்ய முடியும்?",),
        questions_en=("What can you do?",),
    ),
}


def sector_info(sector: Sector | str) -> SectorInfo:
    return SECTORS[Sector(sector)]


def all_sectors() -> list[SectorInfo]:
    return list(SECTORS.values())
