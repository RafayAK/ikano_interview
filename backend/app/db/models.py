import uuid
from datetime import datetime

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String, UniqueConstraint, func, text
from sqlalchemy import Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.domain.enums import (
    ApplicationStatus,
    Country,
    CustomerType,
    Decision,
    StepStatus,
)


class OnboardingApplication(Base):
    __tablename__ = "onboarding_applications"
    __table_args__ = (
        # partial unique index: only enforce uniqueness while a token is actually set
        Index(
            "uq_onboarding_applications_resume_token",
            "resume_token",
            unique=True,
            postgresql_where=text("resume_token IS NOT NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    country: Mapped[Country] = mapped_column(SAEnum(Country, native_enum=False, length=20))
    customer_type: Mapped[CustomerType] = mapped_column(
        SAEnum(CustomerType, native_enum=False, length=20)
    )
    status: Mapped[ApplicationStatus] = mapped_column(
        SAEnum(ApplicationStatus, native_enum=False, length=20),
        default=ApplicationStatus.IN_PROGRESS,
    )
    current_step: Mapped[str | None] = mapped_column(String(64), nullable=True)
    decision: Mapped[Decision | None] = mapped_column(
        SAEnum(Decision, native_enum=False, length=20), nullable=True
    )
    decision_reasons: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)

    # opaque bearer token for the resume flow; never the application id itself
    resume_token: Mapped[str | None] = mapped_column(String(64), nullable=True)
    resume_token_expires_at: Mapped[datetime | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
    submitted_at: Mapped[datetime | None] = mapped_column(nullable=True)


class StepState(Base):
    __tablename__ = "step_states"
    __table_args__ = (UniqueConstraint("application_id", "step_id"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("onboarding_applications.id", ondelete="CASCADE"), index=True
    )
    step_id: Mapped[str] = mapped_column(String(64))
    status: Mapped[StepStatus] = mapped_column(
        SAEnum(StepStatus, native_enum=False, length=20), default=StepStatus.PENDING
    )
    answers: Mapped[dict] = mapped_column(JSONB, default=dict)
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )


class IntegrationResult(Base):
    __tablename__ = "integration_results"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("onboarding_applications.id", ondelete="CASCADE"), index=True
    )
    integration: Mapped[str] = mapped_column(String(32))
    outcome: Mapped[str] = mapped_column(String(32))
    # structured decisioning fields only — never raw identifiers (PESEL, DNI/NIE, income...)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict)

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("onboarding_applications.id", ondelete="CASCADE"), index=True
    )
    request_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    event_type: Mapped[str] = mapped_column(String(64))
    step_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    integration: Mapped[str | None] = mapped_column(String(32), nullable=True)
    outcome: Mapped[str | None] = mapped_column(String(32), nullable=True)

    occurred_at: Mapped[datetime] = mapped_column(server_default=func.now())
