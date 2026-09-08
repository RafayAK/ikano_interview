from datetime import UTC, datetime, timedelta
from secrets import token_urlsafe
from uuid import UUID

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import AuditEvent, IntegrationResult, OnboardingApplication, StepState
from app.decisioning.engine import DecisionEngine, IntegrationOutcome
from app.domain.enums import ApplicationStatus, Country, CustomerType, StepStatus
from app.domain.errors import (
    ApplicationAlreadyFinalizedError,
    ApplicationNotFoundError,
    ApplicationNotReadyForSubmissionError,
)
from app.flows.base import FlowDefinition
from app.flows.registry import get_flow


async def create_application(
    session: AsyncSession, country: Country, customer_type: CustomerType
) -> OnboardingApplication:
    flow = get_flow(country, customer_type)
    application = OnboardingApplication(
        country=country,
        customer_type=customer_type,
        status=ApplicationStatus.IN_PROGRESS,
        current_step=flow.first_step.id,
        # opaque bearer token for the resume flow — never the application id itself
        resume_token=token_urlsafe(32),
        resume_token_expires_at=datetime.now(UTC).replace(tzinfo=None)
        + timedelta(days=settings.resume_token_ttl_days),
    )
    session.add(application)
    await session.flush()

    session.add(AuditEvent(application_id=application.id, event_type="application_created"))
    await session.commit()
    await session.refresh(application)
    logger.bind(application_id=str(application.id)).info(
        "event=application_created country={} customer_type={}", country.value, customer_type.value
    )
    return application


async def get_application(session: AsyncSession, application_id: UUID) -> OnboardingApplication:
    application = await session.get(OnboardingApplication, application_id)
    if application is None:
        raise ApplicationNotFoundError(application_id)
    return application


async def get_step_statuses(
    session: AsyncSession, application_id: UUID
) -> dict[str, StepStatus]:
    """Statuses for steps that have a row; steps with no row are implicitly PENDING."""
    result = await session.execute(
        select(StepState.step_id, StepState.status).where(
            StepState.application_id == application_id
        )
    )
    return dict(result.all())


def get_flow_for(application: OnboardingApplication) -> FlowDefinition:
    return get_flow(application.country, application.customer_type)


async def submit_application(session: AsyncSession, application_id: UUID) -> OnboardingApplication:
    application = await get_application(session, application_id)

    if application.status != ApplicationStatus.IN_PROGRESS:
        raise ApplicationAlreadyFinalizedError(application_id)
    if application.current_step is not None:
        raise ApplicationNotReadyForSubmissionError(application_id, application.current_step)

    result = await session.execute(
        select(IntegrationResult.integration, IntegrationResult.outcome).where(
            IntegrationResult.application_id == application_id
        )
    )
    integration_outcomes = [IntegrationOutcome(integration, outcome) for integration, outcome in result.all()]

    decision = DecisionEngine().decide(integration_outcomes)

    application.status = ApplicationStatus(decision.outcome.value)
    application.decision = decision.outcome
    application.decision_reasons = list(decision.reasons)
    application.submitted_at = datetime.now(UTC).replace(tzinfo=None)

    session.add(
        AuditEvent(
            application_id=application.id,
            event_type="decision_made",
            outcome=decision.outcome.value,
        )
    )
    session.add(AuditEvent(application_id=application.id, event_type="application_submitted"))

    await session.commit()
    await session.refresh(application)
    logger.bind(application_id=str(application.id)).info(
        "event=decision_made outcome={} reasons={}", decision.outcome.value, list(decision.reasons)
    )
    return application


async def get_audit_events(session: AsyncSession, application_id: UUID) -> list[AuditEvent]:
    result = await session.execute(
        select(AuditEvent)
        .where(AuditEvent.application_id == application_id)
        .order_by(AuditEvent.occurred_at)
    )
    return list(result.scalars().all())


async def get_application_by_resume_token(
    session: AsyncSession, resume_token: str
) -> OnboardingApplication | None:
    result = await session.execute(
        select(OnboardingApplication).where(OnboardingApplication.resume_token == resume_token)
    )
    application = result.scalar_one_or_none()
    if application is None:
        return None
    if application.resume_token_expires_at < datetime.now(UTC).replace(tzinfo=None):
        return None
    return application
