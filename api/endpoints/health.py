import structlog
from fastapi import APIRouter, HTTPException, Request

from schema.health import HealthCheck
from schema.responses import ResponseBase, create_response

router = APIRouter()
logger = structlog.stdlib.get_logger()


@router.get("/", response_model=ResponseBase[HealthCheck], status_code=200)
async def health_check(request: Request):
    try:
        res = HealthCheck(message=f"Hello, I am alive!")
        await logger.info("Someone checked the health of the API")
        return create_response(data=res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

