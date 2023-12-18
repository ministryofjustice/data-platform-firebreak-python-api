import json
import logging
from tempfile import NamedTemporaryFile
from unittest import TestCase
from unittest.mock import patch

import pytest

from daap_api.services import metadata_services
from daap_api.services.data_platform_paths import JsonSchemaName
from daap_api.services.metadata_services import (
    DataProductMetadata,
    DataProductSchema,
    format_table_schema,
)

TestCase.maxDiff = None

test_metadata_pass = {
    "name": "test_product",
    "description": "just testing the metadata json validation/registration",
    "domain": "MoJ",
    "dataProductOwner": "matthew.laverty@justice.gov.uk",
    "dataProductOwnerDisplayName": "matt laverty",
    "email": "matthew.laverty@justice.gov.uk",
    "status": "draft",
    "retentionPeriod": 3000,
    "dpiaRequired": False,
}

test_metadata_with_schemas = {
    "name": "test_product",
    "description": "just testing the metadata json validation/registration",
    "domain": "MoJ",
    "dataProductOwner": "matthew.laverty@justice.gov.uk",
    "dataProductOwnerDisplayName": "matt laverty",
    "email": "matthew.laverty@justice.gov.uk",
    "status": "draft",
    "retentionPeriod": 3000,
    "dpiaRequired": False,
    "schemas": ["test_product"],
}

test_metadata_fail = {
    "name": "test_product(bad name)",
    "description": "just testing the metadata json validation/registration",
    "domain": "MoJ",
    "dataProductOwner": "matthew.laverty@justice.gov.uk",
    "dataProductOwnerDisplayName": "matt laverty",
    "email": "matthew.laverty@justice.gov.uk",
    "status": "draft",
    "dpiaRequired": False,
}

test_schema_pass = {
    "tableDescription": "table has schema to pass test",
    "columns": [
        {
            "name": "col_1",
            "type": "bigint",
            "description": "ABCDEFGHIJKLMNOPQRSTUVWXY",
        },
        {"name": "col_2", "type": "tinyint", "description": "ABCDEFGHIJKL"},
        {
            "name": "col_3",
            "type": "int",
            "description": "ABCDEFGHIJKLMNOPQRSTUVWX",
        },
        {"name": "col_4", "type": "smallint", "description": "ABCDEFGHIJKLMN"},
    ],
}

test_schema_fail = {
    "tableDescription": "table has schema to pass test",
    "columns": [
        {
            "name": "col()()_1",
            "type": "bigint",
            "description": "ABCDEFGHIJKLMNOPQRSTUVWXY",
        },
        {"name": "col_2", "type": "tinyint", "description": "ABCDEFGHIJKL"},
        {
            "name": "col_3",
            "type": "int",
            "description": "ABCDEFGHIJKLMNOPQRSTUVWX",
        },
        {"name": "col_4", "type": "smallint", "description": "ABCDEFGHIJKLMN"},
    ],
}

test_glue_table_input = {
    "DatabaseName": "test_product_v1",
    "TableInput": {
        "Description": "table has schema to pass test",
        "Name": "test_table",
        "Owner": "matthew.laverty@justice.gov.uk",
        "Retention": 3000,
        "Parameters": {},
        "PartitionKeys": [],
        "StorageDescriptor": {
            "BucketColumns": [],
            "Columns": [
                {
                    "Name": "col_1",
                    "Type": "bigint",
                    "Comment": "ABCDEFGHIJKLMNOPQRSTUVWXY",
                },
                {"Name": "col_2", "Type": "tinyint", "Comment": "ABCDEFGHIJKL"},
                {
                    "Name": "col_3",
                    "Type": "int",
                    "Comment": "ABCDEFGHIJKLMNOPQRSTUVWX",
                },
                {"Name": "col_4", "Type": "smallint", "Comment": "ABCDEFGHIJKLMN"},
            ],
            "Compressed": False,
            "InputFormat": "",
            "Location": "",
            "NumberOfBuckets": -1,
            "OutputFormat": "",
            "Parameters": {},
            "SerdeInfo": {},
            "SortColumns": [],
            "StoredAsSubDirectories": False,
        },
        "TableType": "EXTERNAL_TABLE",
    },
}


def load_test_data_product_metadata(
    bucket_name, s3_client, metadata=test_metadata_pass
):
    json_data = json.dumps(metadata)
    s3_client.put_object(
        Body=json_data,
        Bucket=bucket_name,
        Key="test_product/v1.0/metadata.json",
    )


def load_test_schema(bucket_name, s3_client, schema=test_glue_table_input):
    json_data = json.dumps(schema)
    s3_client.put_object(
        Body=json_data,
        Bucket=bucket_name,
        Key="test_product/v1.0/test_table/schema.json",
    )


