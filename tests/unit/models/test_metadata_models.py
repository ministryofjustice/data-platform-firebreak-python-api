import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlmodel.pool import StaticPool

from daap_api.config import settings
from daap_api.db import Base
from daap_api.orm_models.metadata import DataProductTable, SchemaTable
from daap_api.response_models.metadata import (
    Column,
    DataProductCreate,
    DataProductRead,
    SchemaCreate,
    SchemaRead,
    Status,
)


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(settings.database_uri_test, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
        Base.metadata.drop_all(engine)


def test_create_data_product(session):
    create_request = DataProductCreate(
        name="data-product",
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


def test_round_trip_data_product(session):
    """
    Temporary test for exploring SQLModel
    """
    create_request = DataProductCreate(
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

    data_product = DataProductTable(**create_request.model_dump())
    session.add(data_product)
    session.commit()
    id = data_product.id

    fetched = session.get(DataProductTable, id)
    read_view = DataProductRead(**fetched.to_attributes())
    assert read_view == DataProductRead(
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
        version="v1.0",
    )


def test_create_schema(session):
    schema_request = SchemaCreate(
        tableDescription="example schema",
        columns=[
            Column(name="foo1", type="string", description="example1"),
            Column(name="foo2", type="int", description="example2"),
        ],
    )

    schema = SchemaTable(
        tableDescription=schema_request.tableDescription,
        columns=[column.model_dump() for column in schema_request.columns],
        name="my-schema",
    )
    session.add(schema)
    session.commit()
    session.refresh(schema)

    assert schema.id is not None


def test_round_trip_schema(session):
    """
    Temporary test for exploring SQLModel
    """
    schema_request = SchemaCreate(
        tableDescription="example schema",
        columns=[
            Column(name="foo1", type="string", description="example1"),
            Column(name="foo2", type="int", description="example2"),
        ],
    )

    schema = SchemaTable(
        tableDescription=schema_request.tableDescription,
        columns=[column.model_dump() for column in schema_request.columns],
        name="my-schema",
    )
    session.add(schema)
    session.commit()
    id = schema.id

    fetched = session.get(SchemaTable, id)
    read_view = SchemaRead.model_validate(fetched.to_attributes())

    assert read_view == SchemaRead(
        tableDescription=schema_request.tableDescription,
        columns=[
            Column(name="foo1", type="string", description="example1"),
            Column(name="foo2", type="int", description="example2"),
        ],
    )
