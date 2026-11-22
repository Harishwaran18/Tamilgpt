"""Scheme eligibility scoring and discovery."""

from __future__ import annotations

from dataclasses import dataclass, field

from tamilgpt.knowledge import KnowledgeBase, Scheme, get_knowledge_base
from tamilgpt.sectors import Sector
from tamilgpt.services.profile import Profile

_OCCUPATION_KEYWORDS = {
    "farmer": ("விவசாய", "farmer", "farm", "பயிர்", "crop"),
    "student": ("மாணவ", "student", "படிக்க", "college", "school"),
    "vendor": ("வியாபார", "vendor", "hawker", "கடை", "shop"),
    "artisan": ("கைவினை", "artisan", "carpenter", "தையல்", "welder", "potter"),
    "worker": ("தொழிலாள", "worker", "labour", "labor", "daily wage"),
    "entrepreneur": ("தொழில்", "business", "entrepreneur", "startup", "msme"),
    "senior": ("முதிய", "senior", "pension", "retired"),
}

# Requirements are split into traits every applicant must have (``all_of``)
# and alternatives where at least one applies (``any_of``). A trait that cannot
# be checked from the profile makes the scheme "needs info", never a match.
_SCHEME_REQUIREMENTS: dict[str, dict[str, set[str]]] = {
    "pm-kisan": {"all_of": {"farmer"}},
    "pmfby": {"all_of": {"farmer"}},
    "kcc": {"all_of": {"farmer"}},
    "pm-vishwakarma": {"any_of": {"artisan", "tailor"}},
    "pm-svanidhi": {"all_of": {"vendor"}},
    "mudra": {"any_of": {"business", "shop_owner", "entrepreneur"}},
    "standup-india": {"all_of": {"business"}},
    "nsp-scholarship": {"all_of": {"student"}},
    "magalir-urimai": {"all_of": {"women"}},
    "pudhumai-pen": {"all_of": {"student", "women"}},
    "tamil-pudhalvan": {"all_of": {"student"}},
    "moovalur-higher-education": {"all_of": {"student", "women"}},
    "naan-mudhalvan": {"all_of": {"student"}},
    "vidiyal-payanam": {"all_of": {"women"}},
    "tn-old-age-pension": {"all_of": {"senior"}},
    "tn-widow-pension": {"all_of": {"widow"}},
}

_OCCUPATION_TRAITS: dict[str, set[str]] = {
    "farmer": {"farmer"},
    "student": {"student"},
    "tailor": {"tailor", "artisan"},
    "artisan": {"artisan"},
    "carpenter": {"artisan"},
    "potter": {"artisan"},
    "welder": {"artisan"},
    "vendor": {"vendor"},
    "shop_owner": {"shop_owner", "business"},
    "business": {"business", "entrepreneur"},
    "entrepreneur": {"entrepreneur", "business"},
    "worker": {"worker"},
    "teacher": {"worker"},
    "nurse": {"worker"},
    "driver": {"worker"},
}

_TRAIT_DIMENSIONS: dict[str, str] = {
    "farmer": "occupation",
    "student": "occupation",
    "tailor": "occupation",
    "artisan": "occupation",
    "vendor": "occupation",
    "shop_owner": "occupation",
    "business": "occupation",
    "entrepreneur": "occupation",
    "worker": "occupation",
    "women": "gender",
    "senior": "age",
    "widow": "marital_status",
}

_DIMENSION_LABELS_TA = {
    "occupation": "தொழில்",
    "gender": "பாலினம்",
    "age": "வயது",
    "marital_status": "திருமண நிலை",
}
_DIMENSION_LABELS_EN = {
    "occupation": "occupation",
    "gender": "gender",
    "age": "age",
    "marital_status": "marital status",
}

_TARGET_LABELS_TA = {
    "farmer": "விவசாயிகள்",
    "student": "மாணவர்கள்",
    "women": "பெண்கள்",
    "senior": "மூத்த குடிமக்கள்",
    "widow": "விதவைகள்",
    "business": "தொழில் செய்பவர்கள்",
    "shop_owner": "கடை உரிமையாளர்கள்",
    "entrepreneur": "தொழில்முனைவோர்",
    "vendor": "தெரு வியாபாரிகள்",
    "artisan": "கைவினைஞர்கள்",
    "tailor": "தையலர்கள்",
}


