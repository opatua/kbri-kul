import json
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from app.api.v1.services.redis_service import RedisService

from app.api.v1.services.third_party_service import ThirdPartyService
from app.core.config import settings


class KbriService:
    third_party_service = ThirdPartyService()
    default_slot_limit = 5
    redis_service = RedisService()
    kbri_cache_key = 'kbri_cache'

    async def get_schedule(self, slot_limit: Optional[int]) -> Optional[Dict[str, Any]]:
        redis = self.redis_service.initialize_redis()
        slots = {}
        date_counter = 0
        limit = self.default_slot_limit
        if slot_limit and slot_limit <= 10:
            limit = slot_limit

        cache_object = await redis.get(self.kbri_cache_key)
        if cache_object:
            try:
                slots = json.loads(cache_object.decode('utf-8'))
            except:
                return None

            if len(slots) == limit:
                return slots

        while True:
            date_ = datetime.strftime(
                (datetime.now() + timedelta(days=date_counter)),
                '%d-%m-%Y'
            )
            response = self.third_party_service.call(
                'GET',
                f'{settings.KBRI_HOST}/index.php/ajax/get_day/{date_}',
                None,
            )

            date_counter += 1

            if response.text.replace('"', '') in ['libur', 'penuh', 'lewat']:
                print(
                    f'Skipping {date_} due to {response.text}',
                )

                continue

            response = response.json()
            slots[date_] = response[1]

            if len(slots) == limit:
                await redis.setex(
                    self.kbri_cache_key,
                    timedelta(minutes=1),
                    json.dumps(slots),
                )

                return dict(sorted(slots.items()))
