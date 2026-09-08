from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import RESUME_COOKIE_NAME
from app.db.session import get_session
from app.schemas.resume import ResumeResponse
from app.services import onboarding as onboarding_service

router = APIRouter(prefix="/resume", tags=["resume"])


@router.get("", response_model=ResumeResponse)
async def resume(
    resume_token: str | None = Cookie(default=None),
    session: AsyncSession = Depends(get_session),
):
    """
    Look up the in-progress application for the resume cookie on this browser, if any.
    """
    if resume_token is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No resume cookie present")

    application = await onboarding_service.get_application_by_resume_token(session, resume_token)
    if application is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume token is invalid or expired")

    return ResumeResponse(
        application_id=application.id,
        status=application.status,
        current_step=application.current_step,
    )


@router.post("/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear_resume_cookie(response: Response):
    """
    Clear the resume cookie from the browser. Dev/demo convenience — does not
    invalidate the token server-side, it just stops this browser from presenting it.
    """
    response.delete_cookie(RESUME_COOKIE_NAME)
