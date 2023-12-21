"""
Service for automatically versioning data product metadata based on changes.

Any time a change would break consumers of the data product, we increment its
major version.

E.g. removing tables, removing or renaming columns, changing column types

Any time a change is backwards compatable for consumers, we increment its minor version.

E.g. renaming descriptions, adding tables, adding columns
"""

import logging
from enum import Enum

from ..models.orm.metadata_orm_models import DataProductVersionTable, SchemaTable

logger = logging.getLogger(__name__)


UPDATABLE_METADATA_FIELDS = {
    "description",
    "email",
    "dataProductOwner",
    "dataProductOwnerDisplayName",
    "domain",
    "status",
    "dpiaRequired",
    "retentionPeriod",
    "dataProductMaintainer",
    "dataProductMaintainerDisplayName",
    "tags",
}

MINOR_UPDATE_SCHEMA_FIELDS = {"tableDescription"}


class UpdateType(Enum):
    """
    Whether a schema or data product update represents a major or minor update to the data product.

    Minor updates are those which are backwards compatable, e.g. adding a new table.

    Major updates are those which may require data consumers to update their code,
    e.g. if tables or fields are removed.
    """

    Unchanged = 0
    MinorUpdate = 1
    MajorUpdate = 2
    NotAllowed = 3


class InvalidUpdate(Exception):
    """
    Exception thrown when an update cannot be applied to a data product or schema
    """


class VersioningService:
    def __init__(self, current_metadata: DataProductVersionTable):
        if not current_metadata.version:
            raise InvalidUpdate("Current metadata must have a version set")
        self.current_metadata = current_metadata

    def remove_schemas(self, *schemas_to_remove: str) -> DataProductVersionTable:
        """
        Remove one or more schemas from the next version of the data
        product.
        """
        remove_set = set(schemas_to_remove)
        current_schemas = {schema.name for schema in self.current_metadata.schemas}
        schemas_not_in_current = remove_set.difference(current_schemas)
        remaining = current_schemas.difference(remove_set)
        if schemas_not_in_current:
            error = f"Invalid schemas found in schema_list: {sorted(schemas_not_in_current)}"
            raise InvalidUpdate(error)

        logger.info(f"schemas to delete: {schemas_to_remove}")

        # Copy remaining schemas to the new data product
        new_version = self.current_metadata.next_major_version()
        new_version.schemas.extend(
            [
                schema.copy()
                for schema in self.current_metadata.schemas
                if schema.name in remaining
            ]
        )

        return new_version

    def update_metadata(self, **kwargs):
        updated_fields = set(kwargs.keys())
        invalid_fields = updated_fields.difference(UPDATABLE_METADATA_FIELDS)

        if invalid_fields:
            num_fields = len(invalid_fields)
            msg = f"Non-updatable metadata field{('s'[:num_fields!=1])} changed:"
            for f in sorted(invalid_fields):
                msg += f"{f}: {getattr(self.current_metadata, f)} -> {kwargs[f]}; "
            logger.error(msg)
            raise InvalidUpdate(msg)

        with_changes = self.current_metadata.copy(**kwargs)
        if not with_changes.changed_fields(self.current_metadata):
            logging.info("Nothing changed in metadata update - not bumping version")
            return self.current_metadata

        new_version = self.current_metadata.next_minor_version(**kwargs)

        new_version.schemas.extend(
            [schema.copy() for schema in self.current_metadata.schemas]
        )
        return new_version

    def update_schema(self, table_name, **kwargs):
        new_schemas = []
        is_major_update = False

        for schema in self.current_metadata.schemas:
            if schema.name == table_name:
                # Copy the schema with the updated attributes
                new_schema = schema.copy(**kwargs)
                update_type, changes = schema_update_type(schema, new_schema)

                if update_type == UpdateType.Unchanged:
                    logger.error(
                        f"{schema.name} is unchanged - not increasing version number"
                    )
                    return self.current_metadata

                logger.info(f"{schema.name} {update_type}: {changes}")
                is_major_update = update_type == UpdateType.MajorUpdate

                new_schemas.append(new_schema)
            else:
                # Copy any other schemas as they are
                new_schemas.append(schema.copy())

        if is_major_update:
            new_version = self.current_metadata.next_major_version()
        else:
            new_version = self.current_metadata.next_minor_version()

        new_version.schemas.extend(new_schemas)

        return new_version


