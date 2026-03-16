# models.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, Index, Text
from app.database import Base
from sqlalchemy import Date , DateTime
from datetime import date, datetime
from sqlalchemy.orm import relationship


class Library(Base):
    __tablename__ = "libraries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False,index=True)
    address = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)
    created_at = Column(Date, default=date.today)
    max_seats = Column(Integer, nullable=False)

    admins = relationship("Admin", back_populates="library")
    students = relationship("Student", back_populates="library")
    seats = relationship("Seat", back_populates="library")
    monthly_payments = relationship("MonthlyPayment", back_populates="library")
    subscription = relationship("Subscription", uselist=False, back_populates="library")
    subscription_transactions = relationship("SubscriptionTransaction", back_populates="library")
    notifications = relationship("Notification", back_populates="target_library")



# class Admin(Base):
#     __tablename__ = "admins"

#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, unique=True, index=True, nullable=False)
#     password = Column(String, nullable=False)
    
    
class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    password = Column(String, nullable=False)
    role = Column(String, default="admin",index=True)  # admin / superadmin
    library_id = Column(Integer, ForeignKey("libraries.id", ondelete="CASCADE"),index=True, nullable=True)
    status = Column(String, default="active",index=True)  # 'active', 'inactive', 'blocked'

    created_at = Column(Date, default=date.today)

    library = relationship("Library", back_populates="admins")
    sent_notifications = relationship(
        "Notification",
        foreign_keys="Notification.sender_admin_id",
        back_populates="sender",
    )
    notification_recipients = relationship(
        "NotificationRecipient",
        back_populates="admin",
        cascade="all, delete-orphan",
    )
    push_subscriptions = relationship(
        "PushSubscription",
        back_populates="admin",
        cascade="all, delete-orphan",
    )

    
# class Student(Base):
#     __tablename__ = "students"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String)
#     contact = Column(String)
#     seat_id = Column(Integer, ForeignKey("seats.id"),nullable=True)
#     shift1 = Column(Boolean, default=False)
#     shift2 = Column(Boolean, default=False)
#     shift3 = Column(Boolean, default=False)
#     total_fee = Column(Integer)
#     paid = Column(Boolean, default=False)
#     custom_fees = Column(Integer, nullable=True)
#     date_of_joining = Column(Date, default=date.today)
#     status = Column(String, default="active")  # values: active, left
    
#     monthly_payments = relationship("MonthlyPayment", back_populates="student")

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    contact = Column(String,index=True)
    seat_id = Column(Integer, ForeignKey("seats.id" ,use_alter=True, ondelete="SET NULL"), nullable=True,index=True)
    shift1 = Column(Boolean, default=False)
    shift2 = Column(Boolean, default=False)
    shift3 = Column(Boolean, default=False)
    total_fee = Column(Integer)
    paid = Column(Boolean, default=False)
    custom_fees = Column(Integer, nullable=True)
    date_of_joining = Column(Date, default=date.today,index=True)
    status = Column(String, default="active",index=True)
    left_at = Column(DateTime, nullable=True, index=True)

    library_id = Column(Integer, ForeignKey("libraries.id", ondelete="CASCADE"), nullable=False,index=True)
    library = relationship("Library", back_populates="students")
    monthly_payments = relationship("MonthlyPayment", back_populates="student")
    seat = relationship("Seat", foreign_keys=[seat_id],post_update=True,  uselist=False)
    
    __table_args__ = (
        Index("idx_students_library_status", "library_id", "status"),
    )

    
    
class MonthlyPayment(Base):
    __tablename__ = 'monthly_payments'
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False,index=True)
    month = Column(String, index=True)  # format: '2025-07'
    amount = Column(Integer)
    paid = Column(Boolean, default=False,index=True)
    paid_at = Column(DateTime, nullable=True)
    period_start = Column(Date, nullable=True)
    period_end = Column(Date, nullable=True)
    next_due_date = Column(Date, nullable=True, index=True)

    student = relationship("Student", back_populates="monthly_payments")
    library_id = Column(Integer, ForeignKey("libraries.id", ondelete="CASCADE"), nullable=False,index=True)
    library = relationship("Library", back_populates="monthly_payments")
    
    __table_args__ = (
        Index("idx_payments_student_month", "student_id", "month"),
        Index("idx_payments_library_month", "library_id", "month"),
        Index("idx_payments_library_paid", "library_id", "paid"),
    )


    
