import json
import time
import logging
from typing import Any, Optional
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger("marketpulse.cache")


class MemoryCache:
    """In-memory fallback cache with TTL expiration."""
    def __init__(self):
        self._store: dict[str, tuple[Any, float]] = {}

    async def get(self, key: str) -> Optional[Any]:
        if key not in self._store:
            return None
        val, expiry = self._store[key]
        if expiry is not None and time.time() > expiry:
            del self._store[key]
            return None
        return val

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        expiry = time.time() + ttl if ttl is not None else None
        self._store[key] = (value, expiry)
        return True

    async def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            return True
        return False

    async def clear(self) -> None:
        self._store.clear()


class CacheService:
    def __init__(self):
        self._redis: Optional[aioredis.Redis] = None
        self._memory = MemoryCache()
        self._use_redis = False

    async def connect(self) -> None:
        try:
            client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=1.0,
            )
            await client.ping()
            self._redis = client
            self._use_redis = True
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            self._use_redis = False
            self._redis = None
            logger.warning(f"Redis unavailable ({e}). Using in-memory fallback cache.")

    async def close(self) -> None:
        if self._redis:
            await self._redis.close()

    async def get(self, key: str) -> Optional[Any]:
        if self._use_redis and self._redis:
            try:
                val = await self._redis.get(key)
                if val is not None:
                    try:
                        return json.loads(val)
                    except json.JSONDecodeError:
                        return val
                return None
            except Exception as e:
                logger.warning(f"Redis get error: {e}. Falling back to memory.")
        return await self._memory.get(key)

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        ttl = ttl or settings.CACHE_DEFAULT_TTL
        if self._use_redis and self._redis:
            try:
                serialized = json.dumps(value) if not isinstance(value, str) else value
                await self._redis.set(key, serialized, ex=ttl)
                return True
            except Exception as e:
                logger.warning(f"Redis set error: {e}. Falling back to memory.")
        return await self._memory.set(key, value, ttl=ttl)

    async def delete(self, key: str) -> bool:
        if self._use_redis and self._redis:
            try:
                await self._redis.delete(key)
            except Exception:
                pass
        return await self._memory.delete(key)


cache = CacheService()
