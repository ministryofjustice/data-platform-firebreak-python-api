import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session

from daap_api.config import settings
from daap_api.db import Base, get_session
from daap_api.main import app
from daap_api.main import backend as cache_backend


@pytest.fixture()
def client(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture()
def session():
    engine = create_engine(settings.database_uri_test, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
        Base.metadata.drop_all(engine)
        cache_backend.response_store.clear()
        cache_backend.keys.clear()
