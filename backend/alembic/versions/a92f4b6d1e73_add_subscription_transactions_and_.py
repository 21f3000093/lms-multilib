"""add subscription transactions and webhook events

Revision ID: a92f4b6d1e73
Revises: d4b7a1c9e8f0
Create Date: 2026-03-12 00:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a92f4b6d1e73"
down_revision: Union[str, Sequence[str], None] = "d4b7a1c9e8f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "subscription_transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("subscription_id", sa.Integer(), nullable=True),
        sa.Column("library_id", sa.Integer(), nullable=False),
        sa.Column("plan_id", sa.Integer(), nullable=True),
        sa.Column("amount_paise", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(), nullable=False, server_default="INR"),
        sa.Column("seats_billed", sa.Integer(), nullable=False),
        sa.Column("billing_months", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="created"),
        sa.Column("gateway_order_id", sa.String(), nullable=True),
        sa.Column("gateway_payment_id", sa.String(), nullable=True),
        sa.Column("gateway_signature", sa.String(), nullable=True),
        sa.Column("idempotency_key", sa.String(), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=True),
        sa.Column("period_end", sa.Date(), nullable=True),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("gateway_payload_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["library_id"], ["libraries.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plan_id"], ["subscription_plans.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["subscription_id"], ["subscriptions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_subscription_transactions_id"), "subscription_transactions", ["id"], unique=False)
    op.create_index(
        op.f("ix_subscription_transactions_subscription_id"),
        "subscription_transactions",
        ["subscription_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_subscription_transactions_library_id"),
        "subscription_transactions",
        ["library_id"],
        unique=False,
    )
    op.create_index(op.f("ix_subscription_transactions_plan_id"), "subscription_transactions", ["plan_id"], unique=False)
    op.create_index(op.f("ix_subscription_transactions_status"), "subscription_transactions", ["status"], unique=False)
    op.create_index(
        op.f("ix_subscription_transactions_gateway_order_id"),
        "subscription_transactions",
        ["gateway_order_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_subscription_transactions_gateway_payment_id"),
        "subscription_transactions",
        ["gateway_payment_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_subscription_transactions_idempotency_key"),
        "subscription_transactions",
        ["idempotency_key"],
        unique=True,
    )
    op.create_index(
        "idx_subscription_transactions_library_created",
        "subscription_transactions",
        ["library_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "idx_subscription_transactions_subscription_created",
        "subscription_transactions",
        ["subscription_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "idx_subscription_transactions_status_created",
        "subscription_transactions",
        ["status", "created_at"],
        unique=False,
    )

    op.create_table(
        "subscription_webhook_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("gateway_event_id", sa.String(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("processed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("processed_at", sa.DateTime(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_subscription_webhook_events_id"), "subscription_webhook_events", ["id"], unique=False)
    op.create_index(
        op.f("ix_subscription_webhook_events_gateway_event_id"),
        "subscription_webhook_events",
        ["gateway_event_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_subscription_webhook_events_event_type"),
        "subscription_webhook_events",
        ["event_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_subscription_webhook_events_processed"),
        "subscription_webhook_events",
        ["processed"],
        unique=False,
    )
    op.create_index(
        op.f("ix_subscription_webhook_events_created_at"),
        "subscription_webhook_events",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_subscription_webhook_events_created_at"), table_name="subscription_webhook_events")
    op.drop_index(op.f("ix_subscription_webhook_events_processed"), table_name="subscription_webhook_events")
    op.drop_index(op.f("ix_subscription_webhook_events_event_type"), table_name="subscription_webhook_events")
    op.drop_index(op.f("ix_subscription_webhook_events_gateway_event_id"), table_name="subscription_webhook_events")
    op.drop_index(op.f("ix_subscription_webhook_events_id"), table_name="subscription_webhook_events")
    op.drop_table("subscription_webhook_events")

    op.drop_index("idx_subscription_transactions_status_created", table_name="subscription_transactions")
    op.drop_index("idx_subscription_transactions_subscription_created", table_name="subscription_transactions")
    op.drop_index("idx_subscription_transactions_library_created", table_name="subscription_transactions")
    op.drop_index(op.f("ix_subscription_transactions_idempotency_key"), table_name="subscription_transactions")
    op.drop_index(op.f("ix_subscription_transactions_gateway_payment_id"), table_name="subscription_transactions")
    op.drop_index(op.f("ix_subscription_transactions_gateway_order_id"), table_name="subscription_transactions")
    op.drop_index(op.f("ix_subscription_transactions_status"), table_name="subscription_transactions")
    op.drop_index(op.f("ix_subscription_transactions_plan_id"), table_name="subscription_transactions")
    op.drop_index(op.f("ix_subscription_transactions_library_id"), table_name="subscription_transactions")
    op.drop_index(op.f("ix_subscription_transactions_subscription_id"), table_name="subscription_transactions")
    op.drop_index(op.f("ix_subscription_transactions_id"), table_name="subscription_transactions")
    op.drop_table("subscription_transactions")
