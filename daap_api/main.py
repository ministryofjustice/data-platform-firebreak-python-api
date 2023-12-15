import contextlib

from fastapi import FastAPI

from .db import create_db_and_tables
from .routers import ingestion_router, metadata_router


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(ingestion_router.router)
app.include_router(metadata_router.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
