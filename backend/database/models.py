from pydantic import EmailStr
from sqlmodel import Column, Field, Relationship, SQLModel, text
from uuid import UUID , uuid4
from datetime import date

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

    log_back: list["Log"] = Relationship(
        back_populates="user_back",
        sa_relationship_kwargs={"foreign_keys": "Log.user_id"}
    )


class Student(SQLModel, table = True):

    __tablename__ = "student"

    StudentID: str = Field(primary_key=True, foreign_key="user.user_id")
    fname: str 
    lname: str 
    nname: str 
    department: StudentDepartment 
    classroom: str | None = Field(default=None, max_length=1)
    level: int | None = Field(default=None)
    role: str = Field(default="student" , 
                      sa_column_kwargs={"server_default": "student"})

    id_back: "User" = Relationship(
        back_populates="student_back",
        sa_relationship_kwargs={"foreign_keys": "Student.StudentID"}
    )

    score_back: list["Score"] = Relationship(
        back_populates="student_back",
        sa_relationship_kwargs={"foreign_keys": "Score.studentID"}
    )

class Teacher(SQLModel, table = True):

    __tablename__ = "teacher"

    TeacherID: str = Field(primary_key=True, foreign_key="user.user_id")
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

class Score(SQLModel, table = True):

    __tablename__ = "score"

    exam_id: UUID = Field(sa_column=Column(postgresql.UUID, primary_key=True, index=True, nullable=False))
    studentID: str = Field(primary_key=True, foreign_key="student.StudentID")
    exam_name: str
    exam_round: str
    test_date: date
    score: float


    student_back: "Student" = Relationship(
        back_populates="score_back",
        sa_relationship_kwargs={"foreign_keys": "Score.studentID"}
    )


class Log(SQLModel, table=True):

    __tablename__ = "log"

    id: UUID = Field(sa_column=Column(postgresql.UUID, primary_key=True, default=uuid4))
    user_id: UUID | None = Field(default=None, foreign_key="user.id")
    uri_path: str
    result: bool
    description: str

    user_back: "User" = Relationship(
        back_populates="log_back",
        sa_relationship_kwargs={"foreign_keys": "Log.user_id"}
    )



    