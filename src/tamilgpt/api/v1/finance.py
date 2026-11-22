"""Deterministic finance calculators."""

from __future__ import annotations

from fastapi import APIRouter

from tamilgpt.api.schemas import (
    AffordabilityRequest,
    EmiRequest,
    LoanCompareRequest,
    SavingsRequest,
)
from tamilgpt.services.finance import (
    LoanOffer,
    affordability,
    calculate_emi,
    compare_loans,
    savings_goal,
)

router = APIRouter(prefix="/finance", tags=["finance"])


@router.post("/emi", summary="Calculate a loan EMI")
def emi(payload: EmiRequest) -> dict[str, object]:
    return calculate_emi(payload.principal, payload.annual_rate, payload.months).to_dict()


@router.post("/affordability", summary="Estimate a safe EMI and maximum loan")
def afford(payload: AffordabilityRequest) -> dict[str, object]:
    return affordability(
        payload.monthly_income,
        payload.existing_emi,
        annual_rate=payload.annual_rate,
        months=payload.months,
        emi_ratio=payload.emi_ratio,
    ).to_dict()


@router.post("/savings", summary="Monthly saving needed for a goal")
def savings(payload: SavingsRequest) -> dict[str, object]:
    return savings_goal(payload.target, payload.months, payload.annual_return).to_dict()


@router.post("/compare-loans", summary="Compare loan offers by total cost")
def compare(payload: LoanCompareRequest) -> list[dict[str, object]]:
    offers = [
        LoanOffer(
            name=offer.name,
            annual_rate=offer.annual_rate,
            months=offer.months,
            processing_fee=offer.processing_fee,
        )
        for offer in payload.offers
    ]
    return [item.to_dict() for item in compare_loans(payload.principal, offers)]
