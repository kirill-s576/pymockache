from typing import Union
from .abstract import AbstractAsyncCachingBackend
import aioredis


class AsyncRedisCachingBackend(AbstractAsyncCachingBackend):

    def __init__(self, redis_host):
        self.redis_host = redis_host

    async def get(self, key: Union[str, int]):
        redis = await aioredis.create_redis(self.redis_host, encoding="utf-8")
        value = await redis.get(key, encoding="utf-8")
        redis.close()
        return value

    async def set(self, key: Union[str, int], value: Union[str, int], expire_milliseconds: int = 60):
        redis = await aioredis.create_redis(self.redis_host, encoding="utf-8")
        await redis.set(key, value, expire=expire_milliseconds)
        redis.close()
