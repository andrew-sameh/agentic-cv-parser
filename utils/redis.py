import redis.asyncio as aioredis
from redis.asyncio import Redis
from core.config import settings


async def get_redis_client() -> Redis:
    redis = await aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
        max_connections=10,
        encoding="utf8",
        decode_responses=True,
    )
    return redis
