from fastapi import APIRouter, Request

from app.api.v1.services.kbri_service import KbriService
from app.api.v1.services.response_service import ResponseService

router = APIRouter()
kbri_service = KbriService()
response_service = ResponseService()


@router.get("/")
async def get_schedule(request: Request, limit: int = 1):
    return response_service.to_response(
        request,
        await kbri_service.get_schedule(limit),
    )
