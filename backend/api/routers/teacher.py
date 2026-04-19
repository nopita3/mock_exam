from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas.users import ScoreUploadResponse, TeacherAllStudentScoresResponse, TeacherRegisterRequest, TeacherRegisterResponse
from backend.cores.exception import InvalidToken
from backend.cores.security import verify_teacher_complex_code, verify_token
from backend.database.sessions import get_session
from backend.services.teacher import TeacherService
from backend.utils import create_api_log


router = APIRouter(prefix="/teacher", tags=["teacher"])


@router.post("/{complex_code}/regist", response_model=TeacherRegisterResponse)
async def regist_teacher(
    complex_code: str,
    payload: TeacherRegisterRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    _valid_complex_code: None = Depends(verify_teacher_complex_code),
    session: AsyncSession = Depends(get_session),
):
    service = TeacherService(session)
    user = await service.register_teacher(
        payload,
        complex_code=complex_code,
        background_tasks=background_tasks,
    )
    await create_api_log(
        session=session,
        user_id=getattr(user, "id", None),
        uri_path=str(request.url.path),
        result=True,
        description="Teacher registration succeeded",
    )
    return TeacherRegisterResponse(
        user_id=user.user_id,
        email=user.email,
        fname=user.fname,
        lname=user.lname,
        nname=user.nname,
        department=payload.department,
    )


@router.get("/{complex_code}/score/students", response_model=TeacherAllStudentScoresResponse)
async def get_all_student_scores(
    complex_code: str,
    request: Request,
    _valid_complex_code: None = Depends(verify_teacher_complex_code),
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
            description="Teacher score list read failed: invalid token data",
        )
        raise InvalidToken()

    service = TeacherService(session)
    score_data = await service.get_all_student_scores_for_teacher(user_id)
    await create_api_log(
        session=session,
        user_id=user_uuid,
        uri_path=str(request.url.path),
        result=True,
        description="Teacher score list read succeeded",
    )
    return TeacherAllStudentScoresResponse(**score_data)


@router.post("/{complex_code}/score/upload", response_model=ScoreUploadResponse)
async def upload_scores(
    complex_code: str,
    request: Request,
    exam_name: str = Form(...),
    exam_round: str = Form(...),
    test_date: str = Form(...),
    file: UploadFile = File(...),
    _valid_complex_code: None = Depends(verify_teacher_complex_code),
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
            description="Teacher score upload failed: invalid token data",
        )
        raise InvalidToken()

    service = TeacherService(session)
    upload_result = await service.upload_exam_scores_for_teacher(
        user_id=user_id,
        exam_name=exam_name,
        exam_round=exam_round,
        test_date=test_date,
        upload_file=file,
    )
    await create_api_log(
        session=session,
        user_id=user_uuid,
        uri_path=str(request.url.path),
        result=True,
        description="Teacher score upload succeeded",
    )
    return ScoreUploadResponse(**upload_result)


