import contextlib

import uvicorn
from fastapi import FastAPI, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi_azure_auth import SingleTenantAzureAuthorizationCodeBearer
from pydantic import AnyHttpUrl, computed_field

from .config import settings
from .db import create_db_and_tables
from .routers import ingestion_router, metadata_router


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    await azure_scheme.openid_config.load_config()
    yield


app = FastAPI(
    lifespan=lifespan,  # type: ignore
    swagger_ui_oauth2_redirect_url="/oauth2-redirect",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": settings.AZURE_OPENAPI_CLIENT_ID,
    },
)
app.include_router(ingestion_router.router)
app.include_router(metadata_router.router)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin)
                       for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


azure_scheme = SingleTenantAzureAuthorizationCodeBearer(
    app_client_id=settings.AZURE_APP_CLIENT_ID,
    tenant_id=settings.AZURE_TENANT_ID,
    scopes=settings.SCOPES,
)


@app.get("/", dependencies=[Security(azure_scheme)])
async def root():
    return {"message": "Hello World"}
