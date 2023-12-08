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
