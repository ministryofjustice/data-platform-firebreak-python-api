import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlmodel.pool import StaticPool

from daap_api.config import settings
from daap_api.db import Base
from daap_api.models.api.metadata_api_models import (
    Column,
    DataProductCreate,
    DataProductRead,
    SchemaCreate,
    SchemaRead,
    Status,
)
from daap_api.models.orm.metadata_orm_models import DataProductTable, SchemaTable


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(settings.database_uri_test, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
        Base.metadata.drop_all(engine)


def test_create_data_product(session):
    create_request = DataProductCreate(
        name="data_product",
        domain="hmpps",
        description="example data product",
        dataProductOwner="joe.bloggs@justice.gov.uk",
        dataProductOwnerDisplayName="Joe bloggs",
        status=Status.draft,
        email="data-product-contact@justice.gov.uk",
        retentionPeriod=365,
        dpiaRequired=True,
    )

    data_product = DataProductTable(**create_request.model_dump())
    session.add(data_product)
    session.commit()
    session.refresh(data_product)

    assert data_product.id is not None


def test_create_schema(session):
    data_product = DataProductTable(
        name="data-product",
        domain="hmpps",
        description="example data product",
        dataProductOwner="joe.bloggs@justice.gov.uk",
        dataProductOwnerDisplayName="Joe bloggs",
        status=Status.draft,
        email="data-product-contact@justice.gov.uk",
        retentionPeriod=365,
        dpiaRequired=True,
        tags={"some-tag": "some-value"},
    )
    session.add(data_product)

    schema = SchemaTable(
        data_product=data_product,
        tableDescription="example schema",
        columns=[{"name": "foo1", "type": "string", "description": "example1"}],
        name="my-schema",
    )
    session.add(schema)
    session.commit()
    session.refresh(schema)

    assert schema.id is not None
