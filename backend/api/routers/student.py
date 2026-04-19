from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas.users import StudentRegisterRequest, StudentRegisterResponse
from backend.database.sessions import get_session
from backend.services.user import UserService


router = APIRouter(prefix="/student", tags=["student"])


@router.post("/regist", response_model=StudentRegisterResponse)
async def regist_student(
    payload: StudentRegisterRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    service = UserService(session)
    user = await service.register_student(payload, background_tasks=background_tasks)
    return StudentRegisterResponse(
        user_id=user.user_id,
        email=user.email,
        fname=user.fname,
        lname=user.lname,
        nname=user.nname,
        department=payload.department,
    )
