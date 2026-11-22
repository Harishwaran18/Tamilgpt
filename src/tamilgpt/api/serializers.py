"""Stable JSON shapes shared by the API and the static UI."""

from __future__ import annotations

from typing import Any

from tamilgpt.knowledge import Career, HealthTopic, Helpline, KnowledgeDoc, Scheme, Service


def _pick(language: str, ta: str, en: str) -> str:
    return ta if language == "ta" else en


def scheme_to_dict(scheme: Scheme, language: str = "ta") -> dict[str, Any]:
    return {
        "id": scheme.id,
        "name": _pick(language, scheme.name_ta, scheme.name_en),
        "name_ta": scheme.name_ta,
        "name_en": scheme.name_en,
        "category": scheme.category.value,
        "summary": _pick(language, scheme.summary_ta, scheme.summary_en),
        "benefits": _pick(language, scheme.benefits_ta, scheme.benefits_en),
        "eligibility": _pick(language, scheme.eligibility_ta, scheme.eligibility_en),
        "documents": list(scheme.documents),
        "apply_url": scheme.apply_url,
        "source_name": scheme.source_name,
        "source_url": scheme.source_url,
        "min_age": scheme.min_age,
        "max_age": scheme.max_age,
        "max_income": scheme.max_income,
        "gender": scheme.gender,
        "updated": scheme.updated,
    }


def career_to_dict(career: Career, language: str = "ta") -> dict[str, Any]:
    return {
        "id": career.id,
        "title": _pick(language, career.title_ta, career.title_en),
        "title_ta": career.title_ta,
        "title_en": career.title_en,
        "sector": career.sector.value,
        "summary": _pick(language, career.summary_ta, career.summary_en),
        "education": list(career.education),
        "interests": list(career.interests),
        "skills": list(career.skills),
        "salary_min": career.salary_min,
        "salary_max": career.salary_max,
        "path": _pick(language, career.path_ta, career.path_en),
        "exams": list(career.exams),
    }


def health_topic_to_dict(topic: HealthTopic, language: str = "ta") -> dict[str, Any]:
    return {
        "id": topic.id,
        "title": _pick(language, topic.title_ta, topic.title_en),
        "title_ta": topic.title_ta,
        "title_en": topic.title_en,
        "symptoms": list(topic.symptoms_ta if language == "ta" else topic.symptoms_en),
        "red_flags": list(topic.red_flags_ta if language == "ta" else topic.red_flags_en),
        "advice": _pick(language, topic.advice_ta, topic.advice_en),
        "specialist": _pick(language, topic.specialist_ta, topic.specialist_en),
        "source_url": topic.source_url,
    }


def service_to_dict(service: Service, language: str = "ta") -> dict[str, Any]:
    return {
        "id": service.id,
        "type": service.type,
        "name": _pick(language, service.name_ta, service.name_en),
        "name_ta": service.name_ta,
        "name_en": service.name_en,
        "icon": service.icon,
        "description": _pick(language, service.description_ta, service.description_en),
        "helpline": service.helpline,
        "website": service.website,
    }


def helpline_to_dict(line: Helpline, language: str = "ta") -> dict[str, Any]:
    return {
        "number": line.number,
        "name": _pick(language, line.name_ta, line.name_en),
        "name_ta": line.name_ta,
        "name_en": line.name_en,
        "category": line.category,
        "description": _pick(language, line.description_ta, line.description_en),
        "available": line.available,
    }


def document_to_dict(doc: KnowledgeDoc, language: str = "ta") -> dict[str, Any]:
    return {
        "id": doc.id,
        "sector": doc.sector.value,
        "title": _pick(language, doc.title_ta, doc.title_en),
        "title_ta": doc.title_ta,
        "title_en": doc.title_en,
        "body": _pick(language, doc.body_ta, doc.body_en),
        "tags": list(doc.tags),
        "source_name": doc.source_name,
        "source_url": doc.source_url,
        "updated": doc.updated,
    }
