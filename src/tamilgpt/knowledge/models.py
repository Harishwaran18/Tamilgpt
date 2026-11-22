"""Typed records for every knowledge-base dataset."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from tamilgpt.sectors import Sector


def _require(data: Mapping[str, Any], key: str) -> Any:
    if key not in data or data[key] in (None, ""):
        raise ValueError(f"missing required field '{key}'")
    return data[key]


def _str_tuple(data: Mapping[str, Any], key: str) -> tuple[str, ...]:
    value = data.get(key) or []
    if not isinstance(value, list):
        raise ValueError(f"'{key}' must be a list")
    return tuple(str(item) for item in value)


@dataclass(frozen=True, slots=True)
class KnowledgeDoc:
    id: str
    sector: Sector
    title_ta: str
    title_en: str
    body_ta: str
    body_en: str
    tags: tuple[str, ...] = ()
    source_name: str | None = None
    source_url: str | None = None
    updated: str | None = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> KnowledgeDoc:
        return cls(
            id=str(_require(data, "id")),
            sector=Sector(str(_require(data, "sector"))),
            title_ta=str(_require(data, "title_ta")),
            title_en=str(_require(data, "title_en")),
            body_ta=str(_require(data, "body_ta")),
            body_en=str(_require(data, "body_en")),
            tags=_str_tuple(data, "tags"),
            source_name=data.get("source_name"),
            source_url=data.get("source_url"),
            updated=data.get("updated"),
        )

    def search_text(self) -> str:
        return " ".join(
            [self.title_ta, self.body_ta, " ".join(self.tags), self.title_en, self.body_en]
        )


@dataclass(frozen=True, slots=True)
class Scheme:
    id: str
    name_ta: str
    name_en: str
    category: Sector
    summary_ta: str
    summary_en: str
    benefits_ta: str
    benefits_en: str
    eligibility_ta: str
    eligibility_en: str
    documents: tuple[str, ...] = ()
    apply_url: str | None = None
    source_name: str | None = None
    source_url: str | None = None
    min_age: int | None = None
    max_age: int | None = None
    max_income: int | None = None
    gender: str | None = None
    keywords: tuple[str, ...] = ()
    updated: str | None = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Scheme:
        return cls(
            id=str(_require(data, "id")),
            name_ta=str(_require(data, "name_ta")),
            name_en=str(_require(data, "name_en")),
            category=Sector(str(_require(data, "category"))),
            summary_ta=str(_require(data, "summary_ta")),
            summary_en=str(_require(data, "summary_en")),
            benefits_ta=str(_require(data, "benefits_ta")),
            benefits_en=str(_require(data, "benefits_en")),
            eligibility_ta=str(_require(data, "eligibility_ta")),
            eligibility_en=str(_require(data, "eligibility_en")),
            documents=_str_tuple(data, "documents"),
            apply_url=data.get("apply_url"),
            source_name=data.get("source_name"),
            source_url=data.get("source_url"),
            min_age=data.get("min_age"),
            max_age=data.get("max_age"),
            max_income=data.get("max_income"),
            gender=data.get("gender"),
            keywords=_str_tuple(data, "keywords"),
            updated=data.get("updated"),
        )

    def search_text(self) -> str:
        return " ".join(
            [
                self.name_ta, self.name_en, self.summary_ta, self.summary_en,
                self.benefits_ta, self.benefits_en, self.eligibility_ta,
                self.eligibility_en, " ".join(self.keywords),
            ]
        )


@dataclass(frozen=True, slots=True)
class Career:
    id: str
    title_ta: str
    title_en: str
    sector: Sector
    summary_ta: str
    summary_en: str
    education: tuple[str, ...]
    interests: tuple[str, ...]
    skills: tuple[str, ...]
    salary_min: int
    salary_max: int
    path_ta: str
    path_en: str
    exams: tuple[str, ...] = ()
    keywords: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Career:
        return cls(
            id=str(_require(data, "id")),
            title_ta=str(_require(data, "title_ta")),
            title_en=str(_require(data, "title_en")),
            sector=Sector(str(_require(data, "sector"))),
            summary_ta=str(_require(data, "summary_ta")),
            summary_en=str(_require(data, "summary_en")),
            education=_str_tuple(data, "education"),
            interests=_str_tuple(data, "interests"),
            skills=_str_tuple(data, "skills"),
            salary_min=int(_require(data, "salary_min")),
            salary_max=int(_require(data, "salary_max")),
            path_ta=str(_require(data, "path_ta")),
            path_en=str(_require(data, "path_en")),
            exams=_str_tuple(data, "exams"),
            keywords=_str_tuple(data, "keywords"),
        )

    def search_text(self) -> str:
        return " ".join(
            [
                self.title_ta, self.title_en, self.summary_ta, self.summary_en,
                " ".join(self.interests), " ".join(self.skills),
                " ".join(self.education), " ".join(self.keywords),
            ]
        )


@dataclass(frozen=True, slots=True)
class HealthTopic:
    id: str
    title_ta: str
    title_en: str
    keywords: tuple[str, ...]
    symptoms_ta: tuple[str, ...]
    symptoms_en: tuple[str, ...]
    red_flags_ta: tuple[str, ...]
    red_flags_en: tuple[str, ...]
    advice_ta: str
    advice_en: str
    specialist_ta: str
    specialist_en: str
    source_url: str | None = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> HealthTopic:
        return cls(
            id=str(_require(data, "id")),
            title_ta=str(_require(data, "title_ta")),
            title_en=str(_require(data, "title_en")),
            keywords=_str_tuple(data, "keywords"),
            symptoms_ta=_str_tuple(data, "symptoms_ta"),
            symptoms_en=_str_tuple(data, "symptoms_en"),
            red_flags_ta=_str_tuple(data, "red_flags_ta"),
            red_flags_en=_str_tuple(data, "red_flags_en"),
            advice_ta=str(_require(data, "advice_ta")),
            advice_en=str(_require(data, "advice_en")),
            specialist_ta=str(_require(data, "specialist_ta")),
            specialist_en=str(_require(data, "specialist_en")),
            source_url=data.get("source_url"),
        )

    def search_text(self) -> str:
        return " ".join(
            [
                self.title_ta, self.title_en, " ".join(self.keywords),
                " ".join(self.symptoms_ta), " ".join(self.symptoms_en),
            ]
        )


@dataclass(frozen=True, slots=True)
class Service:
    id: str
    type: str
    name_ta: str
    name_en: str
    icon: str
    description_ta: str
    description_en: str
    helpline: str | None
    website: str | None
    overpass_tags: tuple[str, ...] = ()
    keywords: tuple[str, ...] = ()

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Service:
        return cls(
            id=str(_require(data, "id")),
            type=str(_require(data, "type")),
            name_ta=str(_require(data, "name_ta")),
            name_en=str(_require(data, "name_en")),
            icon=str(data.get("icon", "📍")),
            description_ta=str(_require(data, "description_ta")),
            description_en=str(_require(data, "description_en")),
            helpline=data.get("helpline"),
            website=data.get("website"),
            overpass_tags=_str_tuple(data, "overpass_tags"),
            keywords=_str_tuple(data, "keywords"),
        )


@dataclass(frozen=True, slots=True)
class Helpline:
    number: str
    name_ta: str
    name_en: str
    category: str
    description_ta: str
    description_en: str
    available: str = "24x7"

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Helpline:
        return cls(
            number=str(_require(data, "number")),
            name_ta=str(_require(data, "name_ta")),
            name_en=str(_require(data, "name_en")),
            category=str(_require(data, "category")),
            description_ta=str(_require(data, "description_ta")),
            description_en=str(_require(data, "description_en")),
            available=str(data.get("available", "24x7")),
        )


@dataclass(slots=True)
class KnowledgeStats:
    documents: int = 0
    schemes: int = 0
    careers: int = 0
    health_topics: int = 0
    services: int = 0
    helplines: int = 0
    sectors: tuple[str, ...] = field(default_factory=tuple)