# class Seat(Base):
#     __tablename__ = "seats"
#     id = Column(Integer, primary_key=True, index=True)  # Seat number from 1 to 100
#     shift1_student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
#     shift2_student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
#     shift3_student_id = Column(Integer, ForeignKey("students.id"), nullable=True)

class Seat(Base):
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)
    shift1_student_id = Column(Integer, ForeignKey("students.id", ondelete="SET NULL"), nullable=True,index=True)
    shift2_student_id = Column(Integer, ForeignKey("students.id", ondelete="SET NULL"), nullable=True,index=True)
    shift3_student_id = Column(Integer, ForeignKey("students.id", ondelete="SET NULL"), nullable=True,index=True)

    seat_number = Column(Integer, nullable=False, index=True)  # 1 to max_seats (unique per library)
    library_id = Column(Integer, ForeignKey("libraries.id", ondelete="CASCADE"), nullable=False,index=True)

    __table_args__ = (
        UniqueConstraint('library_id', 'seat_number', name='uq_library_seat_number'),
        Index("idx_seats_library_number", "library_id", "seat_number"),
)
    library = relationship("Library", back_populates="seats")


class MonthlyExpense(Base):
    __tablename__ = 'monthly_expenses'

    id = Column(Integer, primary_key=True, index=True)
    library_id = Column(Integer, ForeignKey("libraries.id", ondelete="CASCADE"), nullable=False, index=True)
    month = Column(String, index=True)  # Format: '2025-08'
    name = Column(String, nullable=False)  # Expense name (e.g., 'Electricity Bill')
    amount = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    description = Column(String)
    category = Column(String, nullable=True)  # E.g., 'Utilities', 'Maintenance'
    created_at = Column(Date, default=lambda: date.today(), nullable=False)

    library = relationship("Library", backref="monthly_expenses")


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    billing_months = Column(Integer, nullable=False)
    price_per_seat_paise = Column(Integer, nullable=False)
    discount_percent = Column(Integer, default=0, nullable=False)
    bonus_months = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    subscriptions = relationship("Subscription", back_populates="plan_config")
    transactions = relationship("SubscriptionTransaction", back_populates="plan")


class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    library_id = Column(Integer, ForeignKey("libraries.id", ondelete="CASCADE"), nullable=False, unique=True)
    status = Column(String, default="inactive")   # "active", "inactive", etc.
    valid_until = Column(DateTime)
    plan = Column(String)                         # e.g., 'per_seat_monthly'
    plan_id = Column(Integer, ForeignKey("subscription_plans.id", ondelete="SET NULL"), nullable=True)
    current_period_start = Column(Date, nullable=True)
    current_period_end = Column(Date, nullable=True)
    grace_until = Column(DateTime, nullable=True)
    auto_renew = Column(Boolean, default=False, nullable=False)
    cancel_at_period_end = Column(Boolean, default=False, nullable=False)
    payment_gateway_id = Column(String)           # Razorpay sub ID, etc.
    gateway_customer_id = Column(String, nullable=True)
    gateway_subscription_id = Column(String, nullable=True)

    last_payment_at = Column(DateTime)            # NEW: tracks last payment timestamp
    is_trial = Column(Boolean, default=False)     # NEW: is user on trial
    trial_valid_until = Column(DateTime)          # NEW: trial end timestamp
    bonus_eligible = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    library = relationship("Library", back_populates="subscription")
    plan_config = relationship("SubscriptionPlan", back_populates="subscriptions")
    transactions = relationship("SubscriptionTransaction", back_populates="subscription")

    __table_args__ = (
        Index("idx_subscriptions_library_status", "library_id", "status"),
        Index("idx_subscriptions_status_valid_until", "status", "valid_until"),
        Index("idx_subscriptions_grace_until", "grace_until"),
        Index("idx_subscriptions_plan_id", "plan_id"),
    )


