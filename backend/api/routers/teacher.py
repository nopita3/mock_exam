from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas.users import TeacherRegisterRequest, TeacherRegisterResponse
from backend.database.sessions import get_session
from backend.services.user import UserService


router = APIRouter(prefix="/teacher", tags=["teacher"])


@router.post("/regist/{complex_code}", response_model=TeacherRegisterResponse)
async def regist_teacher(
    complex_code: str,
    payload: TeacherRegisterRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    service = UserService(session)
    user = await service.register_teacher(
        payload,
        complex_code=complex_code,
        background_tasks=background_tasks,
    )
    return TeacherRegisterResponse(
        user_id=user.user_id,
        email=user.email,
        fname=user.fname,
        lname=user.lname,
        nname=user.nname,
        department=payload.department,
    )


