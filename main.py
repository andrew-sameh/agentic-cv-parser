import asyncio
import time
from contextlib import asynccontextmanager

import structlog
import uvicorn
from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.context import correlation_id
from fastapi import (
    FastAPI,
    HTTPException,
    Request,
    Response,
)
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter

from agent.workflow import ResearchAgent
from api.router import router as api_router
from core.config import settings
from utils.exceptions.global_exceptions import (
    handle_bad_request,
    handle_http_exception,
    handle_timeout_exception,
    handle_validation_exception,
    handle_value_error,
)
from utils.limiter import user_id_identifier
from utils.logger import configure_logger
from utils.middlewares.server_error import ServerErrorMiddleware
from utils.redis import get_redis_client

configure_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        redis_client = await get_redis_client()
        await FastAPILimiter.init(redis_client, identifier=user_id_identifier)
        app.state.graph = ResearchAgent()
        yield

        await FastAPILimiter.close()
    finally:
        pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
    docs_url="/",
)


app.add_middleware(ServerErrorMiddleware)


# Timings Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter_ns()
    response = await call_next(request)
    process_time = time.perf_counter_ns() - start_time
    response.headers["X-Process-Time"] = str(process_time / 10**6)
    return response


# Logging Middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next) -> Response:
    req_id = correlation_id.get()

    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=req_id,
    )

    response: Response = await call_next(request)

    return response


# Correlation ID Middleware
app.add_middleware(CorrelationIdMiddleware)


# CORS Middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Process-Time"],
    )

app.add_exception_handler(RequestValidationError, handle_validation_exception)
app.add_exception_handler(asyncio.TimeoutError, handle_timeout_exception)
app.add_exception_handler(ValueError, handle_value_error)
app.add_exception_handler(AttributeError, handle_bad_request)
app.add_exception_handler(HTTPException, handle_http_exception)

app.include_router(api_router)

if __name__ == "__main__":
    if settings.ENV == "DEV":
        uvicorn.run("main:app", host="0.0.0.0", port=8000, log_config=None, reload=True)
    else:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, log_config=None)
