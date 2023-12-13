from fastapi import FastAPI, Request

from .config import settings
from .routers import ingestion, metadata
import hashlib
import json

from idempotency_header_middleware import IdempotencyHeaderMiddleware
from idempotency_header_middleware.backends import MemoryBackend


IDEMPOTENT_METHODS = ["POST", "PATCH"]

app = FastAPI()
app.include_router(ingestion.router)
app.include_router(metadata.router)


backend = MemoryBackend()

app.add_middleware(
    IdempotencyHeaderMiddleware,
    backend=backend,
    idempotency_header_key="x-idempotent-key",
    applicable_methods=IDEMPOTENT_METHODS,
)


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
    if request.method in IDEMPOTENT_METHODS:
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


@app.get("/")
async def root():
    return {"message": "Hello World"}


def _generate_idempotent_hash_key(body: dict):
    """
    creates a hash of the body content of a request.
    """
    json_body = json.dumps(body, sort_keys=True)
    body_hash = hashlib.md5(json_body.encode()).hexdigest()
    return body_hash
