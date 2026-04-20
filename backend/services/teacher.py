from typing import Any
from uuid import uuid4
from io import BytesIO
from datetime import date, datetime

from fastapi import BackgroundTasks, UploadFile
import pandas as pd
from sqlalchemy import delete, select

from backend.api.schemas.users import Roles, TeacherRegisterRequest
from backend.config import app_settings
from backend.cores.exception import EntityAlreadyExists, EntityNotAllowed, EntityNotFound
from backend.database.models import Score, Student, Teacher, User
from backend.services.user import UserService


class TeacherService(UserService):
    @staticmethod
    def _parse_test_date(value: str) -> date:
        normalized_value = str(value).strip()
        for date_format in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(normalized_value, date_format).date()
            except (TypeError, ValueError):
                continue
        raise EntityNotAllowed()

    @staticmethod
    def _normalize_column_name(name: str) -> str:
        return "".join(ch for ch in name.lower().strip() if ch.isalnum())

    @classmethod
    def _find_required_columns(cls, columns: list[str]) -> tuple[str, str]:
        normalized_to_original = {
            cls._normalize_column_name(col): col for col in columns
        }

        student_col = normalized_to_original.get("studentid")
        score_col = normalized_to_original.get("earnedpoints")

        if student_col is None or score_col is None:
            raise EntityNotAllowed()

        return student_col, score_col

    @staticmethod
    def _normalize_student_id(value: Any) -> str:
        raw_value: str
        if isinstance(value, float) and value.is_integer():
            raw_value = str(int(value))
        else:
            raw_value = str(value).strip()

        if not raw_value:
            return ""

        if raw_value.lower().startswith("e"):
            return f"E{raw_value[1:]}"

        return f"E{raw_value}"

    async def _read_score_dataframe(self, upload_file: UploadFile) -> pd.DataFrame:
        filename = (upload_file.filename or "").lower()
        content = await upload_file.read()
        stream = BytesIO(content)

        try:
            if filename.endswith(".csv"):
                return pd.read_csv(stream)
            if filename.endswith(".xlsx") or filename.endswith(".xls"):
                return pd.read_excel(stream)
        except Exception:
            raise EntityNotAllowed()

        raise EntityNotAllowed()

    async def _create_exam_scores(
        self,
        exam_name: str,
        exam_round: str,
        test_date: str,
        upload_file: UploadFile,
    ) -> dict[str, Any]:
        parsed_test_date = self._parse_test_date(test_date)
        dataframe = await self._read_score_dataframe(upload_file)
        student_col, score_col = self._find_required_columns(dataframe.columns.tolist())

        parsed_rows: list[tuple[str, float]] = []
        skipped_rows = 0

        for _, row in dataframe.iterrows():
            student_id_raw = row.get(student_col)
            score_raw = row.get(score_col)

            if pd.isna(student_id_raw) or pd.isna(score_raw):
                skipped_rows += 1
                continue

            student_id = self._normalize_student_id(student_id_raw)
            if not student_id:
                skipped_rows += 1
                continue

            try:
                score_value = float(score_raw)
            except (TypeError, ValueError):
                skipped_rows += 1
                continue

            parsed_rows.append((student_id, score_value))

        if not parsed_rows:
            raise EntityNotAllowed()

        student_ids = {student_id for student_id, _ in parsed_rows}
        students_result = await self.session.execute(
            select(Student.StudentID).where(Student.StudentID.in_(student_ids))
        )
        valid_student_ids = set(students_result.scalars().all())

        score_rows: list[Score] = []
        exam_uuid = uuid4()

        for student_id, score_value in parsed_rows:
            if student_id not in valid_student_ids:
                skipped_rows += 1
                continue

            score_rows.append(
                Score(
                    exam_id=exam_uuid,
                    studentID=student_id,
                    exam_name=exam_name,
                    exam_round=exam_round,
                    test_date=parsed_test_date,
                    score=score_value,
                )
            )

        if not score_rows:
            raise EntityNotAllowed()

        self.session.add_all(score_rows)
        await self.session.commit()

        return {
            "exam_id": str(exam_uuid),
            "exam_name": exam_name,
            "exam_round": exam_round,
            "test_date": parsed_test_date.strftime("%d/%m/%Y"),
            "inserted_rows": len(score_rows),
            "skipped_rows": skipped_rows,
        }

    @staticmethod
    def _serialize_score(score: Score) -> dict[str, Any]:
        return {
            "exam_id": str(score.exam_id),
            "student_id": score.studentID,
            "exam_name": score.exam_name,
            "exam_round": score.exam_round,
            "test_date": score.test_date.strftime("%d/%m/%Y"),
            "score": score.score,
        }

    async def _require_student(self, student_id: str) -> Student:
        student_result = await self.session.execute(
            select(Student).where(Student.StudentID == student_id)
        )
        student = student_result.scalar()
        if student is None:
            raise EntityNotFound()
        return student

    async def get_scores_for_student(self, user_id: str, student_id: str) -> dict[str, Any]:
        await self._require_roles(user_id, {"teacher", "admin"})
        await self._require_student(student_id)

        score_result = await self.session.execute(
            select(Score)
            .where(Score.studentID == student_id)
            .order_by(Score.test_date.desc(), Score.exam_name.asc())
        )
        score_rows = score_result.scalars().all()

        return {
            "user_id": student_id,
            "scores": [self._serialize_score(score) for score in score_rows],
        }

    async def replace_scores_for_student(
        self,
        user_id: str,
        student_id: str,
        score_rows: list[dict[str, Any]],
    ) -> dict[str, Any]:
        await self._require_roles(user_id, {"teacher", "admin"})
        await self._require_student(student_id)

        if not score_rows:
            raise EntityNotAllowed()

        await self.session.execute(delete(Score).where(Score.studentID == student_id))

        new_rows: list[Score] = []
        for score_row in score_rows:
            new_rows.append(
                Score(
                    exam_id=uuid4(),
                    studentID=student_id,
                    exam_name=str(score_row["exam_name"]),
                    exam_round=str(score_row["exam_round"]),
                    test_date=self._parse_test_date(str(score_row["test_date"])),
                    score=float(score_row["score"]),
                )
            )

        self.session.add_all(new_rows)
        await self.session.commit()

        return {
            "user_id": student_id,
            "scores": [self._serialize_score(score) for score in new_rows],
        }

    async def delete_scores_for_student(self, user_id: str, student_id: str) -> None:
        await self._require_roles(user_id, {"teacher", "admin"})
        await self._require_student(student_id)

        await self.session.execute(delete(Score).where(Score.studentID == student_id))
        await self.session.commit()

    async def register_teacher(
        self,
        payload: TeacherRegisterRequest,
        complex_code: str,
        background_tasks: BackgroundTasks | None = None,
    ) -> User:
        if complex_code != app_settings.TEACHER_CODE:
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
            role=Roles.TEACHER,
            email=payload.email,
            email_validated=False,
        )

        teacher = Teacher(
            TeacherID=payload.userID,
            fname=payload.fname,
            lname=payload.lname,
            nname=payload.nname,
            department=payload.department,
            role="teacher",
        )

        self.session.add(user)
        self.session.add(teacher)
        await self.session.commit()
        await self.session.refresh(user)

        await self._send_verification_email(user, background_tasks)
        return user

    async def upload_exam_scores_for_teacher(
        self,
        user_id: str,
        exam_name: str,
        exam_round: str,
        test_date: str,
        upload_file: UploadFile,
    ) -> dict[str, Any]:
        await self._require_roles(user_id, {"teacher"})
        return await self._create_exam_scores(exam_name, exam_round, test_date, upload_file)

    async def get_all_student_scores_for_teacher(self, user_id: str) -> dict[str, Any]:
        await self._require_roles(user_id, {"teacher", "admin"})

        score_result = await self.session.execute(
            select(Score).order_by(Score.test_date.desc())
        )
        score_rows = score_result.scalars().all()

        return {
            "scores": [
                {
                    "exam_id": str(score.exam_id),
                    "student_id": score.studentID,
                    "exam_name": score.exam_name,
                    "exam_round": score.exam_round,
                    "test_date": score.test_date.strftime("%d/%m/%Y"),
                    "score": score.score,
                }
                for score in score_rows
            ]
        }
