"""add push subscriptions table

Revision ID: f2a1c3d4e5f6
Revises: e8f1a2b3c4d5
Create Date: 2026-03-09 18:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f2a1c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "e8f1a2b3c4d5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "push_subscriptions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("admin_id", sa.Integer(), nullable=False),
        sa.Column("endpoint", sa.String(), nullable=False),
        sa.Column("p256dh", sa.String(), nullable=False),
        sa.Column("auth", sa.String(), nullable=False),
        sa.Column("expiration_time", sa.String(), nullable=True),
        sa.Column("user_agent", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("last_seen_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["admin_id"], ["admins.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("endpoint"),
    )
    op.create_index(op.f("ix_push_subscriptions_id"), "push_subscriptions", ["id"], unique=False)
    op.create_index(op.f("ix_push_subscriptions_admin_id"), "push_subscriptions", ["admin_id"], unique=False)
    op.create_index(op.f("ix_push_subscriptions_endpoint"), "push_subscriptions", ["endpoint"], unique=False)
    op.create_index(
        "idx_push_subscriptions_admin_last_seen",
        "push_subscriptions",
        ["admin_id", "last_seen_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_push_subscriptions_admin_last_seen", table_name="push_subscriptions")
    op.drop_index(op.f("ix_push_subscriptions_endpoint"), table_name="push_subscriptions")
    op.drop_index(op.f("ix_push_subscriptions_admin_id"), table_name="push_subscriptions")
    op.drop_index(op.f("ix_push_subscriptions_id"), table_name="push_subscriptions")
    op.drop_table("push_subscriptions")
