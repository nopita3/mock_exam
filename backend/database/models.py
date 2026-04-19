from pydantic import EmailStr
from sqlmodel import Column, Field, Relationship, SQLModel, text
from uuid import UUID , uuid4

from backend.api.schemas.users import Roles , TeacherDepartment , StudentDepartment
from sqlalchemy.dialects import postgresql


class User(SQLModel, table = True):
    __tablename__ = "user"

    id: UUID = Field(sa_column=Column(postgresql.UUID, primary_key=True, default=uuid4))
    user_id: str = Field(unique=True)
    fname: str 
    lname: str 
    nname: str
    role: Roles 
    email: EmailStr = Field(unique=True)
    email_validated: bool = Field(default=False, 
                                  sa_column_kwargs={"server_default": text("false")})

    student_back: "Student" = Relationship(
        back_populates="id_back",
        sa_relationship_kwargs={"foreign_keys": "Student.StudentID"}
    )

    teacher_back: "Teacher" = Relationship(
        back_populates="id_back",
        sa_relationship_kwargs={"foreign_keys": "Teacher.TeacherID"}
    )


class Student(SQLModel, table = True):

    __tablename__ = "student"

    StudentID: str = Field(unique=True , foreign_key = "user.user_id")
    fname: str 
    lname: str 
    nname: str 
    department: StudentDepartment 
    role: str = Field(default="student" , 
                      sa_column_kwargs={"server_default": "student"})

    id_back: "User" = Relationship(
        back_populates="student_back",
        sa_relationship_kwargs={"foreign_keys": "Student.StudentID"}
    )

class Teacher(SQLModel, table = True):

    __tablename__ = "teacher"

    TeacherID: str = Field(unique=True , foreign_key = "user.user_id")
    fname: str 
    lname: str 
    nname: str 
    department: TeacherDepartment 
    role: str = Field(default="teacher" , 
                      sa_column_kwargs={"server_default": "teacher"})

    id_back: "User" = Relationship(
        back_populates="teacher_back",
        sa_relationship_kwargs={"foreign_keys": "Teacher.TeacherID"}
    )