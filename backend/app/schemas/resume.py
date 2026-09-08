from uuid import UUID

from pydantic import BaseModel

from app.domain.enums import ApplicationStatus


class ResumeResponse(BaseModel):
    application_id: UUID
    status: ApplicationStatus
    current_step: str | None
