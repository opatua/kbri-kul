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
        slots = []
        date_counter = 0
        limit = self.default_slot_limit
        if slot_limit <= 10:
            limit = slot_limit

        cache_object = await redis.get(self.kbri_cache_key)
        if cache_object:
            slots = json.loads(cache_object.decode('utf-8'))

            if limit <= len(slots):
                return slots[:limit]

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

            if [slot for slot in slots if slot['date'] == date_]:
                print(f'Skipping date={date_} exists in slots')

                continue

            if response.text.replace('"', '') in ['libur', 'penuh', 'lewat']:
                print(
                    f'Skipping {date_} due to {response.text}',
                )

                continue

            response = response.json()

            slots.append(
                {
                    'date' : date_,
                    'time': response[1],
                },
            )

            if limit <= len(slots):
                await redis.setex(
                    self.kbri_cache_key,
                    self.expire_cache,
                    json.dumps(slots),
                )

                break

        return slots[:limit]
