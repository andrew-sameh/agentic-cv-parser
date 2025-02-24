import time
from contextlib import asynccontextmanager

import structlog
import uvicorn
from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.context import correlation_id
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from agent.workflow import ResearchAgent
from api.router import router as api_router
from core.config import settings
from utils.logger import configure_logger

configure_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        app.state.graph = ResearchAgent()
        yield
    finally:
        pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
    docs_url="/",
)


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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

if __name__ == "__main__":
    if settings.ENV == "DEV":
        uvicorn.run("main:app", host="0.0.0.0", port=8000, log_config=None, reload=True)
    else:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, log_config=None)

