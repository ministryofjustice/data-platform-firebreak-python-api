import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlmodel.pool import StaticPool

from daap_api.config import settings
from daap_api.db import Base
from daap_api.models.orm.metadata_orm_models import DataProductTable, Status
from daap_api.models.orm.metadata_repositories import DataProductRepository


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(settings.database_uri_test, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
        Base.metadata.drop_all(engine)


def test_create_data_product(session):
    repo = DataProductRepository(session)
    data_product = DataProductTable(
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

    repo.create(data_product)

    assert data_product.id is not None


def test_cannot_create_existing_data_product(session):
    repo = DataProductRepository(session)
    data_product = DataProductTable(
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
    repo.create(data_product)

    duplicate = DataProductTable(
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

    with pytest.raises(repo.IntegrityError):
        repo.create(duplicate)


def test_fetch_latest_data_product(session):
    repo = DataProductRepository(session)
    v1 = DataProductTable(
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

    repo.create(v1)

    data_product = DataProductTable(
        name="data_product",
        domain="hmpps",
        description="example data product",
        dataProductOwner="joe.bloggs@justice.gov.uk",
        dataProductOwnerDisplayName="Joe bloggs",
        status=Status.published,
        email="data-product-contact@justice.gov.uk",
        retentionPeriod=365,
        dpiaRequired=True,
        version="v1.1",
    )

    repo.create(data_product)
    fetched = repo.fetch_latest(name="data_product")

    assert fetched == data_product


def test_no_latest_data_product(session):
    repo = DataProductRepository(session)
    fetched = repo.fetch_latest(name="data_product")

    assert fetched is None


def test_fetch_data_product(session):
    repo = DataProductRepository(session)
    v1 = DataProductTable(
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
    v2 = DataProductTable(
        name="data_product",
        domain="hmpps",
        description="example data product",
        dataProductOwner="joe.bloggs@justice.gov.uk",
        dataProductOwnerDisplayName="Joe bloggs Jr",
        status=Status.draft,
        email="data-product-contact@justice.gov.uk",
        retentionPeriod=365,
        dpiaRequired=True,
        version="v2.0",
    )

    repo.create(v1)
    repo.create(v2)
    fetched = repo.fetch(name="data_product", version="v1.0")

    assert fetched == v1


def test_no_data_product(session):
    repo = DataProductRepository(session)
    v1 = repo.fetch(name="data_product", version="v1.0")
    latest = repo.fetch_latest(name="data_product")

    assert v1 is None
    assert latest is None
