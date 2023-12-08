from fastapi import FastAPI

from .config import settings
from .routers import ingestion, metadata

app = FastAPI()
app.include_router(ingestion.router)
app.include_router(metadata.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
