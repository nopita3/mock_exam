
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import  select
from uuid import UUID
from fastapi import BackgroundTasks
import httpx

from backend.cores.exception import ClientNotVerified, InvalidToken, EntityAlreadyExists, EntityNotAllowed, EntityNotFound
from backend.services.base import BaseService
from backend.services.email import EmailService
from backend.config import app_settings, oauth_settings

from backend.api.schemas.users import BaseUser, Roles, StudentRegisterRequest, TeacherRegisterRequest
from backend.database.models import Student, Teacher, User
from backend.utils import decode_email_token, generate_access_token, generate_email_token 

email_service = EmailService()

class UserService(BaseService):
    def __init__(self, session: AsyncSession ):
        super().__init__(User, session)
        self.session = session
        
        

    async def add(self, credentials: BaseUser, background_tasks: BackgroundTasks | None = None ) -> BaseUser:
        user = User(
            user_id=credentials.userID,
            fname=credentials.fname,
            lname=credentials.lname,
            nname=credentials.nname,
            role=getattr(credentials, "role", Roles.student),
            email=credentials.email,
            email_validated=False,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)

        await self._send_verification_email(user, background_tasks)
      
        return user

    async def register_student(self, payload: StudentRegisterRequest, background_tasks: BackgroundTasks | None = None) -> User:
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
            role=Roles.student,
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

    async def register_teacher(
        self,
        payload: TeacherRegisterRequest,
        complex_code: str,
        background_tasks: BackgroundTasks | None = None,
    ) -> User:
        if complex_code != app_settings.TEACHER_REGIST_COMPLEX_CODE:
            raise EntityNotAllowed()

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
                "verify_url": f"{app_settings.app_domain}/auth/verify?token={token}",
            },
            "template_name": "verification.html",
        }
        if background_tasks is not None:
            background_tasks.add_task(email_service.send_message, **email_payload)
        else:
            await email_service.send_message(**email_payload)
    
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
        email = payload["email"]
        user = await self._get_by_email(email)

        if user is None:
            user = User(
                user_id=payload["sub"],
                fname=payload.get("given_name") or payload.get("name") or email.split("@")[0],
                lname=payload.get("family_name") or "",
                nname=payload.get("given_name") or payload.get("name") or email.split("@")[0],
                role=Roles.student,
                email=email,
                email_validated=False,
            )
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            await self._send_verification_email(user, background_tasks)
            raise ClientNotVerified()

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
        if not email or not email.endswith("@essence.ac.th"):
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
    
    
        
    

