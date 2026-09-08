from typing import Any
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import RESUME_COOKIE_NAME, settings
from app.db.session import get_session
from app.domain.enums import StepStatus
from app.domain.errors import (
    ApplicationAlreadyFinalizedError,
    ApplicationNotFoundError,
    ApplicationNotReadyForSubmissionError,
    InvalidStepTransitionError,
)
from app.schemas.applications import ApplicationResponse, CreateApplicationRequest
from app.schemas.applications import ApplicationDetailResponse, AuditEventResponse, CurrentStepResponse
from app.schemas.applications import ProgressResponse, StepSummary
from app.schemas.steps import get_step_input_schema
from app.services import onboarding as onboarding_service
from app.services.step_processing import complete_step

router = APIRouter(
    prefix="/applications",
    tags=["applications"],
)


async def _build_detail_response(session: AsyncSession, application) -> ApplicationDetailResponse:
    flow = onboarding_service.get_flow_for(application)
    statuses = await onboarding_service.get_step_statuses(session, application.id)
    steps = [
        StepSummary(id=step.id, title=step.title, status=statuses.get(step.id, StepStatus.PENDING))
        for step in flow.steps
    ]
    completed = sum(1 for s in statuses.values() if s == StepStatus.COMPLETED)

    return ApplicationDetailResponse(
        id=application.id,
        country=application.country,
        customer_type=application.customer_type,
        status=application.status,
        current_step=application.current_step,
        progress=ProgressResponse(completed=completed, total=len(flow.step_ids)),
        created_at=application.created_at,
        updated_at=application.updated_at,
        steps=steps,
        decision=application.decision,
        decision_reasons=application.decision_reasons or [],
    )


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ApplicationResponse)
async def create_application(
    request: CreateApplicationRequest,
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new onboarding application.
    """
    application = await onboarding_service.create_application(
        session, request.country, request.customer_type
    )
    response.set_cookie(
        RESUME_COOKIE_NAME,
        application.resume_token,
        max_age=settings.resume_token_ttl_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
    )
    flow = onboarding_service.get_flow_for(application)
    return ApplicationResponse(
        id=application.id,
        country=application.country,
        customer_type=application.customer_type,
        status=application.status,
        current_step=application.current_step,
        progress=ProgressResponse(completed=0, total=len(flow.step_ids)),
        created_at=application.created_at,
        updated_at=application.updated_at,
    )


@router.get("/{application_id}", response_model=ApplicationDetailResponse)
async def get_application(application_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Get current overall state of an onboarding application by ID.
    """
    try:
        application = await onboarding_service.get_application(session, application_id)
    except ApplicationNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Application not found") from exc

    return await _build_detail_response(session, application)


@router.get("/{application_id}/steps/current", response_model=CurrentStepResponse)
async def get_current_step(application_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Get the current actionable step of an onboarding application by ID.
    """
    try:
        application = await onboarding_service.get_application(session, application_id)
    except ApplicationNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Application not found") from exc

    if application.current_step is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Application has no current step")

    flow = onboarding_service.get_flow_for(application)
    step = flow.get_step(application.current_step)
    statuses = await onboarding_service.get_step_statuses(session, application.id)
    input_schema = get_step_input_schema(
        application.country, application.customer_type, step.id
    )

    return CurrentStepResponse(
        id=step.id,
        title=step.title,
        position=flow.position(step.id),
        total_steps=len(flow.step_ids),
        status=statuses.get(step.id, StepStatus.PENDING),
        schema=input_schema.model_json_schema(),
    )


@router.put("/{application_id}/steps/{step_id}", response_model=ApplicationDetailResponse)
async def update_step(
    application_id: UUID,
    step_id: str,
    payload: dict[str, Any] = Body(default_factory=dict),
    session: AsyncSession = Depends(get_session),
):
    """
    Validate + update + complete the status of a specific step in an onboarding application.
    """
    try:
        application = await onboarding_service.get_application(session, application_id)
    except ApplicationNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Application not found") from exc

    schema = get_step_input_schema(application.country, application.customer_type, step_id)
    try:
        validated = schema.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_CONTENT, jsonable_encoder(exc.errors())
        ) from exc

    try:
        await complete_step(session, application, step_id, validated.model_dump())
    except InvalidStepTransitionError as exc:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            {"code": "INVALID_STEP_TRANSITION", "message": str(exc)},
        ) from exc

    return await _build_detail_response(session, application)


@router.put("/{application_id}/submit", response_model=ApplicationDetailResponse)
async def submit_application(application_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Submit an onboarding application by ID.
    """
    try:
        application = await onboarding_service.submit_application(session, application_id)
    except ApplicationNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Application not found") from exc
    except ApplicationAlreadyFinalizedError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc
    except ApplicationNotReadyForSubmissionError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc

    return await _build_detail_response(session, application)


@router.get("/{application_id}/audit-events", response_model=list[AuditEventResponse])
async def get_audit_events(application_id: UUID, session: AsyncSession = Depends(get_session)):
    """
    Audit history of an onboarding application by ID.
    """
    try:
        await onboarding_service.get_application(session, application_id)
    except ApplicationNotFoundError as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Application not found") from exc

    events = await onboarding_service.get_audit_events(session, application_id)
    return [
        AuditEventResponse(
            id=event.id,
            event_type=event.event_type,
            step_id=event.step_id,
            integration=event.integration,
            outcome=event.outcome,
            occurred_at=event.occurred_at,
        )
        for event in events
    ]
