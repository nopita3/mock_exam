from typing import Any

from fastapi import BackgroundTasks
from sqlalchemy import select

from backend.api.schemas.users import Roles, StudentRegisterRequest
from backend.cores.exception import EntityAlreadyExists
from backend.database.models import Score, Student, User
from backend.services.user import UserService


class StudentService(UserService):
    async def register_student(
        self,
        payload: StudentRegisterRequest,
        background_tasks: BackgroundTasks | None = None,
    ) -> User:
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
            role=Roles.STUDENT,
            email=payload.email,
            email_validated=False,
        )

        student = Student(
            StudentID=payload.userID,
            fname=payload.fname,
            lname=payload.lname,
            nname=payload.nname,
            department=payload.department,
            role="student",
        )

        self.session.add(user)
        self.session.add(student)
        await self.session.commit()
        await self.session.refresh(user)

        await self._send_verification_email(user, background_tasks)
        return user

    async def get_student_self_scores(self, user_id: str) -> dict[str, Any]:
        user = await self._require_roles(user_id, {"student"})

        score_result = await self.session.execute(
            select(Score)
            .where(Score.studentID == user.user_id)
            .order_by(Score.test_date.desc())
        )
        score_rows = score_result.scalars().all()

        return {
            "user_id": user.user_id,
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
            ],
        }
