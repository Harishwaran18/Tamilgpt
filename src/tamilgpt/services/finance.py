"""Deterministic, auditable finance calculators.

All money is computed with :class:`~decimal.Decimal` and rounded half-up to two
places, so results match what a bank statement would show.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal, getcontext

from tamilgpt.core.errors import ValidationFailed

getcontext().prec = 28

_CENT = Decimal("0.01")


def _q(value: Decimal) -> Decimal:
    return value.quantize(_CENT, rounding=ROUND_HALF_UP)


def _positive(name: str, value: float, *, allow_zero: bool = False) -> Decimal:
    if value is None or value < 0 or (value == 0 and not allow_zero):
        comparator = "non-negative" if allow_zero else "positive"
        raise ValidationFailed(f"{name} must be {comparator}", details={"field": name})
    return Decimal(str(value))


@dataclass(slots=True)
class YearlyRow:
    year: int
    principal_paid: float
    interest_paid: float
    balance: float


@dataclass(slots=True)
class EmiResult:
    principal: float
    annual_rate: float
    months: int
    monthly_emi: float
    total_interest: float
    total_payment: float
    yearly_schedule: list[YearlyRow] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "principal": self.principal,
            "annual_rate": self.annual_rate,
            "months": self.months,
            "monthly_emi": self.monthly_emi,
            "total_interest": self.total_interest,
            "total_payment": self.total_payment,
            "yearly_schedule": [
                {
                    "year": row.year,
                    "principal_paid": row.principal_paid,
                    "interest_paid": row.interest_paid,
                    "balance": row.balance,
                }
                for row in self.yearly_schedule
            ],
        }


def calculate_emi(principal: float, annual_rate: float, months: int) -> EmiResult:
    amount = _positive("principal", principal)
    rate = _positive("annual_rate", annual_rate, allow_zero=True)
    if months <= 0 or months > 600:
        raise ValidationFailed("months must be between 1 and 600", details={"field": "months"})

    monthly_rate = rate / Decimal(1200)
    n = Decimal(months)
    if monthly_rate == 0:
        emi = amount / n
    else:
        factor = (1 + monthly_rate) ** months
        emi = amount * monthly_rate * factor / (factor - 1)
    emi = _q(emi)

    balance = amount
    yearly: list[YearlyRow] = []
    year_principal = Decimal("0")
    year_interest = Decimal("0")
    total_interest = Decimal("0")

    for month in range(1, months + 1):
        interest = _q(balance * monthly_rate)
        principal_paid = balance if month == months else emi - interest
        if principal_paid > balance:
            principal_paid = balance
        balance = _q(balance - principal_paid)
        total_interest += interest
        year_principal += principal_paid
        year_interest += interest
        if month % 12 == 0 or month == months:
            yearly.append(
                YearlyRow(
                    year=(month - 1) // 12 + 1,
                    principal_paid=float(_q(year_principal)),
                    interest_paid=float(_q(year_interest)),
                    balance=float(max(balance, Decimal("0"))),
                )
            )
            year_principal = Decimal("0")
            year_interest = Decimal("0")

    total_payment = amount + total_interest
    return EmiResult(
        principal=float(amount),
        annual_rate=float(rate),
        months=months,
        monthly_emi=float(emi),
        total_interest=float(_q(total_interest)),
        total_payment=float(_q(total_payment)),
        yearly_schedule=yearly,
    )


@dataclass(slots=True)
class AffordabilityResult:
    monthly_income: float
    existing_emi: float
    safe_emi: float
    max_loan: float
    annual_rate: float
    months: int
    debt_to_income: float
    note_ta: str
    note_en: str

    def to_dict(self) -> dict[str, object]:
        return {
            "monthly_income": self.monthly_income,
            "existing_emi": self.existing_emi,
            "safe_emi": self.safe_emi,
            "max_loan": self.max_loan,
            "annual_rate": self.annual_rate,
            "months": self.months,
            "debt_to_income": self.debt_to_income,
            "note_ta": self.note_ta,
            "note_en": self.note_en,
        }


def max_loan_for_emi(emi: float, annual_rate: float, months: int) -> float:
    payment = _positive("emi", emi)
    rate = _positive("annual_rate", annual_rate, allow_zero=True)
    if months <= 0 or months > 600:
        raise ValidationFailed("months must be between 1 and 600")
    monthly_rate = rate / Decimal(1200)
    if monthly_rate == 0:
        return float(_q(payment * months))
    factor = (1 + monthly_rate) ** months
    principal = payment * (factor - 1) / (monthly_rate * factor)
    return float(_q(principal))


def affordability(
    monthly_income: float,
    existing_emi: float = 0,
    *,
    annual_rate: float = 10.0,
    months: int = 60,
    emi_ratio: float = 0.4,
) -> AffordabilityResult:
    income = _positive("monthly_income", monthly_income)
    existing = _positive("existing_emi", existing_emi, allow_zero=True)
    if not 0.1 <= emi_ratio <= 0.6:
        raise ValidationFailed("emi_ratio must be between 0.1 and 0.6")

    safe_emi = max(Decimal("0"), income * Decimal(str(emi_ratio)) - existing)
    max_loan = max_loan_for_emi(float(_q(safe_emi)), annual_rate, months)
    dti = float(existing / income)
    return AffordabilityResult(
        monthly_income=float(income),
        existing_emi=float(existing),
        safe_emi=float(_q(safe_emi)),
        max_loan=max_loan,
        annual_rate=annual_rate,
        months=months,
        debt_to_income=round(dti, 3),
        note_ta=(
            "மொத்த மாதத் தவணை வருமானத்தின் 40%க்கு மேல் செல்ல வேண்டாம். "
            "இது வங்கியின் உண்மையான தகுதியை உறுதிப்படுத்தாது."
        ),
        note_en=(
            "Keep total monthly EMIs within about 40% of income. "
            "This does not guarantee the bank's actual approval."
        ),
    )


@dataclass(slots=True)
class SavingsResult:
    target: float
    months: int
    annual_return: float
    monthly_contribution: float
    total_contributed: float
    growth: float

    def to_dict(self) -> dict[str, object]:
        return {
            "target": self.target,
            "months": self.months,
            "annual_return": self.annual_return,
            "monthly_contribution": self.monthly_contribution,
            "total_contributed": self.total_contributed,
            "growth": self.growth,
        }


def savings_goal(target: float, months: int, annual_return: float = 0.0) -> SavingsResult:
    amount = _positive("target", target)
    if months <= 0 or months > 600:
        raise ValidationFailed("months must be between 1 and 600")
    rate = _positive("annual_return", annual_return, allow_zero=True) / Decimal(1200)
    n = Decimal(months)
    if rate == 0:
        monthly = amount / n
    else:
        factor = (1 + rate) ** months
        monthly = amount * rate / (factor - 1)
    monthly = _q(monthly)
    contributed = _q(monthly * n)
    return SavingsResult(
        target=float(amount),
        months=months,
        annual_return=float(annual_return),
        monthly_contribution=float(monthly),
        total_contributed=float(contributed),
        growth=float(_q(amount - contributed)),
    )


@dataclass(slots=True)
class LoanOffer:
    name: str
    annual_rate: float
    months: int
    processing_fee: float = 0.0


@dataclass(slots=True)
class LoanComparison:
    name: str
    monthly_emi: float
    total_interest: float
    processing_fee: float
    total_cost: float

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "monthly_emi": self.monthly_emi,
            "total_interest": self.total_interest,
            "processing_fee": self.processing_fee,
            "total_cost": self.total_cost,
        }


def compare_loans(principal: float, offers: list[LoanOffer]) -> list[LoanComparison]:
    if not offers:
        raise ValidationFailed("at least one loan offer is required")
    comparisons: list[LoanComparison] = []
    for offer in offers:
        result = calculate_emi(principal, offer.annual_rate, offer.months)
        fee = _positive("processing_fee", offer.processing_fee, allow_zero=True)
        total_cost = Decimal(str(result.total_interest)) + fee
        comparisons.append(
            LoanComparison(
                name=offer.name,
                monthly_emi=result.monthly_emi,
                total_interest=result.total_interest,
                processing_fee=float(_q(fee)),
                total_cost=float(_q(total_cost)),
            )
        )
    comparisons.sort(key=lambda item: item.total_cost)
    return comparisons
