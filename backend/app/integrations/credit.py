from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class CreditOutcome(StrEnum):
    CLEAN = "clean"
    LOW_AFFORDABILITY = "low_affordability"
    POOR_CREDIT_HISTORY = "poor_credit_history"


@dataclass(frozen=True)
class CreditCheckRequest:
    identifier: str
    income: float


@dataclass(frozen=True)
class CreditCheckResult:
    outcome: CreditOutcome
    score: int
    debt_flags: tuple[str, ...]
    disposable_income: float

    def to_payload(self) -> dict:
        return {
            "outcome": self.outcome.value,
            "score": self.score,
            "debt_flags": list(self.debt_flags),
            "disposable_income": self.disposable_income,
        }


class CreditClient(Protocol):
    async def check(self, request: CreditCheckRequest) -> CreditCheckResult: ...


class MockCreditClient:
    """Deterministic credit-bureau/affordability mock, keyed off the identifier's suffix.

    ...999 -> poor_credit_history, ...000 -> low_affordability, else clean.
    """

    async def check(self, request: CreditCheckRequest) -> CreditCheckResult:
        identifier = request.identifier
        if identifier.endswith("999"):
            return CreditCheckResult(
                CreditOutcome.POOR_CREDIT_HISTORY,
                score=300,
                debt_flags=("default_history",),
                disposable_income=-100.0,
            )
        if identifier.endswith("000"):
            return CreditCheckResult(
                CreditOutcome.LOW_AFFORDABILITY,
                score=580,
                debt_flags=("high_debt",),
                disposable_income=50.0,
            )
        return CreditCheckResult(
            CreditOutcome.CLEAN,
            score=750,
            debt_flags=(),
            disposable_income=max(request.income * 0.4, 0.0),
        )
