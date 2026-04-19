from fastapi import APIRouter

from backend.api.routers import admin, auth, teacher, student




# api router to group endpoints
master_router = APIRouter()

master_router.include_router(auth.router)
master_router.include_router(teacher.router)
master_router.include_router(student.router)
master_router.include_router(admin.router)

