# from collections.abc import AsyncGenerator
import redis.asyncio as aioredis
from redis.asyncio import Redis

from core.config import settings
# from db.session import SessionLocal

# from utils.s3_client import S3Client


async def get_redis_client() -> Redis:
    redis = await aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
        max_connections=10,
        encoding="utf8",
        decode_responses=True,
    )
    return redis


#
# async def get_db() -> AsyncGenerator[AsyncSession, None]:
#     async with SessionLocal() as session:
#         yield session


# def s3_auth() -> S3Client:
#     s3_client = S3Client(
#         aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
#         aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
#         region_name=settings.AWS_S3_REGION_NAME,
#         private_bucket_name=settings.AWS_S3_BUCKET_NAME_PRIVATE,
#         public_bucket_name=settings.AWS_S3_BUCKET_NAME_PUBLIC,
#         base_folder=settings.AWS_S3_BASE_FOLDER,
#         environment=settings.ENV.value,
#     )
#
#     return s3_client
