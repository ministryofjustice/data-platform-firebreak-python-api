import pytest
from fastapi import status


@pytest.fixture
def data_product(data_product_factory):
    return data_product_factory.create()


@pytest.fixture
def data_product_current_version(data_product):
    return data_product.current_version


@pytest.fixture
def schema(schema_factory, data_product_current_version):
    return schema_factory.create(data_product_version=data_product_current_version)


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
    assert response_data_product["id"] == "dp:hmpps_use_of_force"


def test_read_metadata(client, data_product_current_version):
    response = client.get("/data-products/dp:hmpps_use_of_force")

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
        "id": "dp:hmpps_use_of_force",
        "tags": {},
    }


def test_list_data_products(client, data_product_current_version):
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
            "id": "dp:hmpps_use_of_force",
            "tags": {},
        }
    ]


def test_no_data_products(client):
    response = client.get("/data-products")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_create_schema(client, session, data_product_current_version):
    response = client.post(
        "/schemas/dp:hmpps_use_of_force:statement",
        json={
            "tableDescription": "statement desc",
            "columns": [],
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "tableDescription": "statement desc",
        "columns": [],
        "id": "dp:hmpps_use_of_force:v1.0:statement",
    }


def test_create_schema_for_non_existent_product(client):
    response = client.post(
        "/schemas/dp:hmpps_use_of_force:statement",
        json={
            "tableDescription": "statement desc",
            "columns": [],
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_schema_that_already_exists(client, session, schema):
    response = client.post(
        "/schemas/dp:hmpps_use_of_force:statement",
        json={
            "tableDescription": "statement desc",
            "columns": schema.columns,
        },
    )
    assert response.status_code == status.HTTP_409_CONFLICT


def test_read_schema(client, schema):
    response = client.get("/schemas/dp:hmpps_use_of_force:statement")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "tableDescription": "desc",
        "columns": schema.columns,
        "id": "dp:hmpps_use_of_force:v1.0:statement",
    }


def test_read_data_product_with_schema(client, schema):
    response = client.get("/data-products/dp:hmpps_use_of_force")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["schemas"] == [
        {"id": "dp:hmpps_use_of_force:v1.0:statement"}
    ]


def test_missing_data_product(client):
    response = client.get("/data-products/dp:hmpps_use_of_the_force")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Data product does not exist with id dp:hmpps_use_of_the_force"
    }


def test_invalid_id(client):
    response = client.get("/data-products/hmpps_use_of_the_force")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Invalid id: hmpps_use_of_the_force"}


def test_missing_schema(client):
    response = client.get("/data-products/dp:hmpps_use_of_the_force")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": "Data product does not exist with id dp:hmpps_use_of_the_force"
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
        "/data-products/dp:hmpps_use_of_the_force",
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
        "detail": "Data product does not exist with id dp:hmpps_use_of_the_force"
    }


def test_update_data_product(client, session, data_product_current_version):
    response = client.put(
        "/data-products/dp:hmpps_use_of_force",
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
        "id": "dp:hmpps_use_of_force",
        "name": "hmpps_use_of_force",
        "tags": {},
        "schemas": [],
        "version": "v1.1",
    }


def test_remove_column_from_schema(client, schema):
    response = client.put(
        "/schemas/dp:hmpps_use_of_force:statement",
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
            "id": "dp:hmpps_use_of_force",
            "name": "hmpps_use_of_force",
            "retentionPeriod": 3000,
            "schemas": [],
            "status": "draft",
            "tags": {},
            "version": "v2.0",
        },
    }


def test_minor_schema_update(client, schema):
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
        "/schemas/dp:hmpps_use_of_force:statement",
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
            "id": "dp:hmpps_use_of_force",
            "name": "hmpps_use_of_force",
            "retentionPeriod": 3000,
            "schemas": [],
            "status": "draft",
            "tags": {},
            "version": "v1.1",
        },
    }


def test_schema_unchanged(client, schema):
    response = client.put(
        "/schemas/dp:hmpps_use_of_force:statement",
        json={
            "tableDescription": schema.tableDescription,
            "columns": schema.columns,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "tableDescription": "desc",
        "columns": schema.columns,
        "id": "dp:hmpps_use_of_force:v1.0:statement",
        "data_product": {
            "dataProductOwner": "dataplatformlabs@digital.justice.gov.uk",
            "dataProductOwnerDisplayName": "Data Platform Labs",
            "description": "Data product for hmpps_use_of_force dev data",
            "domain": "HMPPS",
            "dpiaRequired": False,
            "email": "dataplatformlabs@digital.justice.gov.uk",
            "id": "dp:hmpps_use_of_force",
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
