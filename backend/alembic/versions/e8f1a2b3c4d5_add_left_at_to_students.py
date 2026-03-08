"""add left_at to students

Revision ID: e8f1a2b3c4d5
Revises: c1d2e3f4a5b6
Create Date: 2026-03-08 10:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e8f1a2b3c4d5"
down_revision: Union[str, Sequence[str], None] = "c1d2e3f4a5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("students", sa.Column("left_at", sa.DateTime(), nullable=True))
    op.create_index(op.f("ix_students_left_at"), "students", ["left_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_students_left_at"), table_name="students")
    op.drop_column("students", "left_at")
