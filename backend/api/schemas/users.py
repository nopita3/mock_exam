from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator

class Roles(str , Enum):
    TEACHER = "teacher"
    ADMIN = "admin"
    STUDENT = "student"
    student = "student"

class RolesTeacher(str , Enum):
    teacher = "teacher"
    care = "care supervisor"

class RolesStudent(str , Enum):
    student = "student"

class TeacherDepartment(str , Enum):
    physics = "physics"
    chemistry = "chemistry"
    biology = "biology"
    math = "mathematics"
    thai = 'Thai'
    english = 'English'
    social = 'social'
    computer = 'computer'
    care = 'care supervisor'

class StudentDepartment(str , Enum):
    med = 'Medical Science'
    app = 'Applied Science'
    soc = 'Social Science'



class BaseUser(BaseModel):

    email: EmailStr
    userID: str
    fname: str 
    lname: str 
    nname: str 

    @field_validator("email")
    @classmethod
    def validate_essence_domain(cls, value: EmailStr) -> EmailStr:
        if not str(value).lower().endswith("@essence.ac.th"):
            raise ValueError("email must use @essence.ac.th domain")
        return value
    
class TeacherCreate(BaseUser):
    role: RolesTeacher
    department: TeacherDepartment

    
class StudentCreate(BaseUser):
    role: RolesStudent
    department: StudentDepartment


class StudentRegisterRequest(BaseUser):
    department: StudentDepartment
    classroom: Optional[str] = None
    level: Optional[int] = None

    @field_validator("classroom")
    @classmethod
    def validate_classroom(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = value.strip().upper()
        if len(normalized) != 1 or not normalized.isascii() or not normalized.isalpha():
            raise ValueError("classroom must be exactly one English alphabet character")
        return normalized

    @field_validator("level")
    @classmethod
    def validate_level(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return value
        if value >= 10:
            raise ValueError("level must be an integer less than 10")
        return value


class StudentRegisterResponse(BaseModel):
    user_id: str
    email: EmailStr
    fname: str
    lname: str
    nname: str
    role: RolesStudent = RolesStudent.student
    department: StudentDepartment
    classroom: Optional[str] = None
    level: Optional[int] = None


class TeacherRegisterRequest(BaseUser):
    department: TeacherDepartment


class TeacherRegisterResponse(BaseModel):
    user_id: str
    email: EmailStr
    fname: str
    lname: str
    nname: str
    role: RolesTeacher = RolesTeacher.teacher
    department: TeacherDepartment


class AdminRegisterRequest(BaseUser):
    pass


class AdminRegisterResponse(BaseModel):
    user_id: str
    email: EmailStr
    fname: str
    lname: str
    nname: str
    role: Roles = Roles.ADMIN


class GoogleLoginRequest(BaseModel):
    id_token: str


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class MessageResponse(BaseModel):
    detail: str


class UserProfileResponse(BaseModel):
    id: str
    user_id: str
    email: EmailStr
    fname: str
    lname: str
    nname: str
    role: Roles
    email_validated: bool
    department: Optional[str] = None
    classroom: Optional[str] = None
    level: Optional[int] = None
    table_role: Optional[str] = None


class StudentScoreItemResponse(BaseModel):
    exam_id: str
    student_id: str
    exam_name: str
    exam_round: str
    test_date: str
    score: float


class StudentSelfScoreResponse(BaseModel):
    user_id: str
    scores: list[StudentScoreItemResponse]


class TeacherAllStudentScoresResponse(BaseModel):
    scores: list[StudentScoreItemResponse]


class ScoreUploadResponse(BaseModel):
    exam_id: str
    exam_name: str
    exam_round: str
    test_date: str
    inserted_rows: int
    skipped_rows: int


class ScoreEditItemRequest(BaseModel):
    exam_name: str
    exam_round: str
    test_date: str
    score: float


class ScoreEditRequest(BaseModel):
    scores: list[ScoreEditItemRequest]


class AdminUpdateStudentRequest(BaseModel):
    email: Optional[EmailStr] = None
    fname: Optional[str] = None
    lname: Optional[str] = None
    nname: Optional[str] = None
    department: Optional[StudentDepartment] = None
    classroom: Optional[str] = None
    level: Optional[int] = None

    @field_validator("classroom")
    @classmethod
    def validate_classroom(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = value.strip().upper()
        if len(normalized) != 1 or not normalized.isascii() or not normalized.isalpha():
            raise ValueError("classroom must be exactly one English alphabet character")
        return normalized

    @field_validator("level")
    @classmethod
    def validate_level(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return value
        if value >= 10:
            raise ValueError("level must be an integer less than 10")
        return value


class AdminUpdateTeacherRequest(BaseModel):
    email: Optional[EmailStr] = None
    fname: Optional[str] = None
    lname: Optional[str] = None
    nname: Optional[str] = None
    department: Optional[TeacherDepartment] = None


class AdminLogItemResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    uri_path: str
    result: bool
    description: str


class AdminLogListResponse(BaseModel):
    logs: list[AdminLogItemResponse]
    









    








