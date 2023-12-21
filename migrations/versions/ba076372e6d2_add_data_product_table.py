"""Add data product table

Revision ID: ba076372e6d2
Revises: 89cac6c73079
Create Date: 2023-12-21 15:08:42.133330

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ba076372e6d2"  # pragma: allowlist secret
down_revision: Union[str, None] = "89cac6c73079"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "data_products",
        sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("current_version_id", sa.Integer(), nullable=False),
    )
    op.create_foreign_key(
        None, "data_products", "data_product_versions", ["current_version_id"], ["id"]
    )


def downgrade() -> None:
    op.drop_table("data_products")
