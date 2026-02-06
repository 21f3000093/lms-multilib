"""bridge missing revision 3eea03944e74

Revision ID: 3eea03944e74
Revises: 42b2dd45c406
Create Date: 2026-02-05 00:00:00.000000
"""

from alembic import op

# revision identifiers, used by Alembic.
revision = '3eea03944e74'
down_revision = '42b2dd45c406'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # no-op bridge revision to repair missing history
    pass


def downgrade() -> None:
    # no-op
    pass
