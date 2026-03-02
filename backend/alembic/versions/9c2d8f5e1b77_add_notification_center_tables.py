"""add notification center tables

Revision ID: 9c2d8f5e1b77
Revises: 4f4412e07997
Create Date: 2026-03-02 23:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9c2d8f5e1b77"
down_revision: Union[str, Sequence[str], None] = "4f4412e07997"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("category", sa.String(), nullable=False, server_default="general"),
        sa.Column("sender_admin_id", sa.Integer(), nullable=True),
        sa.Column("target_type", sa.String(), nullable=False, server_default="all_admins"),
        sa.Column("target_library_id", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["sender_admin_id"], ["admins.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["target_library_id"], ["libraries.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notifications_id"), "notifications", ["id"], unique=False)
    op.create_index(op.f("ix_notifications_category"), "notifications", ["category"], unique=False)
    op.create_index(op.f("ix_notifications_sender_admin_id"), "notifications", ["sender_admin_id"], unique=False)
    op.create_index(op.f("ix_notifications_target_type"), "notifications", ["target_type"], unique=False)
    op.create_index(op.f("ix_notifications_target_library_id"), "notifications", ["target_library_id"], unique=False)
    op.create_index(op.f("ix_notifications_is_active"), "notifications", ["is_active"], unique=False)
    op.create_index(op.f("ix_notifications_created_at"), "notifications", ["created_at"], unique=False)

    op.create_table(
        "notification_recipients",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("notification_id", sa.Integer(), nullable=False),
        sa.Column("admin_id", sa.Integer(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("read_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["admin_id"], ["admins.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["notification_id"], ["notifications.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("notification_id", "admin_id", name="uq_notification_recipient"),
    )
    op.create_index(op.f("ix_notification_recipients_id"), "notification_recipients", ["id"], unique=False)
    op.create_index(
        op.f("ix_notification_recipients_notification_id"),
        "notification_recipients",
        ["notification_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notification_recipients_admin_id"),
        "notification_recipients",
        ["admin_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notification_recipients_is_read"),
        "notification_recipients",
        ["is_read"],
        unique=False,
    )
    op.create_index(
        "idx_notification_recipient_admin_unread_created",
        "notification_recipients",
        ["admin_id", "is_read", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_notification_recipient_admin_unread_created", table_name="notification_recipients")
    op.drop_index(op.f("ix_notification_recipients_is_read"), table_name="notification_recipients")
    op.drop_index(op.f("ix_notification_recipients_admin_id"), table_name="notification_recipients")
    op.drop_index(op.f("ix_notification_recipients_notification_id"), table_name="notification_recipients")
    op.drop_index(op.f("ix_notification_recipients_id"), table_name="notification_recipients")
    op.drop_table("notification_recipients")

    op.drop_index(op.f("ix_notifications_created_at"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_is_active"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_target_library_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_target_type"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_sender_admin_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_category"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_id"), table_name="notifications")
    op.drop_table("notifications")
