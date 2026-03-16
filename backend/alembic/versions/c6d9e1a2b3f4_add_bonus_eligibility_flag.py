"""add bonus eligibility flag to subscriptions

Revision ID: c6d9e1a2b3f4
Revises: b5c8d2e7f1a4
Create Date: 2026-03-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c6d9e1a2b3f4"
down_revision: Union[str, Sequence[str], None] = "b5c8d2e7f1a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "subscriptions",
        sa.Column("bonus_eligible", sa.Boolean(), nullable=False, server_default=sa.true()),
    )

    # Legacy subscriptions existed before this flag and should not receive first-time bonus.
    op.execute(sa.text("UPDATE subscriptions SET bonus_eligible = false"))

    # Some legacy libraries may still not have a subscription row yet.
    # Seed them now as non-eligible so bonus logic remains deterministic.
    op.execute(
        sa.text(
            """
            INSERT INTO subscriptions (
                library_id,
                status,
                auto_renew,
                cancel_at_period_end,
                is_trial,
                trial_valid_until,
                bonus_eligible,
                created_at,
                updated_at
            )
            SELECT
                l.id,
                'inactive',
                false,
                false,
                false,
                NULL,
                false,
                now(),
                now()
            FROM libraries l
            LEFT JOIN subscriptions s ON s.library_id = l.id
            WHERE s.id IS NULL
            """
        )
    )


def downgrade() -> None:
    op.drop_column("subscriptions", "bonus_eligible")
