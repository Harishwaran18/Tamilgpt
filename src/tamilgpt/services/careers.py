"""Career matching from education, interests and skills."""

from __future__ import annotations

from dataclasses import dataclass, field

from tamilgpt.knowledge import Career, KnowledgeBase, get_knowledge_base
from tamilgpt.services.profile import Profile

_EDUCATION_RANK = {
    "no formal schooling": 0,
    "10th": 1,
    "12th": 2,
    "iti": 2,
    "diploma": 3,
    "degree": 4,
    "engineering": 4,
    "nursing": 4,
    "postgraduate": 5,
    "medical": 5,
}

_EDUCATION_KEYWORDS = {
    "degree": {"b.com", "commerce", "any degree"},
    "12th": {"12th", "higher secondary"},
    "10th": {"10th", "sslc"},
    "iti": {"iti"},
    "diploma": {"diploma", "polytechnic"},
    "engineering": {"engineering", "b.e", "b.tech"},
    "postgraduate": {"postgraduate", "masters", "m.a", "m.sc", "m.com"},
    "nursing": {"nursing", "gnm", "anm"},
    "medical": {"mbbs", "medical"},
}

_INTEREST_ALIASES = {
    "technology": {"technology", "computer", "tech", "கணினி", "தொழில்நுட்பம்"},
    "math": {"math", "maths", "numbers", "கணிதம்", "எண்"},
    "science": {"science", "அறிவியல்", "biology", "physics", "chemistry"},
    "helping": {"helping", "help", "service", "உதவி", "சேவை"},
    "people": {"people", "communication", "மக்கள்", "மனிதர்"},
    "health": {"health", "medical", "மருத்துவம்", "உடல்நலம்"},
    "creative": {"creative", "art", "design", "படைப்பு", "கலை"},
    "hands_on": {"hands on", "practical", "கைவேலை", "நேரடி"},
    "business": {"business", "money", "தொழில்", "வணிகம்", "பணம்"},
    "organization": {"organization", "organising", "ஒழுங்கு", "நிர்வாகம்"},
    "detail": {"detail", "accuracy", "நுட்பம்", "துல்லியம்"},
    "fitness": {"fitness", "sport", "உடற்பயிற்சி", "விளையாட்டு"},
    "public service": {"public service", "government", "அரசு", "பொது சேவை"},
    "policy": {"policy", "administration", "கொள்கை", "நிர்வாகம்"},
    "leadership": {"leadership", "leader", "தலைமை"},
    "driving": {"driving", "vehicle", "ஓட்டுதல்", "வாகனம்"},
    "travel": {"travel", "பயணம்"},
    "risk": {"risk", "ஆபத்து", "சவால்"},
}


def _canonical_interests(values: tuple[str, ...]) -> set[str]:
    result: set[str] = set()
    lowered = [value.strip().lower() for value in values]
    for canonical, aliases in _INTEREST_ALIASES.items():
        if any(value in aliases for value in lowered):
            result.add(canonical)
    return result


@dataclass(slots=True)
class CareerMatch:
    career: Career
    score: float
    reasons_ta: list[str] = field(default_factory=list)
    reasons_en: list[str] = field(default_factory=list)

    def to_dict(self, language: str = "ta") -> dict[str, object]:
        career = self.career
        return {
            "id": career.id,
            "title": career.title_ta if language == "ta" else career.title_en,
            "title_ta": career.title_ta,
            "title_en": career.title_en,
            "sector": career.sector.value,
            "summary": career.summary_ta if language == "ta" else career.summary_en,
            "education": list(career.education),
            "skills": list(career.skills),
            "salary_min": career.salary_min,
            "salary_max": career.salary_max,
            "path": career.path_ta if language == "ta" else career.path_en,
            "exams": list(career.exams),
            "score": round(self.score, 3),
            "reasons": self.reasons_ta if language == "ta" else self.reasons_en,
        }


def match_careers(
    profile: Profile,
    *,
    kb: KnowledgeBase | None = None,
    limit: int = 6,
) -> list[CareerMatch]:
    base = kb or get_knowledge_base()
    interests = _canonical_interests(profile.interests)
    skills = {skill.strip().lower() for skill in profile.skills}
    profile_rank = _EDUCATION_RANK.get((profile.education or "").lower())

    matches: list[CareerMatch] = []
    for career in base.careers:
        score = 0.2
        reasons_ta: list[str] = []
        reasons_en: list[str] = []

        overlap = interests & set(career.interests)
        if overlap:
            score += 0.5 * len(overlap) / max(1, len(career.interests))
            reasons_ta.append("உங்கள் ஆர்வத்துடன் பொருந்துகிறது")
            reasons_en.append("matches your interests")

        skill_overlap = skills & {skill.lower() for skill in career.skills}
        if skill_overlap:
            score += 0.2 * len(skill_overlap) / max(1, len(career.skills))
            reasons_ta.append("உங்கள் திறன்களுடன் பொருந்துகிறது")
            reasons_en.append("matches your skills")

        if profile_rank is not None:
            required = min(
                (_EDUCATION_RANK.get(level.lower(), 0) for level in career.education),
                default=0,
            )
            if profile_rank >= required:
                score += 0.2
                reasons_ta.append("உங்கள் கல்வித் தகுதி போதுமானது")
                reasons_en.append("your education level qualifies")
            else:
                score -= 0.25
                reasons_ta.append("கூடுதல் கல்வித் தகுதி தேவைப்படலாம்")
                reasons_en.append("a higher education level may be needed")

        if profile.education:
            education = profile.education.lower()
            education_terms = _EDUCATION_KEYWORDS.get(education, set()) | {education}
            if any(
                term in keyword.lower()
                for keyword in career.keywords
                for term in education_terms
                if len(term) >= 3
            ):
                score += 0.15
                reasons_ta.append("உங்கள் படிப்புக்கு நேரடித் தொடர்பு உள்ளது")
                reasons_en.append("directly related to your field of study")

        score = max(0.0, min(1.0, score))
        matches.append(
            CareerMatch(
                career=career,
                score=score,
                reasons_ta=reasons_ta,
                reasons_en=reasons_en,
            )
        )

    matches.sort(key=lambda match: match.score, reverse=True)
    return matches[:limit]


def find_careers(
    query: str = "", *, kb: KnowledgeBase | None = None, limit: int = 20
) -> list[Career]:
    base = kb or get_knowledge_base()
    if not query.strip():
        return list(base.careers)[:limit]
    return [hit.item for hit in base.search_careers(query, top_k=limit)]
