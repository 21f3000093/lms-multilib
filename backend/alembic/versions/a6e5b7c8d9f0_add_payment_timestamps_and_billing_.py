"""add payment timestamps and billing period fields

Revision ID: a6e5b7c8d9f0
Revises: 9c2d8f5e1b77
Create Date: 2026-03-07 18:45:00.000000

"""
from typing import Sequence, Union
from datetime import date, timedelta
import calendar

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a6e5b7c8d9f0"
down_revision: Union[str, Sequence[str], None] = "9c2d8f5e1b77"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _compute_billing_window(month_value: str, joining_date: date | None) -> tuple[date, date, date] | None:
    try:
        year, month_num = map(int, month_value.split("-"))
    except Exception:
        return None

    if month_num < 1 or month_num > 12:
        return None

    due_day = joining_date.day if joining_date else 1
    current_last_day = calendar.monthrange(year, month_num)[1]
    current_due_date = date(year, month_num, min(due_day, current_last_day))

    if month_num == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month_num + 1

    next_last_day = calendar.monthrange(next_year, next_month)[1]
    next_due_date = date(next_year, next_month, min(due_day, next_last_day))

    period_start = current_due_date
    period_end = next_due_date - timedelta(days=1)
    return period_start, period_end, next_due_date


def upgrade() -> None:
    op.add_column("monthly_payments", sa.Column("paid_at", sa.DateTime(), nullable=True))
    op.add_column("monthly_payments", sa.Column("period_start", sa.Date(), nullable=True))
    op.add_column("monthly_payments", sa.Column("period_end", sa.Date(), nullable=True))
    op.add_column("monthly_payments", sa.Column("next_due_date", sa.Date(), nullable=True))
    op.create_index(op.f("ix_monthly_payments_next_due_date"), "monthly_payments", ["next_due_date"], unique=False)

    connection = op.get_bind()
    payments = sa.table(
        "monthly_payments",
        sa.column("id", sa.Integer),
        sa.column("student_id", sa.Integer),
        sa.column("month", sa.String),
        sa.column("period_start", sa.Date),
        sa.column("period_end", sa.Date),
        sa.column("next_due_date", sa.Date),
    )
    students = sa.table(
        "students",
        sa.column("id", sa.Integer),
        sa.column("date_of_joining", sa.Date),
    )

    rows = connection.execute(
        sa.select(payments.c.id, payments.c.month, students.c.date_of_joining)
        .select_from(payments.join(students, payments.c.student_id == students.c.id))
    ).fetchall()

    for row in rows:
        if not row.month:
            continue
        period_values = _compute_billing_window(row.month, row.date_of_joining)
        if not period_values:
            continue
        period_start, period_end, next_due_date = period_values
        connection.execute(
            payments.update()
            .where(payments.c.id == row.id)
            .values(
                period_start=period_start,
                period_end=period_end,
                next_due_date=next_due_date,
            )
        )


def downgrade() -> None:
    op.drop_index(op.f("ix_monthly_payments_next_due_date"), table_name="monthly_payments")
    op.drop_column("monthly_payments", "next_due_date")
    op.drop_column("monthly_payments", "period_end")
    op.drop_column("monthly_payments", "period_start")
    op.drop_column("monthly_payments", "paid_at")
