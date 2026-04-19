from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas.users import StudentRegisterRequest, StudentRegisterResponse, StudentSelfScoreResponse
from backend.cores.exception import InvalidToken
from backend.cores.security import verify_token
from backend.database.sessions import get_session
from backend.services.student import StudentService
from backend.utils import create_api_log


router = APIRouter(prefix="/student", tags=["student"])


@router.post("/regist", response_model=StudentRegisterResponse)
async def regist_student(
    payload: StudentRegisterRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    session: AsyncSession = Depends(get_session),
):
    service = StudentService(session)
    user = await service.register_student(payload, background_tasks=background_tasks)
    await create_api_log(
        session=session,
        user_id=getattr(user, "id", None),
        uri_path=str(request.url.path),
        result=True,
        description="Student registration succeeded",
    )
    return StudentRegisterResponse(
        user_id=user.user_id,
        email=user.email,
        fname=user.fname,
        lname=user.lname,
        nname=user.nname,
        department=payload.department,
    )


@router.get("/score/self", response_model=StudentSelfScoreResponse)
async def get_my_score(
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
            description="Student self score read failed: invalid token data",
        )
        raise InvalidToken()

    service = StudentService(session)
    score_data = await service.get_student_self_scores(user_id)
    await create_api_log(
        session=session,
        user_id=user_uuid,
        uri_path=str(request.url.path),
        result=True,
        description="Student self score read succeeded",
    )
    return StudentSelfScoreResponse(**score_data)
