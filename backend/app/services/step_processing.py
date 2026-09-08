from dataclasses import dataclass
from typing import Any, Callable
from uuid import UUID

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AuditEvent, IntegrationResult, OnboardingApplication, StepState
from app.domain.enums import Country, CustomerType, StepStatus
from app.domain.errors import InvalidStepTransitionError
from app.integrations.bank_account import BankAccountCheckRequest, MockBankAccountClient
from app.integrations.credit import CreditCheckRequest, MockCreditClient
from app.integrations.identity import IdentityCheckRequest, MockIdentityClient
from app.integrations.registry import MockRegistryClient, RegistryCheckRequest
from app.integrations.sanctions import MockSanctionsClient, SanctionsCheckRequest
from app.services.onboarding import get_flow_for

_identity_client = MockIdentityClient()
_registry_client = MockRegistryClient()
_sanctions_client = MockSanctionsClient()
_credit_client = MockCreditClient()
_bank_account_client = MockBankAccountClient()

_CLIENTS = {
    "identity": _identity_client,
    "registry": _registry_client,
    "sanctions": _sanctions_client,
    "credit": _credit_client,
    "bank_account": _bank_account_client,
}


@dataclass
class StepAnswers:
    """Answers available while processing a step: this step's own input, plus
    every earlier completed step's persisted answers, keyed by step_id."""

    current: dict[str, Any]
    prior: dict[str, dict[str, Any]]

    def field(self, step_id: str, field_name: str) -> Any:
        return self.prior.get(step_id, {}).get(field_name)


@dataclass(frozen=True)
class IntegrationSpec:
    name: str
    build_request: Callable[[StepAnswers], Any]


# Registered per (country, customer_type, step_id) — no per-country conditionals
# anywhere else in the codebase reference this; adding a country/step only means
# adding entries here.
STEP_INTEGRATIONS: dict[tuple[Country, CustomerType, str], tuple[IntegrationSpec, ...]] = {
    # Sweden private
    (Country.SWEDEN, CustomerType.PRIVATE, "personal_info"): (
        IntegrationSpec("identity", lambda a: IdentityCheckRequest(a.current["personal_identity_number"])),
    ),
    (Country.SWEDEN, CustomerType.PRIVATE, "consent"): (
        IntegrationSpec(
            "sanctions",
            lambda a: SanctionsCheckRequest(a.field("personal_info", "personal_identity_number")),
        ),
    ),
    (Country.SWEDEN, CustomerType.PRIVATE, "credit_decision"): (
        IntegrationSpec(
            "credit",
            lambda a: CreditCheckRequest(
                a.field("personal_info", "personal_identity_number"),
                a.field("employment_income", "monthly_income") or 0.0,
            ),
        ),
    ),
    # Spain private
    (Country.SPAIN, CustomerType.PRIVATE, "personal_info"): (
        IntegrationSpec("identity", lambda a: IdentityCheckRequest(a.current["dni_or_nie"])),
    ),
    (Country.SPAIN, CustomerType.PRIVATE, "consent"): (
        IntegrationSpec("sanctions", lambda a: SanctionsCheckRequest(a.field("personal_info", "dni_or_nie"))),
    ),
    (Country.SPAIN, CustomerType.PRIVATE, "credit_decision"): (
        IntegrationSpec(
            "credit",
            lambda a: CreditCheckRequest(
                a.field("personal_info", "dni_or_nie"),
                a.field("employment_income", "monthly_income") or 0.0,
            ),
        ),
    ),
    # Poland private
    (Country.POLAND, CustomerType.PRIVATE, "personal_info"): (
        IntegrationSpec("identity", lambda a: IdentityCheckRequest(a.current["pesel"])),
    ),
    (Country.POLAND, CustomerType.PRIVATE, "consent"): (
        IntegrationSpec("sanctions", lambda a: SanctionsCheckRequest(a.field("personal_info", "pesel"))),
    ),
    (Country.POLAND, CustomerType.PRIVATE, "credit_decision"): (
        IntegrationSpec(
            "credit",
            lambda a: CreditCheckRequest(
                a.field("personal_info", "pesel"),
                a.field("employment_income", "monthly_income") or 0.0,
            ),
        ),
    ),
    # Sweden business
    (Country.SWEDEN, CustomerType.BUSINESS, "company_registry_lookup"): (
        IntegrationSpec(
            "registry", lambda a: RegistryCheckRequest(a.field("organisation_info", "organisation_number"))
        ),
    ),
    (Country.SWEDEN, CustomerType.BUSINESS, "authorised_representative"): (
        IntegrationSpec("identity", lambda a: IdentityCheckRequest(a.current["representative_identifier"])),
    ),
    (Country.SWEDEN, CustomerType.BUSINESS, "beneficial_owners"): (
        IntegrationSpec("sanctions", lambda a: SanctionsCheckRequest(a.current["owners"][0]["identifier"])),
    ),
    (Country.SWEDEN, CustomerType.BUSINESS, "kyb_credit_decision"): (
        IntegrationSpec(
            "credit",
            lambda a: CreditCheckRequest(
                a.field("organisation_info", "organisation_number"),
                a.field("business_activity", "turnover") or 0.0,
            ),
        ),
    ),
    # Spain business
    (Country.SPAIN, CustomerType.BUSINESS, "registro_mercantil"): (
        IntegrationSpec("registry", lambda a: RegistryCheckRequest(a.field("company_info", "company_nif"))),
    ),
    (Country.SPAIN, CustomerType.BUSINESS, "legal_representative_verification"): (
        IntegrationSpec("identity", lambda a: IdentityCheckRequest(a.current["representative_identifier"])),
    ),
    (Country.SPAIN, CustomerType.BUSINESS, "beneficial_owners"): (
        IntegrationSpec("sanctions", lambda a: SanctionsCheckRequest(a.current["owners"][0]["identifier"])),
    ),
    (Country.SPAIN, CustomerType.BUSINESS, "kyb_credit_iban"): (
        IntegrationSpec(
            "credit",
            lambda a: CreditCheckRequest(
                a.field("company_info", "company_nif"), a.field("sector_turnover", "turnover") or 0.0
            ),
        ),
        IntegrationSpec("bank_account", lambda a: BankAccountCheckRequest(a.current["iban"])),
    ),
    # Poland business
    (Country.POLAND, CustomerType.BUSINESS, "registry_lookup"): (
        IntegrationSpec("registry", lambda a: RegistryCheckRequest(a.field("organisation_info", "nip"))),
    ),
    (Country.POLAND, CustomerType.BUSINESS, "authority_confirmation"): (
        IntegrationSpec("identity", lambda a: IdentityCheckRequest(a.current["representative_identifier"])),
    ),
    (Country.POLAND, CustomerType.BUSINESS, "beneficial_owners"): (
        IntegrationSpec("sanctions", lambda a: SanctionsCheckRequest(a.current["owners"][0]["identifier"])),
    ),
    (Country.POLAND, CustomerType.BUSINESS, "kyb_credit_bank_validation"): (
        IntegrationSpec("credit", lambda a: CreditCheckRequest(a.field("organisation_info", "nip"), 0.0)),
        IntegrationSpec("bank_account", lambda a: BankAccountCheckRequest(a.current["iban"])),
    ),
}


