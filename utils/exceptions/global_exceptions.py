import asyncio
import traceback
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import structlog
from sqlalchemy.exc import IntegrityError

logger = structlog.stdlib.get_logger()

async def handle_sqlalchemy_integrity_error(request: Request, exc: IntegrityError):
    stack_trace = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    await logger.error(
        "SQLAlchemy Integrity Error",
        error=str(exc.__class__.__name__),
        error_info=stack_trace,
    )
    return JSONResponse(
        status_code=400,
        content={
            "error_type": "DatabaseError",
            "message": "An error occurred while processing the request.",
            "details": str(exc),
            "status": "error",
        },
    )

async def handle_validation_exception(request: Request, exc: RequestValidationError):
    detail = exc.errors()
    await logger.error(
        "Validation Error",
        error=str(exc.__class__.__name__),
        error_info=detail,
    )
    return JSONResponse(
        status_code=422,
        content={
            "error_type": "ValidationError",
            "message": "An error occurred while validating the request.",
            "details": detail,
            "status": "error",
        },
    )


async def handle_timeout_exception(request: Request, exc: asyncio.TimeoutError):
    stack_trace = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    await logger.error(
        "Timeout Error",
        error=str(exc.__class__.__name__),
        error_info=stack_trace,
    )
    return JSONResponse(
        status_code=408,
        content={
            "error_type": "TimeoutError",
            "message": "Request timed out.",
            "status": "error",
        },
    )


async def handle_value_error(request: Request, exc: ValueError):
    stack_trace = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    await logger.error(
        "Value Error",
        error=str(exc.__class__.__name__),
        error_info=stack_trace,
    )
    return JSONResponse(
        status_code=400,
        content={
            "error_type": "ValueError",
            "message": f"Invalid input.{str(exc)}",
            "details": str(exc),
            "status": "error",
        },
    )


async def handle_bad_request(request: Request, exc: AttributeError):
    stack_trace = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    await logger.error(
        "Bad Request",
        error=str(exc.__class__.__name__),
        error_info=stack_trace,
    )
    return JSONResponse(
        status_code=400,
        content={
            "error_type": "BadRequest",
            "message": "Malformed request or data.",
            "details": str(exc),
            "status": "error",
        },
    )


async def handle_http_exception(request: Request, exc: HTTPException):
    await logger.error(
        "HTTP Exception",
        error=str(exc.__class__.__name__),
        error_info=exc.detail,
        status_code=exc.status_code,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_type": "HTTPException",
            "message": "An HTTP exception occurred.",
            "details": exc.detail,
            "status": "error",
        },
    )
