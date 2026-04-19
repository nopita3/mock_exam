from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas.users import AccessTokenResponse, GoogleLoginRequest, MessageResponse
from backend.database.sessions import get_session
from backend.services.user import UserService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/google", response_model=AccessTokenResponse)
async def google_login(
    payload: GoogleLoginRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    service = UserService(session)
    token = await service.google_login(payload.id_token, background_tasks=background_tasks)
    return AccessTokenResponse(access_token=token)


@router.get("/verify", response_model=MessageResponse)
async def verify_email(
    token: str,
    session: AsyncSession = Depends(get_session),
):
    service = UserService(session)
    await service.verify_email(token)
    return MessageResponse(detail="Email verified successfully")