import contextlib

import structlog
from fastapi import FastAPI, Request, Response

from .db import create_db_and_tables
from .routers import ingestion_router, metadata_router


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()

    log = structlog.get_logger(__name__)
    log.info("example")

    yield


app = FastAPI(lifespan=lifespan)
app.include_router(ingestion_router.router)
app.include_router(metadata_router.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.middleware("http")
async def logging_middleware(request: Request, call_next) -> Response:
    req_id = request.headers.get("request-id")

    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=req_id,
    )

    response: Response = await call_next(request)

    return response
