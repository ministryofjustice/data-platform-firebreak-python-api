import pytest
from factory import SubFactory
from factory.alchemy import SQLAlchemyModelFactory
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session

from daap_api.config import settings
from daap_api.db import Base, get_session
from daap_api.main import app
from daap_api.main import backend as cache_backend
from daap_api.models.orm.metadata_orm_models import (
    DataProductTable,
    DataProductVersionTable,
    SchemaTable,
)


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


@pytest.fixture
def data_product_version_factory(session):
    class DataProductVersionFactory(SQLAlchemyModelFactory):
        class Meta:
            model = DataProductVersionTable
            sqlalchemy_session = session

        name = "hmpps_use_of_force"
        description = "Data product for hmpps_use_of_force dev data"
        domain = "HMPPS"
        dataProductOwner = "dataplatformlabs@digital.justice.gov.uk"
        dataProductOwnerDisplayName = "Data Platform Labs"
        email = "dataplatformlabs@digital.justice.gov.uk"
        status = "draft"
        retentionPeriod = 3000
        dpiaRequired = False
        version = "v1.0"

    return DataProductVersionFactory


@pytest.fixture
def data_product_factory(session, data_product_version_factory):
    class DataProductFactory(SQLAlchemyModelFactory):
        class Meta:
            model = DataProductTable
            sqlalchemy_session = session

        name = "hmpps_use_of_force"
        current_version = SubFactory(data_product_version_factory)

    return DataProductFactory


@pytest.fixture
def schema_factory(session, data_product_version_factory):
    class SchemaFactory(SQLAlchemyModelFactory):
        class Meta:
            model = SchemaTable
            sqlalchemy_session = session

        data_product_version = SubFactory(data_product_version_factory)
        name = "statement"
        tableDescription = "desc"
        columns = [
            {"name": "id", "type": "bigint", "description": ""},
            {"name": "report_id", "type": "bigint", "description": ""},
            {"name": "user_id", "type": "string", "description": ""},
            {"name": "name", "type": "string", "description": ""},
            {"name": "email", "type": "string", "description": ""},
            {"name": "submitted_date", "type": "string", "description": ""},
            {"name": "statement_status", "type": "string", "description": ""},
            {"name": "last_training_month", "type": "string", "description": ""},
            {"name": "last_training_year", "type": "string", "description": ""},
            {"name": "job_start_year", "type": "string", "description": ""},
            {"name": "statement", "type": "string", "description": ""},
            {"name": "staff_id", "type": "bigint", "description": ""},
            {"name": "created_date", "type": "timestamp", "description": ""},
            {"name": "updated_date", "type": "string", "description": ""},
            {"name": "next_reminder_date", "type": "string", "description": ""},
            {"name": "overdue_date", "type": "string", "description": ""},
            {"name": "in_progress", "type": "string", "description": ""},
            {"name": "deleted", "type": "string", "description": ""},
            {"name": "removal_requested_reason", "type": "string", "description": ""},
            {"name": "removal_requested_date", "type": "string", "description": ""},
        ]

    return SchemaFactory
