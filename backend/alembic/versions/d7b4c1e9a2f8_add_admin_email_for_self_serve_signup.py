"""add admin email for self-serve signup

Revision ID: d7b4c1e9a2f8
Revises: c6d9e1a2b3f4
Create Date: 2026-03-16 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d7b4c1e9a2f8"
down_revision: Union[str, Sequence[str], None] = "c6d9e1a2b3f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("admins", sa.Column("email", sa.String(), nullable=True))
    op.create_index("ix_admins_email", "admins", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_admins_email", table_name="admins")
    op.drop_column("admins", "email")
