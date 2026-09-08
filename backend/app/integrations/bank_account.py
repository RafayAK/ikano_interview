from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class BankAccountOutcome(StrEnum):
    IBAN_VERIFIED = "iban_verified"
    NAME_MISMATCH = "name_mismatch"
    UNREACHABLE = "unreachable"


@dataclass(frozen=True)
class BankAccountCheckRequest:
    iban: str


@dataclass(frozen=True)
class BankAccountCheckResult:
    outcome: BankAccountOutcome

    def to_payload(self) -> dict:
        return {"outcome": self.outcome.value}


class BankAccountClient(Protocol):
    async def check(self, request: BankAccountCheckRequest) -> BankAccountCheckResult: ...


class MockBankAccountClient:
    """Deterministic bank-account mock, keyed off the IBAN's suffix.

    ...00 -> unreachable, ...99 -> name_mismatch, else iban_verified.
    """

    async def check(self, request: BankAccountCheckRequest) -> BankAccountCheckResult:
        iban = request.iban
        if iban.endswith("00"):
            return BankAccountCheckResult(BankAccountOutcome.UNREACHABLE)
        if iban.endswith("99"):
            return BankAccountCheckResult(BankAccountOutcome.NAME_MISMATCH)
        return BankAccountCheckResult(BankAccountOutcome.IBAN_VERIFIED)
