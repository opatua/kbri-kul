import json
from fastapi import APIRouter, HTTPException, Request
from http import HTTPStatus

from app.core.config import settings
from app.api.v1.services.kbri_service import KbriService
from app.api.v1.services.kbri_service import KbriService
from app.api.v1.services.response_service import ResponseService
from app.api.v1.services.third_party_service import ThirdPartyService

router = APIRouter()
kbri_service = KbriService()
third_party_service = ThirdPartyService()
response_service = ResponseService()


@router.get("/")
async def get_schedule(request: Request, limit: int = 1):
    if limit > 10:
        raise HTTPException(
            HTTPStatus.BAD_REQUEST.value,
            f'Exceeding the limit, maximum limit is 10. Please try again',
        )

    return response_service.to_response(
        request,
        await kbri_service.get_schedule(limit),
    )


@router.post("/telegram/webhook")
async def post_telegram_webhook(request: Request):
    data = await request.body()
    data = json.loads(data.decode('utf-8'))

    try:
        third_party_service.call(
            'GET',
            f"{settings.TELEGRAM_URL}/bot{settings.TELEGRAM_KEY}/sendMessage?chat_id={data['message']['chat']['id']}&text={await get_message(data['message']['text'])}",
            {}
        )
    except Exception as exception:
        print(exception)

    return response_service.to_response(
        request,
        None,
    )


async def get_message(text: str) -> str:
    if text not in [
        '/next',
        '/next@kbrikul_bot',
        '/get5',
        '/get5@kbrikul_bot',
        '/get10',
        '/get10@kbrikul_bot',
    ]:
        return'Unknown command'

    limit = 1

    if '/get5' in text:
        limit = 5

    if '/get10' in text:
        limit = 10

    slots = await kbri_service.get_schedule(limit)

    return '\n\n'.join(
        [
            f"Date: {slot['date']}\nTime: {slot['time']}"
            for slot in slots
        ],
    )
