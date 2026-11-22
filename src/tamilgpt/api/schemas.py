"""Pydantic request/response models for API v1."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

LanguageCode = Literal["auto", "ta", "en"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class HistoryMessage(StrictModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ProfileIn(StrictModel):
    age: int | None = Field(default=None, ge=0, le=120)
    gender: Literal["male", "female", "other"] | None = None
    annual_income: int | None = Field(default=None, ge=0, le=1_000_000_000)
    monthly_income: int | None = Field(default=None, ge=0, le=100_000_000)
    education: str | None = Field(default=None, max_length=80)
    district: str | None = Field(default=None, max_length=80)
    occupation: str | None = Field(default=None, max_length=80)
    marital_status: Literal["married", "unmarried", "widow", "widower"] | None = None
    land_acres: float | None = Field(default=None, ge=0, le=10_000)
    family_size: int | None = Field(default=None, ge=0, le=50)
    interests: list[str] = Field(default_factory=list, max_length=20)
    skills: list[str] = Field(default_factory=list, max_length=30)


class ChatRequest(StrictModel):
    message: str = Field(min_length=1, max_length=2000)
    language: LanguageCode = "auto"
    history: list[HistoryMessage] = Field(default_factory=list, max_length=20)
    profile: ProfileIn | None = None


class CitationOut(BaseModel):
    title: str
    url: str | None = None
    source: str | None = None


class ChatResponse(BaseModel):
    reply: str
    language: str
    intent: dict[str, Any]
    citations: list[CitationOut]
    followups: list[str]
    disclaimers: list[str]
    crisis: bool
    provider: str
    grounded: bool
    request_id: str | None = None


class SchemeMatchRequest(ProfileIn):
    query: str = Field(default="", max_length=500)
    limit: int = Field(default=10, ge=1, le=30)
    eligible_only: bool = False


class CareerMatchRequest(ProfileIn):
    limit: int = Field(default=6, ge=1, le=20)


class EmiRequest(StrictModel):
    principal: float = Field(gt=0, le=1_000_000_000)
    annual_rate: float = Field(ge=0, le=60)
    months: int = Field(ge=1, le=600)


class AffordabilityRequest(StrictModel):
    monthly_income: float = Field(gt=0, le=100_000_000)
    existing_emi: float = Field(default=0, ge=0, le=100_000_000)
    annual_rate: float = Field(default=10, ge=0, le=60)
    months: int = Field(default=60, ge=1, le=600)
    emi_ratio: float = Field(default=0.4, ge=0.1, le=0.6)


class SavingsRequest(StrictModel):
    target: float = Field(gt=0, le=1_000_000_000)
    months: int = Field(ge=1, le=600)
    annual_return: float = Field(default=0, ge=0, le=40)


class LoanOfferIn(StrictModel):
    name: str = Field(min_length=1, max_length=80)
    annual_rate: float = Field(ge=0, le=60)
    months: int = Field(ge=1, le=600)
    processing_fee: float = Field(default=0, ge=0, le=10_000_000)


class LoanCompareRequest(StrictModel):
    principal: float = Field(gt=0, le=1_000_000_000)
    offers: list[LoanOfferIn] = Field(min_length=1, max_length=10)


class HealthTriageRequest(StrictModel):
    text: str = Field(min_length=2, max_length=1000)
    language: Literal["ta", "en"] = "ta"


class FeedbackRequest(StrictModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=1000)
    sector: str | None = Field(default=None, max_length=40)
    language: Literal["ta", "en"] | None = None
    message_id: str | None = Field(default=None, max_length=80)