def _profile_traits(profile: Profile) -> set[str]:
    traits: set[str] = set()
    if profile.occupation:
        key = profile.occupation.lower()
        traits |= _OCCUPATION_TRAITS.get(key, {key})
    if profile.gender == "female":
        traits.add("women")
    if profile.age is not None and profile.age >= 60:
        traits.add("senior")
    if profile.marital_status:
        status = profile.marital_status.lower()
        traits.add("widow" if status in {"widow", "widowed", "விதவை"} else status)
    return traits


def _known_dimensions(profile: Profile) -> set[str]:
    dimensions: set[str] = set()
    if profile.occupation:
        dimensions.add("occupation")
    if profile.gender:
        dimensions.add("gender")
    if profile.age is not None:
        dimensions.add("age")
    if profile.marital_status:
        dimensions.add("marital_status")
    return dimensions


@dataclass(slots=True)
class SchemeMatch:
    scheme: Scheme
    score: float
    eligible: bool
    reasons_ta: list[str] = field(default_factory=list)
    reasons_en: list[str] = field(default_factory=list)
    missing_ta: list[str] = field(default_factory=list)
    missing_en: list[str] = field(default_factory=list)

    def to_dict(self, language: str = "ta") -> dict[str, object]:
        scheme = self.scheme
        return {
            "id": scheme.id,
            "name": scheme.name_ta if language == "ta" else scheme.name_en,
            "name_ta": scheme.name_ta,
            "name_en": scheme.name_en,
            "category": scheme.category.value,
            "summary": scheme.summary_ta if language == "ta" else scheme.summary_en,
            "benefits": scheme.benefits_ta if language == "ta" else scheme.benefits_en,
            "eligibility": scheme.eligibility_ta if language == "ta" else scheme.eligibility_en,
            "documents": list(scheme.documents),
            "apply_url": scheme.apply_url,
            "source_name": scheme.source_name,
            "source_url": scheme.source_url,
            "score": round(self.score, 3),
            "eligible": self.eligible,
            "reasons": self.reasons_ta if language == "ta" else self.reasons_en,
            "missing": self.missing_ta if language == "ta" else self.missing_en,
            "updated": scheme.updated,
        }


