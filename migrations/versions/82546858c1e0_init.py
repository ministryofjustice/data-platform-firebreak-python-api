"""init

Revision ID: 82546858c1e0
Revises:
Create Date: 2023-12-18 14:59:55.053857

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "82546858c1e0"  # pragma: allowlist secret
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataproducts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("domain", sa.String(), nullable=False),
        sa.Column("dataProductOwner", sa.String(), nullable=False),
        sa.Column("dataProductOwnerDisplayName", sa.String(), nullable=False),
        sa.Column("dataProductMaintainer", sa.String(), nullable=True),
        sa.Column("dataProductMaintainerDisplayName", sa.String(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("draft", "published", "retired", name="status"),
            nullable=False,
        ),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("retentionPeriod", sa.Integer(), nullable=False),
        sa.Column("dpiaRequired", sa.Boolean(), nullable=False),
        sa.Column("dpiaLocation", sa.String(), nullable=True),
        sa.Column("lastUpdated", sa.DateTime(), nullable=True),
        sa.Column("creationDate", sa.DateTime(), nullable=True),
        sa.Column("s3Location", sa.String(), nullable=True),
        sa.Column("rowCount", sa.Integer(), nullable=True),
        sa.Column("version", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.Column("tags", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_dataproducts_name"), "dataproducts", ["name"], unique=True)
    op.create_table(
        "schemas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("data_product_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("tableDescription", sa.String(), nullable=False),
        sa.Column("columns", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(
            ["data_product_id"],
            ["dataproducts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_schemas_name"), "schemas", ["name"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_schemas_name"), table_name="schemas")
    op.drop_table("schemas")
    op.drop_index(op.f("ix_dataproducts_name"), table_name="dataproducts")
    op.drop_table("dataproducts")
    sa.Enum(name="status").drop(op.get_bind(), checkfirst=False)
