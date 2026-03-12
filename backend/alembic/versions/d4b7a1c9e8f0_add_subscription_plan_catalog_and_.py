"""add subscription plan catalog and extend subscriptions

Revision ID: d4b7a1c9e8f0
Revises: f2a1c3d4e5f6
Create Date: 2026-03-12 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d4b7a1c9e8f0"
down_revision: Union[str, Sequence[str], None] = "f2a1c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "subscription_plans",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("billing_months", sa.Integer(), nullable=False),
        sa.Column("price_per_seat_paise", sa.Integer(), nullable=False),
        sa.Column("discount_percent", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("bonus_months", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index(op.f("ix_subscription_plans_id"), "subscription_plans", ["id"], unique=False)
    op.create_index(op.f("ix_subscription_plans_code"), "subscription_plans", ["code"], unique=True)

    op.add_column("subscriptions", sa.Column("plan_id", sa.Integer(), nullable=True))
    op.add_column("subscriptions", sa.Column("current_period_start", sa.Date(), nullable=True))
    op.add_column("subscriptions", sa.Column("current_period_end", sa.Date(), nullable=True))
    op.add_column("subscriptions", sa.Column("grace_until", sa.DateTime(), nullable=True))
    op.add_column("subscriptions", sa.Column("auto_renew", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column(
        "subscriptions",
        sa.Column("cancel_at_period_end", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column("subscriptions", sa.Column("gateway_customer_id", sa.String(), nullable=True))
    op.add_column("subscriptions", sa.Column("gateway_subscription_id", sa.String(), nullable=True))
    op.add_column(
        "subscriptions",
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
    )
    op.add_column(
        "subscriptions",
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
    )
    op.create_foreign_key(
        "fk_subscriptions_plan_id_subscription_plans",
        "subscriptions",
        "subscription_plans",
        ["plan_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("idx_subscriptions_plan_id", "subscriptions", ["plan_id"], unique=False)
    op.create_index("idx_subscriptions_grace_until", "subscriptions", ["grace_until"], unique=False)
    op.create_index(
        "idx_subscriptions_status_valid_until",
        "subscriptions",
        ["status", "valid_until"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_subscriptions_status_valid_until", table_name="subscriptions")
    op.drop_index("idx_subscriptions_grace_until", table_name="subscriptions")
    op.drop_index("idx_subscriptions_plan_id", table_name="subscriptions")
    op.drop_constraint("fk_subscriptions_plan_id_subscription_plans", "subscriptions", type_="foreignkey")

    op.drop_column("subscriptions", "updated_at")
    op.drop_column("subscriptions", "created_at")
    op.drop_column("subscriptions", "gateway_subscription_id")
    op.drop_column("subscriptions", "gateway_customer_id")
    op.drop_column("subscriptions", "cancel_at_period_end")
    op.drop_column("subscriptions", "auto_renew")
    op.drop_column("subscriptions", "grace_until")
    op.drop_column("subscriptions", "current_period_end")
    op.drop_column("subscriptions", "current_period_start")
    op.drop_column("subscriptions", "plan_id")

    op.drop_index(op.f("ix_subscription_plans_code"), table_name="subscription_plans")
    op.drop_index(op.f("ix_subscription_plans_id"), table_name="subscription_plans")
    op.drop_table("subscription_plans")