def evaluate_scheme(scheme: Scheme, profile: Profile) -> SchemeMatch:
    score = 0.5
    eligible = True
    reasons_ta: list[str] = []
    reasons_en: list[str] = []
    missing_ta: list[str] = []
    missing_en: list[str] = []

    if scheme.min_age is not None or scheme.max_age is not None:
        if profile.age is None:
            missing_ta.append("வயது")
            missing_en.append("age")
        else:
            age_ok = (scheme.min_age is None or profile.age >= scheme.min_age) and (
                scheme.max_age is None or profile.age <= scheme.max_age
            )
            if age_ok:
                score += 0.2
                reasons_ta.append("வயது தகுதிக்குள் உள்ளது")
                reasons_en.append("age is within the eligible range")
            else:
                eligible = False
                score -= 0.45
                reasons_ta.append("வயது தகுதிக்கு வெளியே உள்ளது")
                reasons_en.append("age is outside the eligible range")

    if scheme.gender:
        if profile.gender is None:
            missing_ta.append("பாலினம்")
            missing_en.append("gender")
        elif profile.gender.lower() == scheme.gender.lower():
            score += 0.15
            reasons_ta.append("பாலினம் பொருந்துகிறது")
            reasons_en.append("gender matches")
        else:
            eligible = False
            score -= 0.45
            reasons_ta.append("இந்தத் திட்டம் குறிப்பிட்ட பாலினத்திற்கானது")
            reasons_en.append("this scheme is limited to a specific gender")

    income = profile.effective_annual_income
    if scheme.max_income is not None:
        if income is None:
            missing_ta.append("ஆண்டு வருமானம்")
            missing_en.append("annual income")
        elif income <= scheme.max_income:
            score += 0.2
            reasons_ta.append("வருமான வரம்பிற்குள் உள்ளது")
            reasons_en.append("income is within the limit")
        else:
            eligible = False
            score -= 0.45
            reasons_ta.append("வருமானம் வரம்பை மீறுகிறது")
            reasons_en.append("income exceeds the limit")

    requirements = _SCHEME_REQUIREMENTS.get(scheme.id, {})
    if requirements:
        traits = _profile_traits(profile)
        known = _known_dimensions(profile)

        def status(trait: str) -> str:
            if trait in traits:
                return "met"
            dimension = _TRAIT_DIMENSIONS.get(trait)
            return "failed" if dimension in known else "unknown"

        failed = False
        missing: set[str] = set()
        for trait in requirements.get("all_of", set()):
            result = status(trait)
            if result == "failed":
                failed = True
                break
            if result == "unknown":
                missing.add(_TRAIT_DIMENSIONS[trait])

        if not failed:
            any_of = requirements.get("any_of", set())
            results = {trait: status(trait) for trait in any_of}
            if any_of and "met" not in results.values():
                if all(result == "failed" for result in results.values()):
                    failed = True
                else:
                    missing.update(
                        _TRAIT_DIMENSIONS[trait]
                        for trait, result in results.items()
                        if result == "unknown"
                    )

        if failed:
            eligible = False
            score -= 0.4
            targets = requirements.get("all_of") or requirements.get("any_of") or set()
            labels = ", ".join(
                _TARGET_LABELS_TA.get(target, target) for target in sorted(targets)
            )
            reasons_ta.append(f"இந்தத் திட்டம் {labels} பிரிவினருக்கானது")
            reasons_en.append(f"this scheme is meant for: {', '.join(sorted(targets))}")
        elif missing:
            eligible = False
            missing_ta.extend(_DIMENSION_LABELS_TA[item] for item in sorted(missing))
            missing_en.extend(_DIMENSION_LABELS_EN[item] for item in sorted(missing))
            reasons_ta.append("தகுதியை உறுதிசெய்ய கூடுதல் தகவல் தேவை")
            reasons_en.append("more profile information is needed to confirm eligibility")
        else:
            score += 0.15
            reasons_ta.append("உங்கள் பிரிவுக்குப் பொருந்துகிறது")
            reasons_en.append("matches your citizen category")

    if profile.occupation:
        terms = _OCCUPATION_KEYWORDS.get(profile.occupation.lower(), ())
        haystack = scheme.search_text().lower()
        if any(term in haystack for term in terms):
            score += 0.1
            reasons_ta.append("உங்கள் தொழிலுக்கு பொருத்தமானது")
            reasons_en.append("relevant to your occupation")

    if profile.land_acres and scheme.category is Sector.AGRICULTURE:
        score += 0.05
        reasons_ta.append("விவசாயத் தகுதி உள்ளது")
        reasons_en.append("agriculture eligibility applies")

    score = max(0.0, min(1.0, score))
    if score < 0.55:
        eligible = False
    return SchemeMatch(
        scheme=scheme,
        score=score,
        eligible=eligible,
        reasons_ta=list(dict.fromkeys(reasons_ta)),
        reasons_en=list(dict.fromkeys(reasons_en)),
        missing_ta=list(dict.fromkeys(missing_ta)),
        missing_en=list(dict.fromkeys(missing_en)),
    )


def match_schemes(
    profile: Profile,
    *,
    kb: KnowledgeBase | None = None,
    limit: int = 10,
    eligible_only: bool = False,
) -> list[SchemeMatch]:
    base = kb or get_knowledge_base()
    matches = [evaluate_scheme(scheme, profile) for scheme in base.schemes]
    if eligible_only:
        matches = [match for match in matches if match.eligible]
    matches.sort(key=lambda match: (match.eligible, match.score), reverse=True)
    return matches[:limit]


def find_schemes(
    query: str = "",
    *,
    category: str | None = None,
    kb: KnowledgeBase | None = None,
    limit: int = 20,
) -> list[Scheme]:
    base = kb or get_knowledge_base()
    if query.strip():
        hits = base.search_schemes(query, top_k=limit)
        schemes = [hit.item for hit in hits]
    else:
        schemes = list(base.schemes)
    if category:
        schemes = [scheme for scheme in schemes if scheme.category.value == category]
    return schemes[:limit]
