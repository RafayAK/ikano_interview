from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class IdentityOutcome(StrEnum):
    VERIFIED = "verified"
    DOCUMENT_MISMATCH = "document_mismatch"
    EXPIRED_ID = "expired_id"
    MANUAL_REVIEW = "manual_review"


@dataclass(frozen=True)
class IdentityCheckRequest:
    identifier: str


@dataclass(frozen=True)
class IdentityCheckResult:
    outcome: IdentityOutcome
    confidence: float

    def to_payload(self) -> dict:
        return {"outcome": self.outcome.value, "confidence": self.confidence}


class IdentityClient(Protocol):
    async def check(self, request: IdentityCheckRequest) -> IdentityCheckResult: ...


class MockIdentityClient:
    """Deterministic identity/KYC mock, keyed off the identifier's suffix.

    ...000 -> manual_review, ...999 -> document_mismatch, ...888 -> expired_id, else verified.
    """

    async def check(self, request: IdentityCheckRequest) -> IdentityCheckResult:
        identifier = request.identifier
        if identifier.endswith("000"):
            return IdentityCheckResult(IdentityOutcome.MANUAL_REVIEW, confidence=0.5)
        if identifier.endswith("999"):
            return IdentityCheckResult(IdentityOutcome.DOCUMENT_MISMATCH, confidence=0.1)
        if identifier.endswith("888"):
            return IdentityCheckResult(IdentityOutcome.EXPIRED_ID, confidence=0.2)
        return IdentityCheckResult(IdentityOutcome.VERIFIED, confidence=0.98)
