import json
from typing import Any

import redis.asyncio as aioredis

from app.core.config import get_settings
from app.domain.interfaces.cache_service import ICacheService


class RedisCache(ICacheService):
    def __init__(self) -> None:
        settings = get_settings()
        self._redis = aioredis.from_url(settings.redis_url, decode_responses=True)

    async def get(self, key: str) -> Any | None:
        value = await self._redis.get(key)
        return json.loads(value) if value is not None else None

    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        payload = json.dumps(value)
        if ttl_seconds:
            await self._redis.setex(key, ttl_seconds, payload)
        else:
            await self._redis.set(key, payload)

    async def delete(self, key: str) -> None:
        await self._redis.delete(key)
