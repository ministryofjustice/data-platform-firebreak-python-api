"""Rename dataproducts -> data_products

Revision ID: b076b332cf17
Revises: 82546858c1e0
Create Date: 2023-12-18 15:22:25.699579

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b076b332cf17"  # pragma: allowlist secret
down_revision: Union[str, None] = "82546858c1e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "data_products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("domain", sa.String(), nullable=False),
        sa.Column("dataProductOwner", sa.String(), nullable=False),
        sa.Column("dataProductOwnerDisplayName", sa.String(), nullable=False),
        sa.Column("dataProductMaintainer", sa.String(), nullable=True),
        sa.Column("dataProductMaintainerDisplayName", sa.String(), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "draft", "published", "retired", name="status", create_type=False
            ),
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
    op.create_index(
        op.f("ix_data_products_name"), "data_products", ["name"], unique=True
    )
    op.execute("insert into data_products select * from dataproducts")

    op.drop_index("ix_dataproducts_name", table_name="dataproducts")
    op.drop_constraint("schemas_data_product_id_fkey", "schemas", type_="foreignkey")
    op.create_foreign_key(None, "schemas", "data_products", ["data_product_id"], ["id"])
    op.drop_table("dataproducts")


def downgrade() -> None:
    op.create_table(
        "dataproducts",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("domain", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "dataProductOwner", sa.VARCHAR(), autoincrement=False, nullable=False
        ),
        sa.Column(
            "dataProductOwnerDisplayName",
            sa.VARCHAR(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "dataProductMaintainer", sa.VARCHAR(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "dataProductMaintainerDisplayName",
            sa.VARCHAR(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "status",
            postgresql.ENUM(
                "draft", "published", "retired", name="status", create_type=False
            ),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column("email", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("retentionPeriod", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("dpiaRequired", sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.Column("dpiaLocation", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "lastUpdated", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "creationDate", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
        sa.Column("s3Location", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("rowCount", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("version", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("description", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "tags",
            postgresql.JSON(astext_type=sa.Text()),
            autoincrement=False,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="dataproducts_pkey"),
    )
    op.create_index("ix_dataproducts_name", "dataproducts", ["name"], unique=False)

    op.execute("insert into dataproducts select * from data_products")

    op.drop_index(op.f("ix_data_products_name"), table_name="data_products")
    op.drop_constraint("schemas_data_product_id_fkey", "schemas", type_="foreignkey")
    op.create_foreign_key(
        "schemas_data_product_id_fkey",
        "schemas",
        "dataproducts",
        ["data_product_id"],
        ["id"],
    )
    op.drop_table("data_products")
