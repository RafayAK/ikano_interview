from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class RegistryOutcome(StrEnum):
    ACTIVE_COMPANY = "active_company"
    DISSOLVED = "dissolved"
    UNKNOWN_REPRESENTATIVE = "unknown_representative"
    MISSING_UBO = "missing_ubo"


@dataclass(frozen=True)
class RegistryCheckRequest:
    identifier: str


@dataclass(frozen=True)
class RegistryCheckResult:
    outcome: RegistryOutcome

    def to_payload(self) -> dict:
        return {"outcome": self.outcome.value}


class RegistryClient(Protocol):
    async def check(self, request: RegistryCheckRequest) -> RegistryCheckResult: ...


class MockRegistryClient:
    """Deterministic KYB/company-registry mock, keyed off the identifier's suffix.

    ...000 -> dissolved, ...999 -> unknown_representative, ...888 -> missing_ubo, else active_company.
    """

    async def check(self, request: RegistryCheckRequest) -> RegistryCheckResult:
        identifier = request.identifier
        if identifier.endswith("000"):
            return RegistryCheckResult(RegistryOutcome.DISSOLVED)
        if identifier.endswith("999"):
            return RegistryCheckResult(RegistryOutcome.UNKNOWN_REPRESENTATIVE)
        if identifier.endswith("888"):
            return RegistryCheckResult(RegistryOutcome.MISSING_UBO)
        return RegistryCheckResult(RegistryOutcome.ACTIVE_COMPANY)
