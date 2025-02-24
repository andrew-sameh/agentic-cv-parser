import structlog
from fastapi import APIRouter, Depends, Request
from fastapi_limiter.depends import RateLimiter

from schema.health import HealthCheck
from schema.responses import ResponseBase, create_response

router = APIRouter()
logger = structlog.stdlib.get_logger()


@router.get(
    "/",
    dependencies=[Depends(RateLimiter(times=10, seconds=20))],
    response_model=ResponseBase[HealthCheck],
    status_code=200,
)
async def health_check():
    res = HealthCheck(message="Hello, I am alive!")
    await logger.info("Someone checked the health of the API")
    return create_response(data=res)
