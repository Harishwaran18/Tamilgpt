"""A single citizen profile shared by every recommendation service."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from tamilgpt.nlp.entities import Entities


@dataclass(slots=True)
class Profile:
    age: int | None = None
    gender: str | None = None
    annual_income: int | None = None
    monthly_income: int | None = None
    education: str | None = None
    district: str | None = None
    occupation: str | None = None
    marital_status: str | None = None
    land_acres: float | None = None
    family_size: int | None = None
    interests: tuple[str, ...] = ()
    skills: tuple[str, ...] = ()

    @property
    def effective_annual_income(self) -> int | None:
        if self.annual_income is not None:
            return self.annual_income
        if self.monthly_income is not None:
            return self.monthly_income * 12
        return None

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any] | None) -> Profile:
        if not data:
            return cls()
        interests = data.get("interests") or ()
        skills = data.get("skills") or ()
        return cls(
            age=_as_int(data.get("age")),
            gender=_as_str(data.get("gender")),
            annual_income=_as_int(data.get("annual_income")),
            monthly_income=_as_int(data.get("monthly_income")),
            education=_as_str(data.get("education")),
            district=_as_str(data.get("district")),
            occupation=_as_str(data.get("occupation")),
            marital_status=_as_str(data.get("marital_status")),
            land_acres=_as_float(data.get("land_acres")),
            family_size=_as_int(data.get("family_size")),
            interests=tuple(str(item) for item in interests),
            skills=tuple(str(item) for item in skills),
        )

    @classmethod
    def from_entities(cls, entities: Entities, base: Profile | None = None) -> Profile:
        profile = base or cls()
        return cls(
            age=entities.age if entities.age is not None else profile.age,
            gender=entities.gender or profile.gender,
            annual_income=profile.annual_income,
            monthly_income=entities.monthly_income or profile.monthly_income,
            education=entities.education or profile.education,
            district=entities.district or profile.district,
            occupation=entities.occupation or profile.occupation,
            marital_status=entities.marital_status or profile.marital_status,
            land_acres=entities.land_acres if entities.land_acres is not None else profile.land_acres,
            family_size=entities.family_size or profile.family_size,
            interests=profile.interests,
            skills=profile.skills,
        )

    def merged(self, other: Profile) -> Profile:
        return Profile(
            age=other.age if other.age is not None else self.age,
            gender=other.gender or self.gender,
            annual_income=other.annual_income if other.annual_income is not None else self.annual_income,
            monthly_income=other.monthly_income if other.monthly_income is not None else self.monthly_income,
            education=other.education or self.education,
            district=other.district or self.district,
            occupation=other.occupation or self.occupation,
            marital_status=other.marital_status or self.marital_status,
            land_acres=other.land_acres if other.land_acres is not None else self.land_acres,
            family_size=other.family_size if other.family_size is not None else self.family_size,
            interests=other.interests or self.interests,
            skills=other.skills or self.skills,
        )


def _as_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _as_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None
