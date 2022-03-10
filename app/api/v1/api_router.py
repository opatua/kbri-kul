from fastapi import APIRouter

from app.api.v1.endpoints import schedule

router = APIRouter()

router.include_router(schedule.router, prefix="/schedule", tags=["schedule"])