def detect_column_differences_in_new_version(
    old_schema: SchemaTable, new_schema: SchemaTable
) -> dict:
    """
    Detects and returns what has changed comparing the latest saved version of
    schema with an updated version that has passed validation but not yet been
    converted to a glue table input (is available at self.data_pre_convert)
    """

    types_changed = []
    descriptions_changed = []
    changes = {}

    old_col_dict = {col["name"]: col for col in old_schema.columns}
    new_col_dict = {col["name"]: col for col in new_schema.columns}

    old_col_names = set(old_col_dict.keys())
    new_col_names = set(new_col_dict.keys())

    added_columns = list(new_col_names - old_col_names)
    removed_columns = list(old_col_names - new_col_names)

    # check each column in old schema against column in new schema for type or description
    # changes, if old column exists in new columns
    types_changed = [
        old_col
        for old_col in old_col_dict
        if new_col_dict.get(old_col) is not None
        and not old_col_dict[old_col]["type"] == new_col_dict[old_col]["type"]
    ]
    descriptions_changed = [
        old_col
        for old_col in old_col_dict
        if new_col_dict.get(old_col) is not None
        and not old_col_dict[old_col]["description"]
        == new_col_dict[old_col]["description"]
    ]

    changes["removed_columns"] = removed_columns if removed_columns else None
    changes["added_columns"] = added_columns if added_columns else None
    changes["types_changed"] = types_changed if types_changed else None
    changes["descriptions_changed"] = (
        descriptions_changed if descriptions_changed else None
    )

    return changes


def schema_update_type(
    old_schema: SchemaTable, new_schema: SchemaTable
) -> tuple[UpdateType, dict]:
    """
    Figure out whether changes to the input data represent a major or minor schema update
    and return the changes as a dict, e.g.
        {table_name: {columns:{...}, non_column_fields: {...}}}
    """
    changed_fields = new_schema.changed_fields(old_schema)

    if "columns" in changed_fields:
        column_changes = detect_column_differences_in_new_version(
            old_schema, new_schema
        )

        if any([column_changes["removed_columns"], column_changes["types_changed"]]):
            update_type = UpdateType.MajorUpdate
        elif any(
            [column_changes["added_columns"], column_changes["descriptions_changed"]]
        ):
            update_type = UpdateType.MinorUpdate
        else:
            update_type = UpdateType.Unchanged
    else:
        column_changes = {
            "removed_columns": None,
            "added_columns": None,
            "types_changed": None,
            "descriptions_changed": None,
        }
        if not changed_fields:
            update_type = UpdateType.Unchanged
        elif changed_fields.intersection(MINOR_UPDATE_SCHEMA_FIELDS) == changed_fields:
            update_type = UpdateType.MinorUpdate
        else:
            update_type = UpdateType.MajorUpdate

    # could be returned and used to form notification of change to consumers of data when the
    # notification process is developed
    if not update_type == UpdateType.Unchanged:
        if "columns" in changed_fields:
            changed_fields.remove("columns")
        non_column_changed_fields = (
            [field for field in changed_fields] if changed_fields else None
        )
        all_schema_changes = {
            new_schema.name: {
                "columns": column_changes,
                "non_column_fields": non_column_changed_fields,
            }
        }
    else:
        all_schema_changes = {
            new_schema.name: {
                "columns": column_changes,
                "non_column_fields": None,
            }
        }

    return update_type, all_schema_changes
