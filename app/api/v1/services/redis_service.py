from aioredis import Redis

from app.core.config import settings


class RedisService:
    def initialize_redis(self) -> Redis:
        return Redis.from_url(settings.REDIS_HOST)
