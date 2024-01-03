"""Rename to snake case

Revision ID: 2bc9da0d5ae0
Revises: ba076372e6d2
Create Date: 2024-01-03 15:20:36.195802

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2bc9da0d5ae0"  # pragma: allowlist secret
down_revision: Union[str, None] = "ba076372e6d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "data_product_versions",
        "dataProductOwner",
        new_column_name="data_product_owner",
    )
    op.alter_column(
        "data_product_versions",
        "dataProductOwnerDisplayName",
        new_column_name="data_product_owner_display_name",
    )
    op.alter_column(
        "data_product_versions",
        "dataProductMaintainer",
        new_column_name="data_product_maintainer",
    )
    op.alter_column(
        "data_product_versions",
        "dataProductMaintainerDisplayName",
        new_column_name="data_product_maintainer_display_name",
    )
    op.alter_column(
        "data_product_versions", "retentionPeriod", new_column_name="retention_period"
    )
    op.alter_column(
        "data_product_versions", "dpiaRequired", new_column_name="dpia_required"
    )
    op.alter_column(
        "data_product_versions", "lastUpdated", new_column_name="last_updated"
    )
    op.alter_column(
        "data_product_versions", "creationDate", new_column_name="creation_date"
    )
    op.alter_column(
        "data_product_versions", "s3Location", new_column_name="s3_location"
    )
    op.alter_column("data_product_versions", "rowCount", new_column_name="row_count")
    op.alter_column(
        "data_product_versions", "dpiaLocation", new_column_name="dpia_location"
    )

    op.alter_column("schemas", "tableDescription", new_column_name="table_description")


def downgrade() -> None:
    op.alter_column(
        "data_product_versions",
        new_column_name="dataProductOwner",
        column_name="data_product_owner",
    )
    op.alter_column(
        "data_product_versions",
        new_column_name="dataProductOwnerDisplayName",
        column_name="data_product_owner_display_name",
    )
    op.alter_column(
        "data_product_versions",
        new_column_name="dataProductMaintainer",
        column_name="data_product_maintainer",
    )
    op.alter_column(
        "data_product_versions",
        new_column_name="dataProductMaintainerDisplayName",
        column_name="data_product_maintainer_display_name",
    )
    op.alter_column(
        "data_product_versions",
        new_column_name="retentionPeriod",
        column_name="retention_period",
    )
    op.alter_column(
        "data_product_versions",
        new_column_name="dpiaRequired",
        column_name="dpia_required",
    )
    op.alter_column(
        "data_product_versions",
        new_column_name="lastUpdated",
        column_name="last_updated",
    )
    op.alter_column(
        "data_product_versions",
        new_column_name="creationDate",
        column_name="creation_date",
    )
    op.alter_column(
        "data_product_versions", new_column_name="s3Location", column_name="s3_location"
    )
    op.alter_column(
        "data_product_versions", new_column_name="rowCount", column_name="row_count"
    )
    op.alter_column(
        "data_product_versions",
        new_column_name="dpiaLocation",
        column_name="dpia_location",
    )

    op.alter_column(
        "schemas", new_column_name="tableDescription", column_name="table_description"
    )
