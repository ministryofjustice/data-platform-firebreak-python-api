"""Rename table

Revision ID: 89cac6c73079
Revises: e3b6181569e2
Create Date: 2023-12-20 16:25:46.552387

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "89cac6c73079"
down_revision: Union[str, None] = "e3b6181569e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table("data_products", "data_product_versions")


def downgrade() -> None:
    op.rename_table("data_product_versions", "data_products")
