"""Unique constraint on name and version

Revision ID: e3b6181569e2
Revises: b076b332cf17
Create Date: 2023-12-19 11:08:22.980843

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e3b6181569e2"  # pragma: allowlist secret
down_revision: Union[str, None] = "b076b332cf17"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_data_products_name", "data_products")
    op.create_index(
        "ix_data_products_name_version",
        "data_products",
        columns=["name", "version"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_data_products_name_version", "data_products")
    op.create_index(
        "ix_data_products_name", "data_products", columns=["name"], unique=True
    )
