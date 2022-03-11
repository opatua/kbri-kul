import json
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from app.api.v1.services.redis_service import RedisService
from app.api.v1.services.third_party_service import ThirdPartyService
from app.core.config import settings


class KbriService:
    third_party_service = ThirdPartyService()
    default_slot_limit = 10
    redis_service = RedisService()
    kbri_cache_key = 'kbri_cache'
    expire_cache = timedelta(seconds=3600)

    async def get_schedule(self, slot_limit: int) -> Optional[Dict[str, Any]]:
        redis = self.redis_service.initialize_redis()
        at = datetime.date.today()
        slots = []
        limit = self.default_slot_limit
        if slot_limit <= 10:
            limit = slot_limit

        while len(slots) < limit:
            at += timedelta(days=1)
            slot = self.get_slot(redis, at, False)
            if not slot:
                continue

            slots.append(slot)

        return slots

    async def get_cache_key(
        self, 
        at: datetime,
    ) -> str:
        formatted_date = datetime.strftime(at, '%Y-%m-%d')

        return f'{self.kbri_cache_key}:{formatted_date}'

    async def get_slot(
        self,
        redis: RedisService,
        at: datetime,
        skip_cache: bool,
    ) -> Dict[str, Any]:
        cache_key = self.get_cache_key(at)
        if not skip_cache:
            cache_object = await redis.get(cache_key)
            if cache_object:
                return json.loads(cache_object.decode('utf-8'))

        date_ = datetime.strftime(
            at,
            '%d-%m-%Y'
        )
        response = self.third_party_service.call(
            'GET',
            f'{settings.KBRI_HOST}/index.php/ajax/get_day/{date_}',
            None,
        )

        if response.text.replace('"', '') in ['libur', 'penuh', 'lewat']:
            print(
                f'Skipping {date_} due to {response.text}',
            )

            return None

        response = response.json()
        slot = {
            'date' : date_,
            'time': ', '.join(response[1]),
        }

        await redis.setex(
            cache_key,
            self.expire_cache,
            json.dumps(slot),
        )

        return slot
