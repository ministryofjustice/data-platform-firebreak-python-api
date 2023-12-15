import contextlib
import hashlib
import json

import structlog
from fastapi import FastAPI, Request, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi_azure_auth import SingleTenantAzureAuthorizationCodeBearer
from idempotency_header_middleware import IdempotencyHeaderMiddleware
from idempotency_header_middleware.backends import MemoryBackend
from pydantic import AnyHttpUrl, computed_field

from .config import settings
from .db import create_db_and_tables
from .routers import ingestion_router, metadata_router

IDEMPOTENT_KEY_METHODS = ["POST", "PATCH"]


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()

    if settings.auth_enabled:
        await azure_scheme.openid_config.load_config()
    log = structlog.get_logger(__name__)
    log.info("example")

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
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


azure_scheme = SingleTenantAzureAuthorizationCodeBearer(
    app_client_id=settings.AZURE_APP_CLIENT_ID,
    tenant_id=settings.AZURE_TENANT_ID,
    scopes=settings.SCOPES,
)

backend = MemoryBackend()

app.add_middleware(
    IdempotencyHeaderMiddleware,
    backend=backend,
    idempotency_header_key="x-idempotent-key",
    applicable_methods=IDEMPOTENT_KEY_METHODS,
)


@app.get("/", dependencies=[Security(azure_scheme)])
async def root():
    return {"message": "Hello World"}


async def set_body(request: Request, body: bytes):
    async def receive():
        return {"type": "http.request", "body": body}

    request._receive = receive


async def get_body(request: Request) -> bytes:
    body = await request.body()
    await set_body(request, body)
    return body


@app.middleware("http")
async def add_idempotent_key(request: Request, call_next):
    """
    This will add an idempotent key to `x-idempotent-key` in the request header
    for applicable methods
    """
    if request.method in IDEMPOTENT_KEY_METHODS:
        await set_body(request, await request.body())

        body = await get_body(request)

        idempotent_key = (
            request.url.path[1:].replace("/", ".")
            + "#"
            + _generate_idempotent_hash_key(json.loads(body.decode()))
        )

        request.headers.__dict__["_list"].append(
            (
                "x-idempotent-key".encode(),
                idempotent_key.encode(),
            )
        )
        response = await call_next(request)
    else:
        response = await call_next(request)

    return response


def _generate_idempotent_hash_key(body: dict):
    """
    creates a hash of the body content of a request.
    """
    json_body = json.dumps(body, sort_keys=True)
    body_hash = hashlib.md5(json_body.encode()).hexdigest()
    return body_hash
