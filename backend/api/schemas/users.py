from enum import Enum
from pydantic import BaseModel, EmailStr

class Roles(str , Enum):
    TEACHER = "teacher"
    ADMIN = "admin"
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
    
class TeacherCreate(BaseUser):
    role: RolesTeacher
    department: TeacherDepartment

    
class StudentCreate(BaseUser):
    role: RolesStudent
    department: StudentDepartment


class StudentRegisterRequest(BaseUser):
    department: StudentDepartment


class StudentRegisterResponse(BaseModel):
    user_id: str
    email: EmailStr
    fname: str
    lname: str
    nname: str
    role: RolesStudent = RolesStudent.student
    department: StudentDepartment


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


class GoogleLoginRequest(BaseModel):
    id_token: str


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    detail: str
    









    








