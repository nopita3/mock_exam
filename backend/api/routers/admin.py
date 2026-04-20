from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas.users import (
    AdminRegisterRequest,
    AdminRegisterResponse,
    AdminLogListResponse,
    AdminUpdateStudentRequest,
    AdminUpdateTeacherRequest,
    MessageResponse,
    ScoreEditRequest,
    ScoreUploadResponse,
    StudentSelfScoreResponse,
    UserProfileResponse,
    StudentRegisterResponse,
    TeacherAllStudentScoresResponse,
    TeacherRegisterResponse,
)
from backend.cores.exception import InvalidToken
from backend.cores.security import verify_admin_complex_code, verify_token
from backend.database.sessions import get_session
from backend.services.admin import AdminService
from backend.utils import create_api_log


router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/{complex_code}/regist", response_model=AdminRegisterResponse)
async def regist_admin(
    complex_code: str,
    payload: AdminRegisterRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    _valid_complex_code: None = Depends(verify_admin_complex_code),
    session: AsyncSession = Depends(get_session),
):
    service = AdminService(session)
    user = await service.register_admin(
        payload,
        complex_code=complex_code,
        background_tasks=background_tasks,
    )
    await create_api_log(
        session=session,
        user_id=getattr(user, "id", None),
        uri_path=str(request.url.path),
        result=True,
        description="Admin registration succeeded",
    )
    return AdminRegisterResponse(
        user_id=user.user_id,
        email=user.email,
        fname=user.fname,
        lname=user.lname,
        nname=user.nname,
    )


@router.get("/{complex_code}/logs", response_model=AdminLogListResponse)
async def get_logs_as_admin(
    complex_code: str,
    request: Request,
    _valid_complex_code: None = Depends(verify_admin_complex_code),
    token_data: dict = Depends(verify_token),
    session: AsyncSession = Depends(get_session),
):
    admin_user_id = token_data.get("user", {}).get("user_id")
    user_uuid = token_data.get("user", {}).get("id")
    if not admin_user_id:
        await create_api_log(
            session=session,
            user_id=user_uuid,
            uri_path=str(request.url.path),
            result=False,
            description="Admin log read failed: invalid token data",
        )
        raise InvalidToken()

    service = AdminService(session)
    log_data = await service.get_logs_for_admin(admin_user_id)
    await create_api_log(
        session=session,
        user_id=user_uuid,
        uri_path=str(request.url.path),
        result=True,
        description="Admin log read succeeded",
    )
    return AdminLogListResponse(**log_data)


@router.get("/{complex_code}/score/students", response_model=TeacherAllStudentScoresResponse)
async def get_all_student_scores_as_admin(
    complex_code: str,
    request: Request,
    _valid_complex_code: None = Depends(verify_admin_complex_code),
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
            description="Admin score list read failed: invalid token data",
        )
        raise InvalidToken()

    service = AdminService(session)
    score_data = await service.get_all_student_scores_for_teacher(user_id)
    await create_api_log(
        session=session,
        user_id=user_uuid,
        uri_path=str(request.url.path),
        result=True,
        description="Admin score list read succeeded",
    )
    return TeacherAllStudentScoresResponse(**score_data)


@router.post("/{complex_code}/score/upload", response_model=ScoreUploadResponse)
async def upload_scores_as_admin(
    complex_code: str,
    request: Request,
    exam_name: str = Form(...),
    exam_round: str = Form(...),
    test_date: str = Form(...),
    file: UploadFile = File(...),
    _valid_complex_code: None = Depends(verify_admin_complex_code),
    token_data: dict = Depends(verify_token),
    session: AsyncSession = Depends(get_session),
):
    admin_user_id = token_data.get("user", {}).get("user_id")
    user_uuid = token_data.get("user", {}).get("id")
    if not admin_user_id:
        await create_api_log(
            session=session,
            user_id=user_uuid,
            uri_path=str(request.url.path),
            result=False,
            description="Admin score upload failed: invalid token data",
        )
        raise InvalidToken()

    service = AdminService(session)
    upload_result = await service.upload_exam_scores_for_admin(
        admin_user_id=admin_user_id,
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
        description="Admin score upload succeeded",
    )
    return ScoreUploadResponse(**upload_result)


