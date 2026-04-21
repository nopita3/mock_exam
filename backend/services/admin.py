from typing import Any

from fastapi import BackgroundTasks
from fastapi import UploadFile
from sqlalchemy import delete, select

from backend.api.schemas.users import AdminRegisterRequest, Roles
from backend.config import app_settings
from backend.cores.exception import EntityAlreadyExists, EntityNotAllowed, EntityNotFound
from backend.database.models import Log, Score, Student, Teacher, User
from backend.services.teacher import TeacherService


class AdminService(TeacherService):
    async def register_admin(
        self,
        payload: AdminRegisterRequest,
        complex_code: str,
        background_tasks: BackgroundTasks | None = None,
    ) -> User:
        if complex_code != app_settings.ADMIN_CODE:
            raise EntityNotAllowed()

        self._ensure_allowed_email_domain(payload.email)

        existing_user = await self.session.execute(
            select(User).where((User.email == payload.email) | (User.user_id == payload.userID))
        )
        if existing_user.scalar() is not None:
            raise EntityAlreadyExists()

        user = User(
            user_id=payload.userID,
            fname=payload.fname,
            lname=payload.lname,
            nname=payload.nname,
            role=Roles.ADMIN,
            email=payload.email,
            email_validated=False,
        )

        teacher = Teacher(
            TeacherID=payload.userID,
            fname=payload.fname,
            lname=payload.lname,
            nname=payload.nname,
            department=payload.department,
            role="admin",
        )

        self.session.add(user)
        self.session.add(teacher)
        await self.session.commit()
        await self.session.refresh(user)

        await self._send_verification_email(user, background_tasks)
        return user

    async def get_logs_for_admin(self, admin_user_id: str) -> dict[str, Any]:
        await self._require_roles(admin_user_id, {"admin"})

        log_result = await self.session.execute(
            select(Log).order_by(Log.id.desc())
        )
        log_rows = log_result.scalars().all()

        return {
            "logs": [
                {
                    "id": str(log.id),
                    "user_id": str(log.user_id) if log.user_id is not None else None,
                    "uri_path": log.uri_path,
                    "result": log.result,
                    "description": log.description,
                }
                for log in log_rows
            ]
        }

    async def upload_exam_scores_for_admin(
        self,
        admin_user_id: str,
        exam_name: str,
        exam_round: str,
        test_date: str,
        upload_file: UploadFile,
    ) -> dict[str, Any]:
        await self._require_roles(admin_user_id, {"admin"})
        return await self._create_exam_scores(exam_name, exam_round, test_date, upload_file)

    async def get_student_by_admin(self, admin_user_id: str, student_user_id: str) -> dict[str, Any]:
        await self._require_roles(admin_user_id, {"admin"})
        profile = await self.get_user_data_by_user_id(student_user_id)
        if self._normalize_role(profile["role"]) != "student":
            raise EntityNotAllowed()
        return profile

    async def get_teacher_by_admin(self, admin_user_id: str, teacher_user_id: str) -> dict[str, Any]:
        await self._require_roles(admin_user_id, {"admin"})
        profile = await self.get_user_data_by_user_id(teacher_user_id)
        if self._normalize_role(profile["role"]) not in {"teacher", "admin"}:
            raise EntityNotAllowed()
        return profile

    async def get_scores_for_student_by_admin(self, admin_user_id: str, student_id: str) -> dict[str, Any]:
        await self._require_roles(admin_user_id, {"admin"})
        return await self.get_scores_for_student(admin_user_id, student_id)

    async def replace_scores_for_student_by_admin(
        self,
        admin_user_id: str,
        student_id: str,
        score_rows: list[dict[str, Any]],
    ) -> dict[str, Any]:
        await self._require_roles(admin_user_id, {"admin"})
        return await self.replace_scores_for_student(admin_user_id, student_id, score_rows)

    async def delete_scores_for_student_by_admin(self, admin_user_id: str, student_id: str) -> None:
        await self._require_roles(admin_user_id, {"admin"})
        await self.delete_scores_for_student(admin_user_id, student_id)

    async def update_student_by_admin(
        self,
        admin_user_id: str,
        student_user_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        await self._require_roles(admin_user_id, {"admin"})

        user_result = await self.session.execute(
            select(User).where(User.user_id == student_user_id)
        )
        user = user_result.scalar()
        if user is None:
            raise EntityNotFound()

        if self._normalize_role(user.role) != "student":
            raise EntityNotAllowed()

        student_result = await self.session.execute(
            select(Student).where(Student.StudentID == student_user_id)
        )
        student = student_result.scalar()
        if student is None:
            raise EntityNotFound()

        if "email" in payload and payload["email"] is not None and payload["email"] != user.email:
            self._ensure_allowed_email_domain(payload["email"])
            existing_email = await self._get_by_email(payload["email"])
            if existing_email is not None:
                raise EntityAlreadyExists()
            user.email = payload["email"]

        if "fname" in payload and payload["fname"] is not None:
            user.fname = payload["fname"]
            student.fname = payload["fname"]
        if "lname" in payload and payload["lname"] is not None:
            user.lname = payload["lname"]
            student.lname = payload["lname"]
        if "nname" in payload and payload["nname"] is not None:
            user.nname = payload["nname"]
            student.nname = payload["nname"]
        if "department" in payload and payload["department"] is not None:
            student.department = payload["department"]
        if "classroom" in payload and payload["classroom"] is not None:
            student.classroom = payload["classroom"]
        if "level" in payload and payload["level"] is not None:
            student.level = payload["level"]

        self.session.add(user)
        self.session.add(student)
        await self.session.commit()
        await self.session.refresh(user)
        await self.session.refresh(student)

        return {
            "user_id": user.user_id,
            "email": user.email,
            "fname": user.fname,
            "lname": user.lname,
            "nname": user.nname,
            "department": student.department,
            "classroom": student.classroom,
            "level": student.level,
        }

    async def update_teacher_by_admin(
        self,
        admin_user_id: str,
        teacher_user_id: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        await self._require_roles(admin_user_id, {"admin"})

        user_result = await self.session.execute(
            select(User).where(User.user_id == teacher_user_id)
        )
        user = user_result.scalar()
        if user is None:
            raise EntityNotFound()

        if self._normalize_role(user.role) not in {"teacher", "admin"}:
            raise EntityNotAllowed()

        teacher_result = await self.session.execute(
            select(Teacher).where(Teacher.TeacherID == teacher_user_id)
        )
        teacher = teacher_result.scalar()
        if teacher is None:
            raise EntityNotFound()

        if "email" in payload and payload["email"] is not None and payload["email"] != user.email:
            self._ensure_allowed_email_domain(payload["email"])
            existing_email = await self._get_by_email(payload["email"])
            if existing_email is not None:
                raise EntityAlreadyExists()
            user.email = payload["email"]

        if "fname" in payload and payload["fname"] is not None:
            user.fname = payload["fname"]
            teacher.fname = payload["fname"]
        if "lname" in payload and payload["lname"] is not None:
            user.lname = payload["lname"]
            teacher.lname = payload["lname"]
        if "nname" in payload and payload["nname"] is not None:
            user.nname = payload["nname"]
            teacher.nname = payload["nname"]
        if "department" in payload and payload["department"] is not None:
            teacher.department = payload["department"]

        self.session.add(user)
        self.session.add(teacher)
        await self.session.commit()
        await self.session.refresh(user)
        await self.session.refresh(teacher)

        return {
            "user_id": user.user_id,
            "email": user.email,
            "fname": user.fname,
            "lname": user.lname,
            "nname": user.nname,
            "department": teacher.department,
        }

    async def delete_student_by_admin(self, admin_user_id: str, student_user_id: str) -> None:
        await self._require_roles(admin_user_id, {"admin"})

        user_result = await self.session.execute(
            select(User).where(User.user_id == student_user_id)
        )
        user = user_result.scalar()
        if user is None:
            raise EntityNotFound()
        if self._normalize_role(user.role) != "student":
            raise EntityNotAllowed()

        student_result = await self.session.execute(
            select(Student).where(Student.StudentID == student_user_id)
        )
        student = student_result.scalar()
        if student is None:
            raise EntityNotFound()

        await self.session.execute(delete(Score).where(Score.studentID == student_user_id))
        await self.session.delete(student)
        await self.session.delete(user)
        await self.session.commit()

    async def delete_teacher_by_admin(self, admin_user_id: str, teacher_user_id: str) -> None:
        await self._require_roles(admin_user_id, {"admin"})

        user_result = await self.session.execute(
            select(User).where(User.user_id == teacher_user_id)
        )
        user = user_result.scalar()
        if user is None:
            raise EntityNotFound()
        if self._normalize_role(user.role) not in {"teacher", "admin"}:
            raise EntityNotAllowed()

        teacher_result = await self.session.execute(
            select(Teacher).where(Teacher.TeacherID == teacher_user_id)
        )
        teacher = teacher_result.scalar()
        if teacher is None:
            raise EntityNotFound()

        await self.session.delete(teacher)
        await self.session.delete(user)
        await self.session.commit()
