"""seed subscription plans

Revision ID: b5c8d2e7f1a4
Revises: a92f4b6d1e73
Create Date: 2026-03-12 00:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b5c8d2e7f1a4"
down_revision: Union[str, Sequence[str], None] = "a92f4b6d1e73"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PLANS = [
    {
        "code": "monthly",
        "name": "Monthly Pack",
        "description": "Ideal for testing and flexible monthly billing.",
        "billing_months": 1,
        "price_per_seat_paise": 900,
        "discount_percent": 0,
        "bonus_months": 1,
        "is_active": True,
        "sort_order": 10,
    },
    {
        "code": "quarterly",
        "name": "3-Month Pack",
        "description": "Quarterly billing with immediate savings.",
        "billing_months": 3,
        "price_per_seat_paise": 855,
        "discount_percent": 5,
        "bonus_months": 1,
        "is_active": True,
        "sort_order": 20,
    },
    {
        "code": "half_yearly",
        "name": "6-Month Pack",
        "description": "Balanced pricing for growing libraries.",
        "billing_months": 6,
        "price_per_seat_paise": 810,
        "discount_percent": 10,
        "bonus_months": 1,
        "is_active": True,
        "sort_order": 30,
    },
    {
        "code": "yearly",
        "name": "12-Month Pack",
        "description": "Best annual value with stronger savings.",
        "billing_months": 12,
        "price_per_seat_paise": 765,
        "discount_percent": 15,
        "bonus_months": 2,
        "is_active": True,
        "sort_order": 40,
    },
    {
        "code": "two_year",
        "name": "24-Month Pack",
        "description": "Lowest per-seat rate for long-term operators.",
        "billing_months": 24,
        "price_per_seat_paise": 720,
        "discount_percent": 20,
        "bonus_months": 4,
        "is_active": True,
        "sort_order": 50,
    },
]


def upgrade() -> None:
    bind = op.get_bind()
    for plan in PLANS:
        bind.execute(
            sa.text(
                """
                INSERT INTO subscription_plans
                (code, name, description, billing_months, price_per_seat_paise, discount_percent, bonus_months, is_active, sort_order)
                VALUES
                (:code, :name, :description, :billing_months, :price_per_seat_paise, :discount_percent, :bonus_months, :is_active, :sort_order)
                ON CONFLICT (code) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    billing_months = EXCLUDED.billing_months,
                    price_per_seat_paise = EXCLUDED.price_per_seat_paise,
                    discount_percent = EXCLUDED.discount_percent,
                    bonus_months = EXCLUDED.bonus_months,
                    is_active = EXCLUDED.is_active,
                    sort_order = EXCLUDED.sort_order,
                    updated_at = now()
                """
            ),
            plan,
        )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            DELETE FROM subscription_plans
            WHERE code IN ('monthly', 'quarterly', 'half_yearly', 'yearly', 'two_year')
            """
        )
    )
