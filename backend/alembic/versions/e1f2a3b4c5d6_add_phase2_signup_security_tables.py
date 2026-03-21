"""add phase2 signup security tables

Revision ID: e1f2a3b4c5d6
Revises: d7b4c1e9a2f8
Create Date: 2026-03-16 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e1f2a3b4c5d6"
down_revision: Union[str, Sequence[str], None] = "d7b4c1e9a2f8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("admins", sa.Column("email_verified_at", sa.DateTime(), nullable=True))
    op.create_index("ix_admins_email_verified_at", "admins", ["email_verified_at"], unique=False)

    op.create_table(
        "signup_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("public_id", sa.String(), nullable=False),
        sa.Column("library_name", sa.String(), nullable=False),
        sa.Column("max_seats", sa.Integer(), nullable=False),
        sa.Column("contact_phone", sa.String(), nullable=False),
        sa.Column("address", sa.String(), nullable=True),
        sa.Column("admin_username", sa.String(), nullable=False),
        sa.Column("admin_email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("normalized_username", sa.String(), nullable=False),
        sa.Column("normalized_email", sa.String(), nullable=False),
        sa.Column("normalized_phone", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False, server_default="pending_email_verification"),
        sa.Column("submitted_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("verification_sent_at", sa.DateTime(), nullable=True),
        sa.Column("verified_at", sa.DateTime(), nullable=True),
        sa.Column("approved_at", sa.DateTime(), nullable=True),
        sa.Column("rejected_at", sa.DateTime(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("created_library_id", sa.Integer(), nullable=True),
        sa.Column("created_admin_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["created_admin_id"], ["admins.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["created_library_id"], ["libraries.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("public_id"),
    )
    op.create_index("ix_signup_requests_public_id", "signup_requests", ["public_id"], unique=True)
    op.create_index("ix_signup_requests_normalized_username", "signup_requests", ["normalized_username"], unique=False)
    op.create_index("ix_signup_requests_normalized_email", "signup_requests", ["normalized_email"], unique=False)
    op.create_index("ix_signup_requests_normalized_phone", "signup_requests", ["normalized_phone"], unique=False)
    op.create_index("ix_signup_requests_status", "signup_requests", ["status"], unique=False)
    op.create_index("ix_signup_requests_expires_at", "signup_requests", ["expires_at"], unique=False)
    op.create_index("ix_signup_requests_created_library_id", "signup_requests", ["created_library_id"], unique=False)
    op.create_index("ix_signup_requests_created_admin_id", "signup_requests", ["created_admin_id"], unique=False)
    op.create_index("idx_signup_requests_status_submitted", "signup_requests", ["status", "submitted_at"], unique=False)

    op.create_table(
        "auth_action_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("purpose", sa.String(), nullable=False),
        sa.Column("token_hash", sa.String(), nullable=False),
        sa.Column("target_email", sa.String(), nullable=False),
        sa.Column("signup_request_id", sa.Integer(), nullable=True),
        sa.Column("admin_id", sa.Integer(), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("consumed_at", sa.DateTime(), nullable=True),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_attempts", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("payload_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["admin_id"], ["admins.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["signup_request_id"], ["signup_requests.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("ix_auth_action_tokens_purpose", "auth_action_tokens", ["purpose"], unique=False)
    op.create_index("ix_auth_action_tokens_token_hash", "auth_action_tokens", ["token_hash"], unique=True)
    op.create_index("ix_auth_action_tokens_target_email", "auth_action_tokens", ["target_email"], unique=False)
    op.create_index("ix_auth_action_tokens_signup_request_id", "auth_action_tokens", ["signup_request_id"], unique=False)
    op.create_index("ix_auth_action_tokens_admin_id", "auth_action_tokens", ["admin_id"], unique=False)
    op.create_index("ix_auth_action_tokens_expires_at", "auth_action_tokens", ["expires_at"], unique=False)
    op.create_index("ix_auth_action_tokens_consumed_at", "auth_action_tokens", ["consumed_at"], unique=False)
    op.create_index("idx_auth_action_tokens_purpose_email", "auth_action_tokens", ["purpose", "target_email"], unique=False)

    op.create_table(
        "auth_attempt_trackers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("scope_type", sa.String(), nullable=False),
        sa.Column("scope_key", sa.String(), nullable=False),
        sa.Column("failure_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("locked_until", sa.DateTime(), nullable=True),
        sa.Column("captcha_required_until", sa.DateTime(), nullable=True),
        sa.Column("last_failure_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scope_type", "scope_key", name="uq_auth_attempt_trackers_scope"),
    )
    op.create_index("ix_auth_attempt_trackers_locked_until", "auth_attempt_trackers", ["locked_until"], unique=False)
    op.create_index("ix_auth_attempt_trackers_captcha_required_until", "auth_attempt_trackers", ["captcha_required_until"], unique=False)
    op.create_index("idx_auth_attempt_trackers_scope", "auth_attempt_trackers", ["scope_type", "scope_key"], unique=False)

    op.create_table(
        "auth_security_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("outcome", sa.String(), nullable=False),
        sa.Column("ip_address", sa.String(), nullable=True),
        sa.Column("identifier", sa.String(), nullable=True),
        sa.Column("target_email", sa.String(), nullable=True),
        sa.Column("signup_request_id", sa.Integer(), nullable=True),
        sa.Column("admin_id", sa.Integer(), nullable=True),
        sa.Column("metadata_json", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["admin_id"], ["admins.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["signup_request_id"], ["signup_requests.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_auth_security_events_event_type", "auth_security_events", ["event_type"], unique=False)
    op.create_index("ix_auth_security_events_outcome", "auth_security_events", ["outcome"], unique=False)
    op.create_index("ix_auth_security_events_ip_address", "auth_security_events", ["ip_address"], unique=False)
    op.create_index("ix_auth_security_events_identifier", "auth_security_events", ["identifier"], unique=False)
    op.create_index("ix_auth_security_events_target_email", "auth_security_events", ["target_email"], unique=False)
    op.create_index("ix_auth_security_events_signup_request_id", "auth_security_events", ["signup_request_id"], unique=False)
    op.create_index("ix_auth_security_events_admin_id", "auth_security_events", ["admin_id"], unique=False)
    op.create_index("ix_auth_security_events_created_at", "auth_security_events", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_auth_security_events_created_at", table_name="auth_security_events")
    op.drop_index("ix_auth_security_events_admin_id", table_name="auth_security_events")
    op.drop_index("ix_auth_security_events_signup_request_id", table_name="auth_security_events")
    op.drop_index("ix_auth_security_events_target_email", table_name="auth_security_events")
    op.drop_index("ix_auth_security_events_identifier", table_name="auth_security_events")
    op.drop_index("ix_auth_security_events_ip_address", table_name="auth_security_events")
    op.drop_index("ix_auth_security_events_outcome", table_name="auth_security_events")
    op.drop_index("ix_auth_security_events_event_type", table_name="auth_security_events")
    op.drop_table("auth_security_events")

    op.drop_index("idx_auth_attempt_trackers_scope", table_name="auth_attempt_trackers")
    op.drop_index("ix_auth_attempt_trackers_captcha_required_until", table_name="auth_attempt_trackers")
    op.drop_index("ix_auth_attempt_trackers_locked_until", table_name="auth_attempt_trackers")
    op.drop_table("auth_attempt_trackers")

    op.drop_index("idx_auth_action_tokens_purpose_email", table_name="auth_action_tokens")
    op.drop_index("ix_auth_action_tokens_consumed_at", table_name="auth_action_tokens")
    op.drop_index("ix_auth_action_tokens_expires_at", table_name="auth_action_tokens")
    op.drop_index("ix_auth_action_tokens_admin_id", table_name="auth_action_tokens")
    op.drop_index("ix_auth_action_tokens_signup_request_id", table_name="auth_action_tokens")
    op.drop_index("ix_auth_action_tokens_target_email", table_name="auth_action_tokens")
    op.drop_index("ix_auth_action_tokens_token_hash", table_name="auth_action_tokens")
    op.drop_index("ix_auth_action_tokens_purpose", table_name="auth_action_tokens")
    op.drop_table("auth_action_tokens")

    op.drop_index("idx_signup_requests_status_submitted", table_name="signup_requests")
    op.drop_index("ix_signup_requests_created_admin_id", table_name="signup_requests")
    op.drop_index("ix_signup_requests_created_library_id", table_name="signup_requests")
    op.drop_index("ix_signup_requests_expires_at", table_name="signup_requests")
    op.drop_index("ix_signup_requests_status", table_name="signup_requests")
    op.drop_index("ix_signup_requests_normalized_phone", table_name="signup_requests")
    op.drop_index("ix_signup_requests_normalized_email", table_name="signup_requests")
    op.drop_index("ix_signup_requests_normalized_username", table_name="signup_requests")
    op.drop_index("ix_signup_requests_public_id", table_name="signup_requests")
    op.drop_table("signup_requests")

    op.drop_index("ix_admins_email_verified_at", table_name="admins")
    op.drop_column("admins", "email_verified_at")
