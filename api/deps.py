from redis.asyncio import Redis
from core.config import settings

from utils.s3_client import S3Client, get_s3_client
from typing import Annotated

from database import get_db_session
from utils.redis import get_redis_client
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

DBSessionDep = Annotated[AsyncSession, Depends(get_db_session)]

RedisDep = Annotated[Redis, Depends(get_redis_client)]

S3Dep = Annotated[S3Client, Depends(get_s3_client)]