class TestDataProductMetadata:
    @pytest.fixture(autouse=True)
    def setup(self, metadata_bucket):
        self.bucket_name = metadata_bucket

    def test_metadata_exist(self, s3_client):
        # populate some folders & files to mock s3 bucket
        file_text = json.dumps(test_metadata_pass)
        with NamedTemporaryFile(delete=True, suffix=".json") as tmp:
            with open(tmp.name, "w", encoding="UTF-8") as f:
                f.write(file_text)

            s3_client.upload_file(
                tmp.name, self.bucket_name, "test_product/v1.0/metadata.json"
            )

        with patch("daap_api.services.data_platform_paths.s3_client", s3_client):
            md = DataProductMetadata(
                data_product_name=test_metadata_pass["name"],
                input_data=test_metadata_pass,
            )
            assert md.exists

    def test_metadata_does_not_exist(self):
        with patch(
            "daap_api.services.data_platform_paths.get_latest_version", lambda _: "v1.0"
        ):
            md = DataProductMetadata(
                test_metadata_pass["name"],
                input_data=test_metadata_pass,
            )
            assert not md.exists

    validation_md_inputs = [(test_metadata_pass, True), (test_metadata_fail, False)]

    @pytest.mark.parametrize("test_metadata, expected_out", validation_md_inputs)
    def test_valid_metadata(self, test_metadata, expected_out):
        with patch(
            "daap_api.services.data_platform_paths.get_latest_version", lambda _: "v1.0"
        ):
            md = DataProductMetadata(
                test_metadata["name"],
                input_data=test_metadata,
            )
            assert md.valid == expected_out

    def test_write_json_to_s3(self, s3_client):
        with patch(
            "daap_api.services.data_platform_paths.get_latest_version", lambda _: "v1.0"
        ):
            md = DataProductMetadata(
                test_metadata_pass["name"],
                input_data=test_metadata_pass,
            )

            md.write_json_to_s3("test_product/v1.0/metadata.json")

        response = s3_client.get_object(
            Bucket=self.bucket_name, Key="test_product/v1.0/metadata.json"
        )
        data = response.get("Body").read().decode("utf-8")
        from_s3 = json.loads(data)

        assert test_metadata_pass == from_s3

    def test_load_json_schema_object(self, s3_client):
        load_test_data_product_metadata(self.bucket_name, s3_client)
        with patch(
            "daap_api.services.data_platform_paths.get_latest_version", lambda _: "v1.0"
        ):
            loaded_metadata = (
                DataProductMetadata(
                    test_metadata_pass["name"],
                    input_data=None,
                )
                .load()
                .latest_version_saved_data
            )

            assert loaded_metadata == test_metadata_pass


class TestDataProductSchema:
    @pytest.fixture(autouse=True)
    def setup(self, metadata_bucket):
        self.bucket_name = metadata_bucket

    validation_schema_inputs = [(test_schema_pass, True), (test_schema_fail, False)]

    @pytest.mark.parametrize("test_schema, expected_out", validation_schema_inputs)
    def test_valid_schema(self, test_schema, expected_out, s3_client):
        load_test_data_product_metadata(self.bucket_name, s3_client)
        with patch(
            "daap_api.services.data_platform_paths.get_latest_version", lambda _: "v1.0"
        ):
            md = DataProductSchema(
                data_product_name="test_product",
                table_name="test_table",
                input_data=test_schema,
            )
            assert md.valid == expected_out

    @pytest.mark.parametrize(
        "data_product_name, expected_output",
        [("test_product", True), ("test_product2", False)],
    )
    def test_does_data_product_metadata_exist(
        self, data_product_name, expected_output, s3_client
    ):
        load_test_data_product_metadata(self.bucket_name, s3_client)

        with patch(
            "daap_api.services.data_platform_paths.get_latest_version", lambda _: "v1.0"
        ):
            schema = DataProductSchema(
                data_product_name=data_product_name,
                table_name="test_table",
                input_data=test_schema_pass,
            )
            assert schema.has_registered_data_product == expected_output

    def test_convert_schema_to_glue_table_input_csv(self, s3_client):
        load_test_data_product_metadata(self.bucket_name, s3_client)
        with patch(
            "daap_api.services.data_platform_paths.get_latest_version", lambda _: "v1.0"
        ):
            schema = DataProductSchema(
                data_product_name="test_product",
                table_name="test_table",
                input_data=test_schema_pass,
            )

            schema.convert_schema_to_glue_table_input_csv()

            # assert schema.data == test_glue_table_input
            TestCase().assertDictEqual(test_glue_table_input, schema.data)

    @pytest.mark.parametrize(
        "metadata, expected",
        [(test_metadata_pass, False), (test_metadata_with_schemas, True)],
    )
    def test_schema_parent_metadata_has_registered_schemas(
        self, metadata, expected, s3_client
    ):
        load_test_data_product_metadata(self.bucket_name, s3_client, metadata)
        with patch(
            "daap_api.services.data_platform_paths.get_latest_version", lambda _: "v1.0"
        ):
            schema = DataProductSchema(
                data_product_name="test_product",
                table_name="test_table",
                input_data=test_schema_pass,
            )
            assert schema.parent_product_has_registered_schema == expected


@pytest.mark.parametrize(
    "glue_schema, expected",
    [(test_glue_table_input, test_schema_pass)],
)
def test_format_table_schema(glue_schema, expected):
    out_schema = format_table_schema(glue_schema)

    assert out_schema == expected
