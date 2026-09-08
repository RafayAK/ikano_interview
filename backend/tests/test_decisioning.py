from app.decisioning.engine import DecisionEngine, IntegrationOutcome
from app.domain.enums import Decision


def test_all_clean_checks_approve_application():
    results = [
        IntegrationOutcome("identity", "verified"),
        IntegrationOutcome("sanctions", "no_hit"),
        IntegrationOutcome("credit", "clean"),
    ]
    decision = DecisionEngine().decide(results)
    assert decision.outcome == Decision.APPROVED
    assert decision.reasons == ()


def test_confirmed_sanctions_hit_rejects_application():
    results = [IntegrationOutcome("sanctions", "confirmed_hit")]
    decision = DecisionEngine().decide(results)
    assert decision.outcome == Decision.REJECTED
    assert decision.reasons == ("confirmed_sanctions_hit",)


def test_possible_sanctions_hit_triggers_manual_review():
    results = [IntegrationOutcome("sanctions", "possible_hit")]
    decision = DecisionEngine().decide(results)
    assert decision.outcome == Decision.MANUAL_REVIEW
    assert decision.reasons == ("possible_sanctions_match",)


def test_identity_manual_review_triggers_manual_review():
    results = [IntegrationOutcome("identity", "manual_review")]
    decision = DecisionEngine().decide(results)
    assert decision.outcome == Decision.MANUAL_REVIEW
    assert decision.reasons == ("identity_manual_review",)


def test_identity_document_mismatch_rejects_application():
    results = [IntegrationOutcome("identity", "document_mismatch")]
    decision = DecisionEngine().decide(results)
    assert decision.outcome == Decision.REJECTED
    assert decision.reasons == ("identity_not_verified",)


def test_dissolved_company_rejects_application():
    results = [IntegrationOutcome("registry", "dissolved")]
    decision = DecisionEngine().decide(results)
    assert decision.outcome == Decision.REJECTED
    assert decision.reasons == ("company_dissolved",)


def test_unknown_representative_triggers_manual_review():
    results = [IntegrationOutcome("registry", "unknown_representative")]
    decision = DecisionEngine().decide(results)
    assert decision.outcome == Decision.MANUAL_REVIEW
    assert decision.reasons == ("unknown_representative",)


def test_low_affordability_triggers_manual_review():
    results = [IntegrationOutcome("credit", "low_affordability")]
    decision = DecisionEngine().decide(results)
    assert decision.outcome == Decision.MANUAL_REVIEW
    assert decision.reasons == ("low_affordability",)


def test_poor_credit_history_rejects_application():
    results = [IntegrationOutcome("credit", "poor_credit_history")]
    decision = DecisionEngine().decide(results)
    assert decision.outcome == Decision.REJECTED
    assert decision.reasons == ("poor_credit_history",)


def test_bank_account_unreachable_triggers_manual_review():
    results = [IntegrationOutcome("bank_account", "unreachable")]
    decision = DecisionEngine().decide(results)
    assert decision.outcome == Decision.MANUAL_REVIEW
    assert decision.reasons == ("bank_account_unreachable",)


def test_rejection_takes_priority_over_manual_review():
    results = [
        IntegrationOutcome("sanctions", "possible_hit"),
        IntegrationOutcome("registry", "dissolved"),
    ]
    decision = DecisionEngine().decide(results)
    assert decision.outcome == Decision.REJECTED
    assert set(decision.reasons) == {"possible_sanctions_match", "company_dissolved"}
