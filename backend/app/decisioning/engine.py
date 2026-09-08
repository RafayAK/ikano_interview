from dataclasses import dataclass

from app.domain.enums import Decision


@dataclass(frozen=True)
class IntegrationOutcome:
    """Decoupled from SQLAlchemy — decisioning never needs a DB session to run."""

    integration: str
    outcome: str


@dataclass(frozen=True)
class DecisionResult:
    outcome: Decision
    reasons: tuple[str, ...]


class DecisionEngine:
    """Deterministic rules mapping integration outcomes to a final decision.

    Reject-level findings always win over manual-review-level findings, even if
    both are present; all matched reason codes are reported regardless of severity.
    """

    def decide(self, integration_results: list[IntegrationOutcome]) -> DecisionResult:
        reasons: list[str] = []
        outcome = Decision.APPROVED

        def escalate(new_outcome: Decision, reason: str) -> None:
            nonlocal outcome
            reasons.append(reason)
            if new_outcome == Decision.REJECTED:
                outcome = Decision.REJECTED
            elif new_outcome == Decision.MANUAL_REVIEW and outcome != Decision.REJECTED:
                outcome = Decision.MANUAL_REVIEW

        for result in integration_results:
            if result.integration == "identity":
                if result.outcome in ("document_mismatch", "expired_id"):
                    escalate(Decision.REJECTED, "identity_not_verified")
                elif result.outcome == "manual_review":
                    escalate(Decision.MANUAL_REVIEW, "identity_manual_review")
            elif result.integration == "registry":
                if result.outcome == "dissolved":
                    escalate(Decision.REJECTED, "company_dissolved")
                elif result.outcome == "unknown_representative":
                    escalate(Decision.MANUAL_REVIEW, "unknown_representative")
                elif result.outcome == "missing_ubo":
                    escalate(Decision.MANUAL_REVIEW, "missing_ubo")
            elif result.integration == "sanctions":
                if result.outcome == "confirmed_hit":
                    escalate(Decision.REJECTED, "confirmed_sanctions_hit")
                elif result.outcome == "possible_hit":
                    escalate(Decision.MANUAL_REVIEW, "possible_sanctions_match")
            elif result.integration == "credit":
                if result.outcome == "poor_credit_history":
                    escalate(Decision.REJECTED, "poor_credit_history")
                elif result.outcome == "low_affordability":
                    escalate(Decision.MANUAL_REVIEW, "low_affordability")
            elif result.integration == "bank_account":
                if result.outcome == "unreachable":
                    escalate(Decision.MANUAL_REVIEW, "bank_account_unreachable")
                elif result.outcome == "name_mismatch":
                    escalate(Decision.MANUAL_REVIEW, "bank_account_name_mismatch")

        return DecisionResult(outcome=outcome, reasons=tuple(reasons))