@router.get("/{complex_code}/student/{student_user_id}", response_model=UserProfileResponse)
async def get_student_by_admin(
    complex_code: str,
    student_user_id: str,
    request: Request,
    _valid_complex_code: None = Depends(verify_admin_complex_code),
    token_data: dict = Depends(verify_token),
    session: AsyncSession = Depends(get_session),
):
    admin_user_id = token_data.get("user", {}).get("user_id")
    user_uuid = token_data.get("user", {}).get("id")
    if not admin_user_id:
        await create_api_log(
            session=session,
            user_id=user_uuid,
            uri_path=str(request.url.path),
            result=False,
            description="Admin student read failed: invalid token data",
        )
        raise InvalidToken()

    service = AdminService(session)
    profile = await service.get_student_by_admin(admin_user_id, student_user_id)
    await create_api_log(
        session=session,
        user_id=user_uuid,
        uri_path=str(request.url.path),
        result=True,
        description="Admin student read succeeded",
    )
    return UserProfileResponse(**profile)


@router.get("/{complex_code}/teacher/{teacher_user_id}", response_model=UserProfileResponse)
async def get_teacher_by_admin(
    complex_code: str,
    teacher_user_id: str,
    request: Request,
    _valid_complex_code: None = Depends(verify_admin_complex_code),
    token_data: dict = Depends(verify_token),
    session: AsyncSession = Depends(get_session),
):
    admin_user_id = token_data.get("user", {}).get("user_id")
    user_uuid = token_data.get("user", {}).get("id")
    if not admin_user_id:
        await create_api_log(
            session=session,
            user_id=user_uuid,
            uri_path=str(request.url.path),
            result=False,
            description="Admin teacher read failed: invalid token data",
        )
        raise InvalidToken()

    service = AdminService(session)
    profile = await service.get_teacher_by_admin(admin_user_id, teacher_user_id)
    await create_api_log(
        session=session,
        user_id=user_uuid,
        uri_path=str(request.url.path),
        result=True,
        description="Admin teacher read succeeded",
    )
    return UserProfileResponse(**profile)


@router.put("/{complex_code}/student/{student_user_id}", response_model=StudentRegisterResponse)
async def update_student_by_admin(
    complex_code: str,
    student_user_id: str,
    payload: AdminUpdateStudentRequest,
    request: Request,
    _valid_complex_code: None = Depends(verify_admin_complex_code),
    token_data: dict = Depends(verify_token),
    session: AsyncSession = Depends(get_session),
):
    admin_user_id = token_data.get("user", {}).get("user_id")
    user_uuid = token_data.get("user", {}).get("id")
    if not admin_user_id:
        await create_api_log(
            session=session,
            user_id=user_uuid,
            uri_path=str(request.url.path),
            result=False,
            description="Admin student update failed: invalid token data",
        )
        raise InvalidToken()

    service = AdminService(session)
    update_data = payload.model_dump(exclude_unset=True)
    user = await service.update_student_by_admin(admin_user_id, student_user_id, update_data)
    await create_api_log(
        session=session,
        user_id=user_uuid,
        uri_path=str(request.url.path),
        result=True,
        description="Admin student update succeeded",
    )
    return StudentRegisterResponse(**user)


@router.delete("/{complex_code}/student/{student_user_id}", response_model=MessageResponse)
async def delete_student_by_admin(
    complex_code: str,
    student_user_id: str,
    request: Request,
    _valid_complex_code: None = Depends(verify_admin_complex_code),
    token_data: dict = Depends(verify_token),
    session: AsyncSession = Depends(get_session),
):
    admin_user_id = token_data.get("user", {}).get("user_id")
    user_uuid = token_data.get("user", {}).get("id")
    if not admin_user_id:
        await create_api_log(
            session=session,
            user_id=user_uuid,
            uri_path=str(request.url.path),
            result=False,
            description="Admin student delete failed: invalid token data",
        )
        raise InvalidToken()

    service = AdminService(session)
    await service.delete_student_by_admin(admin_user_id, student_user_id)
    await create_api_log(
        session=session,
        user_id=user_uuid,
        uri_path=str(request.url.path),
        result=True,
        description="Admin student delete succeeded",
    )
    return MessageResponse(detail="Student deleted successfully")


@router.put("/{complex_code}/teacher/{teacher_user_id}", response_model=TeacherRegisterResponse)
async def update_teacher_by_admin(
    complex_code: str,
    teacher_user_id: str,
    payload: AdminUpdateTeacherRequest,
    request: Request,
    _valid_complex_code: None = Depends(verify_admin_complex_code),
    token_data: dict = Depends(verify_token),
    session: AsyncSession = Depends(get_session),
):
    admin_user_id = token_data.get("user", {}).get("user_id")
    user_uuid = token_data.get("user", {}).get("id")
    if not admin_user_id:
        await create_api_log(
            session=session,
            user_id=user_uuid,
            uri_path=str(request.url.path),
            result=False,
            description="Admin teacher update failed: invalid token data",
        )
        raise InvalidToken()

    service = AdminService(session)
    update_data = payload.model_dump(exclude_unset=True)
    user = await service.update_teacher_by_admin(admin_user_id, teacher_user_id, update_data)
    await create_api_log(
        session=session,
        user_id=user_uuid,
        uri_path=str(request.url.path),
        result=True,
        description="Admin teacher update succeeded",
    )
    return TeacherRegisterResponse(**user)


