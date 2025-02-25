from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import structlog
import traceback

logger = structlog.stdlib.get_logger()


class ServerErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)

        except Exception as exc:
            stack_trace = "".join(
                traceback.format_exception(type(exc), exc, exc.__traceback__)
            )
            await logger.error(
                "Server Error",
                error=str(exc.__class__.__name__),
                error_info=stack_trace,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "error_type": "ServerError",
                    "message": "An error occurred while processing the request.",
                    "status": "error",
                },
            )
