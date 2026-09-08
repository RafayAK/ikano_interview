from enum import StrEnum


class Country(StrEnum):
    SWEDEN = "sweden"
    SPAIN = "spain"
    POLAND = "poland"


class CustomerType(StrEnum):
    PRIVATE = "private"
    BUSINESS = "business"


class ApplicationStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    MANUAL_REVIEW = "manual_review"
    REJECTED = "rejected"
    EXPIRED = "expired"


class StepStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"


class Decision(StrEnum):
    APPROVED = "approved"
    MANUAL_REVIEW = "manual_review"
    REJECTED = "rejected"