class SubscriptionTransaction(Base):
    __tablename__ = "subscription_transactions"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True, index=True)
    library_id = Column(Integer, ForeignKey("libraries.id", ondelete="CASCADE"), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id", ondelete="SET NULL"), nullable=True, index=True)
    amount_paise = Column(Integer, nullable=False)
    currency = Column(String, nullable=False, default="INR")
    seats_billed = Column(Integer, nullable=False)
    billing_months = Column(Integer, nullable=False)
    status = Column(String, nullable=False, default="created", index=True)  # created|captured|failed|refunded
    gateway_order_id = Column(String, nullable=True, index=True)
    gateway_payment_id = Column(String, nullable=True, index=True)
    gateway_signature = Column(String, nullable=True)
    idempotency_key = Column(String, nullable=False, unique=True, index=True)
    period_start = Column(Date, nullable=True)
    period_end = Column(Date, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    gateway_payload_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    subscription = relationship("Subscription", back_populates="transactions")
    library = relationship("Library", back_populates="subscription_transactions")
    plan = relationship("SubscriptionPlan", back_populates="transactions")

    __table_args__ = (
        Index("idx_subscription_transactions_library_created", "library_id", "created_at"),
        Index("idx_subscription_transactions_subscription_created", "subscription_id", "created_at"),
        Index("idx_subscription_transactions_status_created", "status", "created_at"),
    )


class SubscriptionWebhookEvent(Base):
    __tablename__ = "subscription_webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    gateway_event_id = Column(String, nullable=False, unique=True, index=True)
    event_type = Column(String, nullable=False, index=True)
    payload_json = Column(Text, nullable=False)
    processed = Column(Boolean, default=False, nullable=False, index=True)
    processed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String, default="general", nullable=False, index=True)
    sender_admin_id = Column(Integer, ForeignKey("admins.id", ondelete="SET NULL"), nullable=True, index=True)
    target_type = Column(String, default="all_admins", nullable=False, index=True)
    target_library_id = Column(Integer, ForeignKey("libraries.id", ondelete="SET NULL"), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=True)

    sender = relationship("Admin", foreign_keys=[sender_admin_id], back_populates="sent_notifications")
    target_library = relationship("Library", back_populates="notifications")
    recipients = relationship(
        "NotificationRecipient",
        back_populates="notification",
        cascade="all, delete-orphan",
    )


class NotificationRecipient(Base):
    __tablename__ = "notification_recipients"

    id = Column(Integer, primary_key=True, index=True)
    notification_id = Column(
        Integer,
        ForeignKey("notifications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    admin_id = Column(Integer, ForeignKey("admins.id", ondelete="CASCADE"), nullable=False, index=True)
    is_read = Column(Boolean, default=False, nullable=False, index=True)
    read_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    notification = relationship("Notification", back_populates="recipients")
    admin = relationship("Admin", back_populates="notification_recipients")

    __table_args__ = (
        UniqueConstraint("notification_id", "admin_id", name="uq_notification_recipient"),
        Index("idx_notification_recipient_admin_unread_created", "admin_id", "is_read", "created_at"),
    )


class PushSubscription(Base):
    __tablename__ = "push_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admins.id", ondelete="CASCADE"), nullable=False, index=True)
    endpoint = Column(String, nullable=False, unique=True, index=True)
    p256dh = Column(String, nullable=False)
    auth = Column(String, nullable=False)
    expiration_time = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    admin = relationship("Admin", back_populates="push_subscriptions")

    __table_args__ = (
        Index("idx_push_subscriptions_admin_last_seen", "admin_id", "last_seen_at"),
    )
