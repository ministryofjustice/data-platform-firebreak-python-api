import pytest

from daap_api.models.orm.metadata_orm_models import DataProductTable, SchemaTable
from daap_api.services.versioning_service import InvalidUpdate, VersioningService


class TestVersioningService:
    @pytest.fixture
    def starting_metadata(self):
        table1 = SchemaTable(
            name="table1",
            columns=[{"name": "foo", "type": "string", "description": "abc"}],
        )
        table2 = SchemaTable(
            name="table2",
            columns=[{"name": "bar", "type": "int", "description": ""}],
        )
        data_product = DataProductTable(name="abc", domain="test", version="v1.0")
        data_product.schemas.append(table1)
        data_product.schemas.append(table2)
        return data_product

    @pytest.fixture
    def service(self, starting_metadata):
        return VersioningService(starting_metadata)

    def test_remove_schemas(self, service):
        result = service.remove_schemas("table1")
        assert result.id is None
        assert result.version == "v2.0"
        assert result.name == "abc"
        assert [schema.id is None for schema in result.schemas]
        assert [schema.name for schema in result.schemas] == ["table2"]

    def test_minor_metadata_update(self, service):
        result = service.update_metadata(domain="test2")
        assert result != self.starting_metadata
        assert result.version == "v1.1"
        assert result.id is None
        assert result.name == "abc"
        assert result.domain == "test2"
        assert [schema.id is None for schema in result.schemas]
        assert [schema.name for schema in result.schemas] == ["table1", "table2"]

    def test_noop_metadata_update(self, service):
        result = service.update_metadata(domain="test")
        assert result.version == "v1.0"

    def test_minor_schema_update(self, service):
        result = service.update_schema("table1", tableDescription="new description")
        assert result != self.starting_metadata
        assert result.version == "v1.1"
        assert [schema.id is None for schema in result.schemas]
        assert [schema.tableDescription for schema in result.schemas] == [
            "new description",
            None,
        ]

    def test_major_schema_update(self, service):
        result = service.update_schema(
            "table1",
            columns=[{"name": "food", "type": "string", "description": "nom nom"}],
        )
        assert result != self.starting_metadata
        assert result.version == "v2.0"
        assert [schema.id is None for schema in result.schemas]
        assert result.schemas[0].columns == [
            {"name": "food", "type": "string", "description": "nom nom"}
        ]

    def test_unchanged_schema(self, service):
        result = service.update_schema(
            "table1",
            columns=[{"name": "foo", "type": "string", "description": "abc"}],
        )
        assert result.version == "v1.0"

    def test_cannot_update_name(self, service):
        with pytest.raises(InvalidUpdate):
            service.update_metadata(name="new_name")

    def test_cannot_update_without_a_version(self):
        """
        The versioning service must operate on a data product that has
        already been saved to the metadata store - otherwise it won't have
        a version number already.
        """
        with pytest.raises(InvalidUpdate):
            VersioningService(DataProductTable(name="new_product"))
