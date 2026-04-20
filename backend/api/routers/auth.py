from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas.users import AccessTokenResponse, GoogleLoginRequest, MessageResponse, ResendVerificationRequest, UserProfileResponse
from backend.cores.exception import InvalidToken
from backend.cores.security import verify_token
from backend.database.sessions import get_session
from backend.services.user import UserService
from backend.utils import create_api_log


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/google", response_model=AccessTokenResponse)
async def google_login(
    payload: GoogleLoginRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    service = UserService(session)
    token = await service.google_login(payload.id_token, background_tasks=background_tasks)
    await create_api_log(
        session=session,
        uri_path=str(request.url.path),
        result=True,
        description="Google login succeeded",
    )
    return AccessTokenResponse(access_token=token)


@router.get("/verify", response_model=AccessTokenResponse)
async def verify_email(
    token: str,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    service = UserService(session)
    token_data = await service.verify_email(token)
    access_token = await service.token(token_data["email"])
    await create_api_log(
        session=session,
        user_id=token_data.get("id"),
        uri_path=str(request.url.path),
        result=True,
        description="Email verification succeeded",
    )
    return AccessTokenResponse(access_token=access_token)


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification_email(
    payload: ResendVerificationRequest,
    request: Request,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    service = UserService(session)
    await service.resend_verification_email(payload.email, background_tasks=background_tasks)
    await create_api_log(
        session=session,
        uri_path=str(request.url.path),
        result=True,
        description="Verification email resend requested",
    )
    return MessageResponse(detail="Verification email sent")


@router.get("/profile", response_model=UserProfileResponse)
async def get_my_profile(
    request: Request,
    token_data: dict = Depends(verify_token),
    session: AsyncSession = Depends(get_session),
):
    user_id = token_data.get("user", {}).get("user_id")
    user_uuid = token_data.get("user", {}).get("id")
    if not user_id:
        await create_api_log(
            session=session,
            user_id=user_uuid,
            uri_path=str(request.url.path),
            result=False,
            description="Profile read failed: invalid token data",
        )
        raise InvalidToken()

    service = UserService(session)
    profile = await service.get_user_data(user_id)
    await create_api_log(
        session=session,
        user_id=user_uuid,
        uri_path=str(request.url.path),
        result=True,
        description="Profile read succeeded",
    )
    return UserProfileResponse(**profile)