@router.delete("/{complex_code}/teacher/{teacher_user_id}", response_model=MessageResponse)
async def delete_teacher_by_admin(
    complex_code: str,
    teacher_user_id: str,
    request: Request,
    _valid_complex_code: None = Depends(verify_admin_complex_code),
    token_data: dict = Depends(verify_token),
    session: AsyncSession = Depends(get_session),
):
    admin_user_id = token_data.get("user", {}).get("user_id")
    user_uuid = token_data.get("user", {}).get("id")
    if not admin_user_id:
        await create_api_log(
            session=session,
            user_id=user_uuid,
            uri_path=str(request.url.path),
            result=False,
            description="Admin teacher delete failed: invalid token data",
        )
        raise InvalidToken()

    service = AdminService(session)
    await service.delete_teacher_by_admin(admin_user_id, teacher_user_id)
    await create_api_log(
        session=session,
        user_id=user_uuid,
        uri_path=str(request.url.path),
        result=True,
        description="Admin teacher delete succeeded",
    )
    return MessageResponse(detail="Teacher deleted successfully")


@router.get("/{complex_code}/score/student/{student_id}", response_model=StudentSelfScoreResponse)
async def get_scores_for_student_by_admin(
    complex_code: str,
    student_id: str,
    request: Request,
    _valid_complex_code: None = Depends(verify_admin_complex_code),
    token_data: dict = Depends(verify_token),
    session: AsyncSession = Depends(get_session),
):
    admin_user_id = token_data.get("user", {}).get("user_id")
    user_uuid = token_data.get("user", {}).get("id")
    if not admin_user_id:
        await create_api_log(
            session=session,
            user_id=user_uuid,
            uri_path=str(request.url.path),
            result=False,
            description="Admin score read failed: invalid token data",
        )
        raise InvalidToken()

    service = AdminService(session)
    score_data = await service.get_scores_for_student_by_admin(admin_user_id, student_id)
    await create_api_log(
        session=session,
        user_id=user_uuid,
        uri_path=str(request.url.path),
        result=True,
        description="Admin score read succeeded",
    )
    return StudentSelfScoreResponse(**score_data)


@router.put("/{complex_code}/score/student/{student_id}", response_model=StudentSelfScoreResponse)
async def replace_scores_for_student_by_admin(
    complex_code: str,
    student_id: str,
    payload: ScoreEditRequest,
    request: Request,
    _valid_complex_code: None = Depends(verify_admin_complex_code),
    token_data: dict = Depends(verify_token),
    session: AsyncSession = Depends(get_session),
):
    admin_user_id = token_data.get("user", {}).get("user_id")
    user_uuid = token_data.get("user", {}).get("id")
    if not admin_user_id:
        await create_api_log(
            session=session,
            user_id=user_uuid,
            uri_path=str(request.url.path),
            result=False,
            description="Admin score update failed: invalid token data",
        )
        raise InvalidToken()

    service = AdminService(session)
    score_data = await service.replace_scores_for_student_by_admin(
        admin_user_id,
        student_id,
        [item.model_dump() for item in payload.scores],
    )
    await create_api_log(
        session=session,
        user_id=user_uuid,
        uri_path=str(request.url.path),
        result=True,
        description="Admin score update succeeded",
    )
    return StudentSelfScoreResponse(**score_data)


@router.delete("/{complex_code}/score/student/{student_id}", response_model=MessageResponse)
async def delete_scores_for_student_by_admin(
    complex_code: str,
    student_id: str,
    request: Request,
    _valid_complex_code: None = Depends(verify_admin_complex_code),
    token_data: dict = Depends(verify_token),
    session: AsyncSession = Depends(get_session),
):
    admin_user_id = token_data.get("user", {}).get("user_id")
    user_uuid = token_data.get("user", {}).get("id")
    if not admin_user_id:
        await create_api_log(
            session=session,
            user_id=user_uuid,
            uri_path=str(request.url.path),
            result=False,
            description="Admin score delete failed: invalid token data",
        )
        raise InvalidToken()

    service = AdminService(session)
    await service.delete_scores_for_student_by_admin(admin_user_id, student_id)
    await create_api_log(
        session=session,
        user_id=user_uuid,
        uri_path=str(request.url.path),
        result=True,
        description="Admin score delete succeeded",
    )
    return MessageResponse(detail="Scores deleted successfully")
