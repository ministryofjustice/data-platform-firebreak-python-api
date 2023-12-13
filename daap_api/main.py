from fastapi import FastAPI

from .db import create_db_and_tables
from .routers import ingestion, metadata


async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(ingestion.router)
app.include_router(metadata.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
