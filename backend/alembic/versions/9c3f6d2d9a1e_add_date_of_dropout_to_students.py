"""add_date_of_dropout_to_students

Revision ID: 9c3f6d2d9a1e
Revises: 4f4412e07997
Create Date: 2026-02-05 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '9c3f6d2d9a1e'
down_revision = '4f4412e07997'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('students', sa.Column('date_of_dropout', sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column('students', 'date_of_dropout')