async def _get_prior_answers(session: AsyncSession, application_id: UUID) -> dict[str, dict[str, Any]]:
    result = await session.execute(
        select(StepState.step_id, StepState.answers).where(
            StepState.application_id == application_id,
            StepState.status == StepStatus.COMPLETED,
        )
    )
    return dict(result.all())


async def complete_step(
    session: AsyncSession,
    application: OnboardingApplication,
    step_id: str,
    answers: dict[str, Any],
) -> None:
    """Validate the transition, persist answers, run any triggered integrations,
    mark the step completed, and advance the application to the next step."""
    if application.current_step != step_id:
        raise InvalidStepTransitionError(step_id, application.current_step)

    prior_answers = await _get_prior_answers(session, application.id)
    step_answers = StepAnswers(current=answers, prior=prior_answers)

    result = await session.execute(
        select(StepState).where(
            StepState.application_id == application.id, StepState.step_id == step_id
        )
    )
    step_state = result.scalar_one_or_none()
    if step_state is None:
        step_state = StepState(application_id=application.id, step_id=step_id)
        session.add(step_state)
    step_state.answers = answers
    step_state.status = StepStatus.COMPLETED

    key = (application.country, application.customer_type, step_id)
    log = logger.bind(application_id=str(application.id))
    for spec in STEP_INTEGRATIONS.get(key, ()):
        client = _CLIENTS[spec.name]
        request = spec.build_request(step_answers)
        outcome_result = await client.check(request)
        session.add(
            IntegrationResult(
                application_id=application.id,
                integration=spec.name,
                outcome=outcome_result.outcome.value,
                payload=outcome_result.to_payload(),
            )
        )
        session.add(
            AuditEvent(
                application_id=application.id,
                event_type="integration_completed",
                step_id=step_id,
                integration=spec.name,
                outcome=outcome_result.outcome.value,
            )
        )
        log.info(
            "event=integration_completed step_id={} integration={} outcome={}",
            step_id,
            spec.name,
            outcome_result.outcome.value,
        )

    flow = get_flow_for(application)
    next_step = flow.next_step(step_id)
    application.current_step = next_step.id if next_step is not None else None

    session.add(
        AuditEvent(application_id=application.id, event_type="step_completed", step_id=step_id)
    )

    await session.commit()
    await session.refresh(application)
    log.info("event=step_completed step_id={}", step_id)
