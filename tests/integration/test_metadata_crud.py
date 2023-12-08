from fastapi.testclient import TestClient

from daap_api.main import app

client = TestClient(app)


def test_read_metadata():
    response = client.get("/data-products/hmpps_use_of_force")
    assert response.status_code == 200
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


def test_read_schema():
    response = client.get("/schemas/hmpps_use_of_force/statement")
    assert response.status_code == 200
    assert response.json() == {
        "tableDescription": "",
        "columns": [
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
        ],
    }


def test_missing_data_product():
    response = client.get("/data-products/hmpps_use_of_the_force")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "no existing metadata found in S3 for "
        "data_product_name='hmpps_use_of_the_force'"
    }


def test_missing_schema():
    response = client.get("/schemas/hmpps_use_of_force/missing")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "no existing schema found in S3 for "
        "data_product_name='hmpps_use_of_force', table_name='missing'"
    }