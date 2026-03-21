"""add google auth identities and signup review fields

Revision ID: f4e5d6c7b8a9
Revises: e1f2a3b4c5d6
Create Date: 2026-03-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f4e5d6c7b8a9"
down_revision: Union[str, Sequence[str], None] = "e1f2a3b4c5d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "signup_requests",
        sa.Column("signup_method", sa.String(), nullable=False, server_default="password"),
    )
    op.add_column("signup_requests", sa.Column("provider", sa.String(), nullable=True))
    op.add_column("signup_requests", sa.Column("provider_subject", sa.String(), nullable=True))
    op.add_column("signup_requests", sa.Column("review_reason", sa.Text(), nullable=True))

    op.create_index("ix_signup_requests_signup_method", "signup_requests", ["signup_method"], unique=False)
    op.create_index("ix_signup_requests_provider", "signup_requests", ["provider"], unique=False)
    op.create_index("ix_signup_requests_provider_subject", "signup_requests", ["provider_subject"], unique=False)

    op.create_table(
        "admin_auth_identities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("admin_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("provider_subject", sa.String(), nullable=False),
        sa.Column("provider_email", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["admin_id"], ["admins.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider", "provider_subject", name="uq_admin_auth_identities_provider_subject"),
    )
    op.create_index("ix_admin_auth_identities_admin_id", "admin_auth_identities", ["admin_id"], unique=False)
    op.create_index("ix_admin_auth_identities_provider", "admin_auth_identities", ["provider"], unique=False)
    op.create_index("ix_admin_auth_identities_provider_subject", "admin_auth_identities", ["provider_subject"], unique=False)
    op.create_index("ix_admin_auth_identities_provider_email", "admin_auth_identities", ["provider_email"], unique=False)
    op.create_index(
        "idx_admin_auth_identities_admin_provider",
        "admin_auth_identities",
        ["admin_id", "provider"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_admin_auth_identities_admin_provider", table_name="admin_auth_identities")
    op.drop_index("ix_admin_auth_identities_provider_email", table_name="admin_auth_identities")
    op.drop_index("ix_admin_auth_identities_provider_subject", table_name="admin_auth_identities")
    op.drop_index("ix_admin_auth_identities_provider", table_name="admin_auth_identities")
    op.drop_index("ix_admin_auth_identities_admin_id", table_name="admin_auth_identities")
    op.drop_table("admin_auth_identities")

    op.drop_index("ix_signup_requests_provider_subject", table_name="signup_requests")
    op.drop_index("ix_signup_requests_provider", table_name="signup_requests")
    op.drop_index("ix_signup_requests_signup_method", table_name="signup_requests")
    op.drop_column("signup_requests", "review_reason")
    op.drop_column("signup_requests", "provider_subject")
    op.drop_column("signup_requests", "provider")
    op.drop_column("signup_requests", "signup_method")
