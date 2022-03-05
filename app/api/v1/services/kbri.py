from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from app.api.v1.services.third_party_service import ThirdPartyService
from app.core.config import settings


class KbriService:
    third_party_service = ThirdPartyService()
    default_slot_limit = 5

    def get_schedule(self, slot_limit: Optional[int]) -> Optional[Dict[str, Any]]:
        slots = {}
        date_counter = 0
        limit = self.default_slot_limit
        if slot_limit and slot_limit <= 10:
            limit = slot_limit

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

            if response.text.replace('"', '') in ['libur', 'penuh']:
                print(
                    f'Skipping {date_} due to {response.text}',
                )

                continue

            response = response.json()
            slots[date_] = response[1]

            if len(slots) == limit:
                return slots
