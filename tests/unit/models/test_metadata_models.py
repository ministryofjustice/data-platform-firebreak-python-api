import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from daap_api.models.metadata import (
    Column,
    DataProductCreate,
    DataProductRead,
    DataProductTable,
    SchemaCreate,
    SchemaRead,
    SchemaTable,
    Status,
)


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_create_data_product(session):
    create_request = DataProductCreate(
        name="data-product",
        domain="hmpps",
        description="example data product",
        dataProductOwner="joe.bloggs@justice.gov.uk",
        dataProductOwnerDisplayName="Joe bloggs",
        status=Status.DRAFT,
        email="data-product-contact@justice.gov.uk",
        retentionPeriod=365,
        dpiaRequired=True,
    )

    data_product = DataProductTable.model_validate(
        create_request.model_dump() | {"version": "v1.0"}
    )
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
        status=Status.DRAFT,
        email="data-product-contact@justice.gov.uk",
        retentionPeriod=365,
        dpiaRequired=True,
        tags={"some-tag": "some-value"},
    )

    data_product = DataProductTable.model_validate(
        create_request.model_dump() | {"version": "v1.0"}
    )
    session.add(data_product)
    session.commit()
    id = data_product.id
    external_id = f"dp:data-product:v1.0"

    fetched = session.get(DataProductTable, id)
    read_view = DataProductRead.model_validate(
        fetched.model_dump() | {"id": external_id}
    )
    assert read_view == DataProductRead(
        name="data-product",
        domain="hmpps",
        description="example data product",
        dataProductOwner="joe.bloggs@justice.gov.uk",
        dataProductOwnerDisplayName="Joe bloggs",
        status=Status.DRAFT,
        email="data-product-contact@justice.gov.uk",
        retentionPeriod=365,
        dpiaRequired=True,
        id=external_id,
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

    schema = SchemaTable.model_validate(
        {
            "tableDescription": schema_request.tableDescription,
            "columns": [column.model_dump() for column in schema_request.columns],
        }
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

    schema = SchemaTable.model_validate(
        {
            "tableDescription": schema_request.tableDescription,
            "columns": [column.model_dump() for column in schema_request.columns],
        }
    )
    session.add(schema)
    session.commit()
    id = schema.id

    fetched = session.get(SchemaTable, id)
    read_view = SchemaRead.model_validate(fetched.model_dump())

    assert read_view == SchemaRead(
        tableDescription=schema_request.tableDescription,
        columns=[
            Column(name="foo1", type="string", description="example1"),
            Column(name="foo2", type="int", description="example2"),
        ],
    )
