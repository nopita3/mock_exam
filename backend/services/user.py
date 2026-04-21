
from typing import Any

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from fastapi import BackgroundTasks
import httpx

from backend.cores.exception import ClientNotAuthorized, ClientNotVerified, InvalidToken, EntityAlreadyExists, EntityNotAllowed, EntityNotFound
from backend.services.base import BaseService
from backend.services.email import EmailService
from backend.config import app_settings, oauth_settings

from backend.api.schemas.users import BaseUser, Roles
from backend.database.models import Student, Teacher, User
from backend.utils import decode_email_token, generate_access_token, generate_email_token 

email_service = EmailService()

class UserService(BaseService):
    def __init__(self, session: AsyncSession ):
        super().__init__(User, session)
        self.session = session

    @staticmethod
    def _normalize_email(email: str) -> str:
        return str(email).strip().lower()

    def _is_allowed_email_domain(self, email: str) -> bool:
        normalized_email = self._normalize_email(email)
        allowed_domain = str(app_settings.ALLOWED_EMAIL_DOMAIN).strip().lower().lstrip("@")
        return normalized_email.endswith(f"@{allowed_domain}")

    def _ensure_allowed_email_domain(self, email: str) -> None:
        if not self._is_allowed_email_domain(email):
            raise EntityNotAllowed()
        
        

    async def add(self, credentials: BaseUser, background_tasks: BackgroundTasks | None = None ) -> BaseUser:
        self._ensure_allowed_email_domain(credentials.email)
        user = User(
            user_id=credentials.userID,
            fname=credentials.fname,
            lname=credentials.lname,
            nname=credentials.nname,
            role=getattr(credentials, "role", Roles.STUDENT),
            email=credentials.email,
            email_validated=False,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        await self._send_verification_email(user, background_tasks)
      
        return user

    async def _send_verification_email(self, user: User, background_tasks: BackgroundTasks | None = None) -> None:
        token = generate_email_token(
            {"id": str(user.id), "email": user.email},
            salt="email-confirmation-salt",
        )
        email_payload = {
            "recipients": [user.email],
            "subject": "Verify your tracking system account",
            "context": {
                "name": user.fname,
                "email": user.email,
                "verify_url": f"{app_settings.frontend_app_domain}/auth/verification-complete?token={token}",
            },
            "template_name": "verification.html",
        }
        if background_tasks is not None:
            background_tasks.add_task(email_service.send_message, **email_payload)
        else:
            await email_service.send_message(**email_payload)

    async def resend_verification_email(self, email: str, background_tasks: BackgroundTasks | None = None) -> None:
        self._ensure_allowed_email_domain(email)
        user = await self._get_by_email(email)
        if user is None:
            raise EntityNotFound()

        if user.email_validated:
            return

        await self._send_verification_email(user, background_tasks)
    
    async def verify_email(self , token: str):
        data = decode_email_token(token , salt="email-confirmation-salt" ,)
        

        if data is None:
            raise InvalidToken()
        
        user = await self._get(UUID(data["id"]))
        if user is None:
            raise EntityNotFound()
        user.email_validated = True
        await self._update(user)

        return data
       
        
    async def google_login(self, id_token: str, background_tasks: BackgroundTasks | None = None) -> str:
        payload = await self._verify_google_id_token(id_token)
        email = self._normalize_email(payload["email"])
        user = await self._get_by_email(email)

        if user is None:
            raise ClientNotAuthorized()

        if not user.email_validated:
            await self._send_verification_email(user, background_tasks)
            raise ClientNotVerified()

        data = {
            "user": {
                "nname": user.nname,
                "fname": user.fname,
                "lname": user.lname,
                "email": user.email,
                "role": user.role,
                "user_id": user.user_id,
                "id": str(user.id),
            }
        }
        return generate_access_token(data)

    async def _verify_google_id_token(self, id_token: str) -> dict:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://oauth2.googleapis.com/tokeninfo",
                    params={"id_token": id_token},
                )
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError):
            raise InvalidToken()

        if payload.get("aud") != oauth_settings.GOOGLE_CLIENT_ID:
            raise InvalidToken()

        issuer = payload.get("iss")
        if issuer not in {"accounts.google.com", "https://accounts.google.com"}:
            raise InvalidToken()

        if str(payload.get("email_verified")).lower() != "true":
            raise InvalidToken()

        email = payload.get("email")
        if not email:
            raise InvalidToken()

        if not self._is_allowed_email_domain(email):
            raise InvalidToken()

        return payload

    async def token(self, email: str) -> str:
        result = await self.session.execute(
            select(User).where(User.email == email)
            )
        user = result.scalar()

        if user is None:
            raise InvalidToken()

        if not user.email_validated:
            raise ClientNotVerified()
            
        
        data = {"user":{"nname":user.nname ,
                        "fname":user.fname,
                        "lname":user.lname,
                        "email":user.email,
                        "role": user.role,
                        "user_id": user.user_id,
                        "id": str(user.id)}}
        
        token = generate_access_token(data)
        
        return token
    
    async def _get_by_email(self, email: EmailStr) :
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar()
        return user

    @staticmethod
    def _normalize_role(role: Any) -> str:
        value = getattr(role, "value", role)
        return str(value).lower()

    async def _require_roles(self, user_id: str, allowed_roles: set[str]) -> User:
        result = await self.session.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalar()

        if user is None:
            raise EntityNotFound()

        if self._normalize_role(user.role) not in allowed_roles:
            raise ClientNotAuthorized()

        return user

    async def get_user_data(self, user_id: str) -> dict[str, Any]:
        """Get user profile with role-specific data from student/teacher tables."""
        result = await self.session.execute(
            select(User).where(User.user_id == user_id)
        )
        user = result.scalar()

        if user is None:
            raise EntityNotFound()

        return await self._build_user_profile(user)

    async def get_user_data_by_user_id(self, target_user_id: str) -> dict[str, Any]:
        result = await self.session.execute(
            select(User).where(User.user_id == target_user_id)
        )
        user = result.scalar()

        if user is None:
            raise EntityNotFound()

        return await self._build_user_profile(user)

    async def _build_user_profile(self, user: User) -> dict[str, Any]:

        profile: dict[str, Any] = {
            "id": str(user.id),
            "user_id": user.user_id,
            "email": user.email,
            "fname": user.fname,
            "lname": user.lname,
            "nname": user.nname,
            "role": user.role,
            "email_validated": user.email_validated,
        }

        if user.role == Roles.STUDENT:
            student_result = await self.session.execute(
                select(Student).where(Student.StudentID == user.user_id)
            )
            student = student_result.scalar()
            if student is None:
                raise EntityNotFound()

            profile["department"] = student.department
            profile["classroom"] = student.classroom
            profile["level"] = student.level
            profile["table_role"] = student.role
            return profile

        if user.role == Roles.TEACHER:
            teacher_result = await self.session.execute(
                select(Teacher).where(Teacher.TeacherID == user.user_id)
            )
            teacher = teacher_result.scalar()
            if teacher is None:
                raise EntityNotFound()

            profile["department"] = teacher.department
            profile["table_role"] = teacher.role
            return profile

        if user.role == Roles.ADMIN:
            teacher_result = await self.session.execute(
                select(Teacher).where(Teacher.TeacherID == user.user_id)
            )
            teacher = teacher_result.scalar()
            if teacher is not None:
                profile["department"] = teacher.department
                profile["table_role"] = teacher.role
            return profile

        return profile
    
    
        
    

