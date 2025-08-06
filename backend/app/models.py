# models.py
from sqlalchemy import Column, Integer, String, Boolean , ForeignKey, UniqueConstraint, Index
from app.database import Base
from sqlalchemy import Date , DateTime
from datetime import date 
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



# class Admin(Base):
#     __tablename__ = "admins"

#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, unique=True, index=True, nullable=False)
#     password = Column(String, nullable=False)
    
    
class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="admin",index=True)  # admin / superadmin
    library_id = Column(Integer, ForeignKey("libraries.id", ondelete="CASCADE"),index=True, nullable=True)
    status = Column(String, default="active",index=True)  # 'active', 'inactive', 'blocked'

    created_at = Column(Date, default=date.today)

    library = relationship("Library", back_populates="admins")

    
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

    
class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    library_id = Column(Integer, ForeignKey("libraries.id", ondelete="CASCADE"), nullable=False, unique=True)
    status = Column(String, default="inactive")   # "active", "inactive", etc.
    valid_until = Column(DateTime)
    plan = Column(String)                         # e.g., 'per_seat_monthly'
    payment_gateway_id = Column(String)           # Razorpay sub ID, etc.

    last_payment_at = Column(DateTime)            # NEW: tracks last payment timestamp
    is_trial = Column(Boolean, default=False)     # NEW: is user on trial
    trial_valid_until = Column(DateTime)          # NEW: trial end timestamp

    library = relationship("Library", back_populates="subscription")

    __table_args__ = (
        Index("idx_subscriptions_library_status", "library_id", "status"),
    )