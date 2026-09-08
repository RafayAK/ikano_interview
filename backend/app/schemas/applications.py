from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.domain.enums import Country, CustomerType, ApplicationStatus
from app.domain.enums import StepStatus, Decision


class CreateApplicationRequest(BaseModel):
    country: Country
    customer_type: CustomerType


class ProgressResponse(BaseModel):
    completed: int
    total: int

class ApplicationResponse(BaseModel):
    id: UUID
    country: Country
    customer_type: CustomerType
    status: ApplicationStatus
    current_step: str | None
    progress: ProgressResponse
    created_at: datetime
    updated_at: datetime


class StepSummary(BaseModel):
    id: str
    title: str
    status: StepStatus

class ApplicationDetailResponse(ApplicationResponse):
    steps: list[StepSummary]
    decision: Decision | None = None
    decision_reasons: list[str] = []

class CurrentStepResponse(BaseModel):
    id: str
    title: str
    position: int
    total_steps: int
    status: StepStatus
    schema_: dict = Field(alias="schema", serialization_alias="schema")

    model_config = {"populate_by_name": True}


class AuditEventResponse(BaseModel):
    id: UUID
    event_type: str
    step_id: str | None
    integration: str | None
    outcome: str | None
    occurred_at: datetime
