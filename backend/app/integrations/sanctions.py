from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class SanctionsOutcome(StrEnum):
    NO_HIT = "no_hit"
    POSSIBLE_HIT = "possible_hit"
    CONFIRMED_HIT = "confirmed_hit"


@dataclass(frozen=True)
class SanctionsCheckRequest:
    identifier: str


@dataclass(frozen=True)
class SanctionsCheckResult:
    outcome: SanctionsOutcome

    def to_payload(self) -> dict:
        return {"outcome": self.outcome.value}


class SanctionsClient(Protocol):
    async def check(self, request: SanctionsCheckRequest) -> SanctionsCheckResult: ...


class MockSanctionsClient:
    """Deterministic PEP/sanctions mock, keyed off the identifier's suffix.

    ...666 -> confirmed_hit, ...000 -> possible_hit, else no_hit.
    """

    async def check(self, request: SanctionsCheckRequest) -> SanctionsCheckResult:
        identifier = request.identifier
        if identifier.endswith("666"):
            return SanctionsCheckResult(SanctionsOutcome.CONFIRMED_HIT)
        if identifier.endswith("000"):
            return SanctionsCheckResult(SanctionsOutcome.POSSIBLE_HIT)
        return SanctionsCheckResult(SanctionsOutcome.NO_HIT)
