import pytest
from fastapi import status

from daap_api.models.orm.metadata_orm_models import (
    DataProductTable,
    DataProductVersionTable,
    SchemaTable,
)

SAMPLE_COLUMNS = [
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


def data_product_version():
    return DataProductVersionTable(
        name="hmpps_use_of_force",
        description="Data product for hmpps_use_of_force dev data",
        domain="HMPPS",
        dataProductOwner="dataplatformlabs@digital.justice.gov.uk",
        dataProductOwnerDisplayName="Data Platform Labs",
        email="dataplatformlabs@digital.justice.gov.uk",
        status="draft",
        retentionPeriod=3000,
        dpiaRequired=False,
        version="v1.0",
    )


def schema(data_product_version):
    return SchemaTable(
        name="statement",
        columns=SAMPLE_COLUMNS,
        tableDescription="desc",
        data_product_version=data_product_version,
    )


@pytest.fixture
def statement_columns():
    return [
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


def test_create_metadata(client):
    response = client.post(
        "/data-products/",
        json={
            "name": "hmpps_use_of_force",
            "description": "Data product for hmpps_use_of_force dev data",
            "domain": "HMPPS",
            "dataProductOwner": "dataplatformlabs@digital.justice.gov.uk",
            "dataProductOwnerDisplayName": "Data Platform Labs",
            "email": "dataplatformlabs@digital.justice.gov.uk",
            "status": "draft",
            "retentionPeriod": 3000,
            "dpiaRequired": False,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    response_data_product = response.json()
    assert response_data_product["version"] == "v1.0"
    assert response_data_product["id"] == "dp:hmpps_use_of_force:v1.0"


def test_read_metadata(client, session):
    session.add(data_product_version())
    session.commit()

    response = client.get("/data-products/dp:hmpps_use_of_force:v1.0")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "name": "hmpps_use_of_force",
        "description": "Data product for hmpps_use_of_force dev data",
        "domain": "HMPPS",
        "dataProductOwner": "dataplatformlabs@digital.justice.gov.uk",
        "dataProductOwnerDisplayName": "Data Platform Labs",
        "email": "dataplatformlabs@digital.justice.gov.uk",
        "status": "draft",
        "retentionPeriod": 3000,
        "dpiaRequired": False,
        "schemas": [],
        "version": "v1.0",
        "id": "dp:hmpps_use_of_force:v1.0",
        "tags": {},
    }


def test_list_data_products(client, session):
    initial_version = data_product_version()
    session.add(initial_version)
    session.add(
        DataProductTable(current_version=initial_version, name=initial_version.name)
    )
    session.commit()

    response = client.get("/data-products")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "name": "hmpps_use_of_force",
            "description": "Data product for hmpps_use_of_force dev data",
            "domain": "HMPPS",
            "dataProductOwner": "dataplatformlabs@digital.justice.gov.uk",
            "dataProductOwnerDisplayName": "Data Platform Labs",
            "email": "dataplatformlabs@digital.justice.gov.uk",
            "status": "draft",
            "retentionPeriod": 3000,
            "dpiaRequired": False,
            "schemas": [],
            "version": "v1.0",
            "id": "dp:hmpps_use_of_force:v1.0",
            "tags": {},
        }
    ]


def test_no_data_products(client, session):
    response = client.get("/data-products")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_create_schema(client, session, statement_columns):
    initial_version = data_product_version()
    session.add(initial_version)
    session.add(
        DataProductTable(current_version=initial_version, name=initial_version.name)
    )
    session.commit()

    response = client.post(
        "/schemas/dp:hmpps_use_of_force:v1.0:statement",
        json={
            "tableDescription": "statement desc",
            "columns": statement_columns,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "tableDescription": "statement desc",
        "columns": statement_columns,
        "id": "dp:hmpps_use_of_force:v1.0:statement",
    }


def test_create_schema_for_non_existent_product(client, session, statement_columns):
    response = client.post(
        "/schemas/dp:hmpps_use_of_force:v1.0:statement",
        json={
            "tableDescription": "statement desc",
            "columns": statement_columns,
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_schema_that_already_exists(client, session, statement_columns):
    existing_data_product = data_product_version()
    session.add(existing_data_product)
    session.add(
        DataProductTable(
            current_version=existing_data_product, name=existing_data_product.name
        )
    )
    existing_schema = schema(existing_data_product)
    session.add(existing_data_product)
    session.add(existing_schema)
    session.commit()

    response = client.post(
        "/schemas/dp:hmpps_use_of_force:v1.0:statement",
        json={
            "tableDescription": "statement desc",
            "columns": statement_columns,
        },
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_read_schema(client, statement_columns, session):
    existing_data_product = data_product_version()
    session.add(existing_data_product)
    session.add(
        DataProductTable(
            current_version=existing_data_product, name=existing_data_product.name
        )
    )
    existing_schema = schema(existing_data_product)
    session.add(existing_data_product)
    session.add(existing_schema)
    session.commit()

    response = client.get("/schemas/dp:hmpps_use_of_force:v1.0:statement")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "tableDescription": "desc",
        "columns": statement_columns,
        "id": "dp:hmpps_use_of_force:v1.0:statement",
    }


def test_read_data_product_with_schema(client, statement_columns, session):
    existing_data_product = data_product_version()
    session.add(existing_data_product)
    session.add(
        DataProductTable(
            current_version=existing_data_product, name=existing_data_product.name
        )
    )
    existing_schema = schema(existing_data_product)
    session.add(existing_data_product)
    session.add(existing_schema)
    session.commit()

    response = client.get("/data-products/dp:hmpps_use_of_force:v1.0")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["schemas"] == [
        {"id": "dp:hmpps_use_of_force:v1.0:statement"}
    ]


def test_missing_data_product(client):
    response = client.get("/data-products/dp:hmpps_use_of_the_force:v1.0")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Data product does not exist with id dp:hmpps_use_of_the_force:v1.0"
    }


def test_invalid_id(client):
    response = client.get("/data-products/hmpps_use_of_the_force")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Invalid id: hmpps_use_of_the_force"}


def test_missing_schema(client):
    response = client.get("/data-products/dp:hmpps_use_of_the_force:v1.0")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Data product does not exist with id dp:hmpps_use_of_the_force:v1.0"
    }


def test_update_invalid_id(client):
    response = client.put(
        "/data-products/hmpps_use_of_the_force",
        json={
            "description": "Data product for hmpps_use_of_force dev data",
            "domain": "HMPPS",
            "dataProductOwner": "dataplatformlabs@digital.justice.gov.uk",
            "dataProductOwnerDisplayName": "Data Platform Labs",
            "email": "dataplatformlabs@digital.justice.gov.uk",
            "status": "draft",
            "retentionPeriod": 3000,
            "dpiaRequired": False,
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Invalid id: hmpps_use_of_the_force"}


def test_update_missing_data_product(client):
    response = client.put(
        "/data-products/dp:hmpps_use_of_the_force:v1.0",
        json={
            "description": "Data product for hmpps_use_of_force dev data",
            "domain": "HMPPS",
            "dataProductOwner": "dataplatformlabs@digital.justice.gov.uk",
            "dataProductOwnerDisplayName": "Data Platform Labs",
            "email": "dataplatformlabs@digital.justice.gov.uk",
            "status": "draft",
            "retentionPeriod": 3000,
            "dpiaRequired": False,
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Data product does not exist with id dp:hmpps_use_of_the_force:v1.0"
    }


def test_update_data_product(client, session):
    existing_data_product = data_product_version()
    session.add(existing_data_product)
    session.add(
        DataProductTable(
            current_version=existing_data_product, name=existing_data_product.name
        )
    )
    session.add(existing_data_product)
    session.commit()

    response = client.put(
        "/data-products/dp:hmpps_use_of_force:v1.0",
        json={
            "description": "Updated description",
            "domain": "HMPPS",
            "dataProductOwner": "dataplatformlabs@digital.justice.gov.uk",
            "dataProductOwnerDisplayName": "Data Platform Labs",
            "email": "dataplatformlabs@digital.justice.gov.uk",
            "status": "draft",
            "retentionPeriod": 3000,
            "dpiaRequired": False,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "description": "Updated description",
        "domain": "HMPPS",
        "dataProductOwner": "dataplatformlabs@digital.justice.gov.uk",
        "dataProductOwnerDisplayName": "Data Platform Labs",
        "email": "dataplatformlabs@digital.justice.gov.uk",
        "status": "draft",
        "retentionPeriod": 3000,
        "dpiaRequired": False,
        "id": "dp:hmpps_use_of_force:v1.1",
        "name": "hmpps_use_of_force",
        "tags": {},
        "schemas": [],
        "version": "v1.1",
    }


def test_remove_column_from_schema(client, session):
    existing_data_product = data_product_version()
    session.add(existing_data_product)
    session.add(
        DataProductTable(
            current_version=existing_data_product, name=existing_data_product.name
        )
    )
    existing_schema = schema(existing_data_product)
    session.add(existing_data_product)
    session.add(existing_schema)

    response = client.put(
        "/schemas/dp:hmpps_use_of_force:v1.0:statement",
        json={
            "tableDescription": "abcd",
            "columns": [{"name": "id", "type": "bigint", "description": ""}],
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "tableDescription": "abcd",
        "columns": [{"name": "id", "type": "bigint", "description": ""}],
        "id": "dp:hmpps_use_of_force:v2.0:statement",
        "data_product": {
            "dataProductOwner": "dataplatformlabs@digital.justice.gov.uk",
            "dataProductOwnerDisplayName": "Data Platform Labs",
            "description": "Data product for hmpps_use_of_force dev data",
            "domain": "HMPPS",
            "dpiaRequired": False,
            "email": "dataplatformlabs@digital.justice.gov.uk",
            "id": "dp:hmpps_use_of_force:v2.0",
            "name": "hmpps_use_of_force",
            "retentionPeriod": 3000,
            "schemas": [],
            "status": "draft",
            "tags": {},
            "version": "v2.0",
        },
    }


def test_minor_schema_update(client, session):
    existing_data_product = data_product_version()
    session.add(existing_data_product)
    session.add(
        DataProductTable(
            current_version=existing_data_product, name=existing_data_product.name
        )
    )
    existing_schema = schema(existing_data_product)
    session.add(existing_data_product)
    session.add(existing_schema)

    columns = [
        {"name": "id", "type": "bigint", "description": "unique identifier"},
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
        {
            "name": "removal_requested_reason",
            "type": "string",
            "description": "",
        },
        {"name": "removal_requested_date", "type": "string", "description": ""},
        {"name": "new_col", "type": "string", "description": ""},
    ]

    response = client.put(
        "/schemas/dp:hmpps_use_of_force:v1.0:statement",
        json={"tableDescription": "abcd", "columns": columns},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "tableDescription": "abcd",
        "columns": columns,
        "id": "dp:hmpps_use_of_force:v1.1:statement",
        "data_product": {
            "dataProductOwner": "dataplatformlabs@digital.justice.gov.uk",
            "dataProductOwnerDisplayName": "Data Platform Labs",
            "description": "Data product for hmpps_use_of_force dev data",
            "domain": "HMPPS",
            "dpiaRequired": False,
            "email": "dataplatformlabs@digital.justice.gov.uk",
            "id": "dp:hmpps_use_of_force:v1.1",
            "name": "hmpps_use_of_force",
            "retentionPeriod": 3000,
            "schemas": [],
            "status": "draft",
            "tags": {},
            "version": "v1.1",
        },
    }


def test_schema_unchanged(client, session):
    existing_data_product = data_product_version()
    existing_schema = schema(existing_data_product)
    session.add(existing_data_product)
    session.add(
        DataProductTable(
            current_version=existing_data_product, name=existing_data_product.name
        )
    )
    session.add(existing_schema)

    response = client.put(
        "/schemas/dp:hmpps_use_of_force:v1.0:statement",
        json={
            "tableDescription": existing_schema.tableDescription,
            "columns": existing_schema.columns,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "tableDescription": "desc",
        "columns": SAMPLE_COLUMNS,
        "id": "dp:hmpps_use_of_force:v1.0:statement",
        "data_product": {
            "dataProductOwner": "dataplatformlabs@digital.justice.gov.uk",
            "dataProductOwnerDisplayName": "Data Platform Labs",
            "description": "Data product for hmpps_use_of_force dev data",
            "domain": "HMPPS",
            "dpiaRequired": False,
            "email": "dataplatformlabs@digital.justice.gov.uk",
            "id": "dp:hmpps_use_of_force:v1.0",
            "name": "hmpps_use_of_force",
            "retentionPeriod": 3000,
            "schemas": [],
            "status": "draft",
            "tags": {},
            "version": "v1.0",
        },
    }


def test_idempotent_request(client):
    json = {
        "name": "hmpps_use_of_force",
        "description": "Data product for hmpps_use_of_force dev data",
        "domain": "HMPPS",
        "dataProductOwner": "dataplatformlabs@digital.justice.gov.uk",
        "dataProductOwnerDisplayName": "Data Platform Labs",
        "email": "dataplatformlabs@digital.justice.gov.uk",
        "status": "draft",
        "retentionPeriod": 3000,
        "dpiaRequired": False,
        "schemas": [
            "knex_migrations",
            "knex_migrations_lock",
            "report",
            "report_log",
            "statement",
            "statement_amendments",
            "table",
        ],
    }

    client.post(
        "/data-products/",
        json=json,
    )

    response = client.post(
        "/data-products/",
        json=json,
    )

    assert response.headers["idempotent-replayed"] == "true"
