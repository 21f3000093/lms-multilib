# models.py
from sqlalchemy import Column, Integer, String, Boolean , ForeignKey, UniqueConstraint
from app.database import Base
from sqlalchemy import Date
from datetime import date
from sqlalchemy.orm import relationship


class Library(Base):
    __tablename__ = "libraries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)
    created_at = Column(Date, default=date.today)
    max_seats = Column(Integer, nullable=False)

    admins = relationship("Admin", back_populates="library")
    students = relationship("Student", back_populates="library")
    seats = relationship("Seat", back_populates="library")
    monthly_payments = relationship("MonthlyPayment", back_populates="library")


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
    role = Column(String, default="admin")  # admin / superadmin
    library_id = Column(Integer, ForeignKey("libraries.id"), nullable=True)
    status = Column(String, default="active")  # 'active', 'inactive', 'blocked'

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
    contact = Column(String)
    seat_id = Column(Integer, ForeignKey("seats.id"), nullable=True)
    shift1 = Column(Boolean, default=False)
    shift2 = Column(Boolean, default=False)
    shift3 = Column(Boolean, default=False)
    total_fee = Column(Integer)
    paid = Column(Boolean, default=False)
    custom_fees = Column(Integer, nullable=True)
    date_of_joining = Column(Date, default=date.today)
    status = Column(String, default="active")

    library_id = Column(Integer, ForeignKey("libraries.id"), nullable=False)
    library = relationship("Library", back_populates="students")
    monthly_payments = relationship("MonthlyPayment", back_populates="student")
    seat = relationship("Seat", backref="student", uselist=False)

    
    
class MonthlyPayment(Base):
    __tablename__ = 'monthly_payments'
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    month = Column(String, index=True)  # format: '2025-07'
    amount = Column(Integer)
    paid = Column(Boolean, default=False)

    student = relationship("Student", back_populates="monthly_payments")
    library_id = Column(Integer, ForeignKey("libraries.id"), nullable=False)
    library = relationship("Library", back_populates="monthly_payments")


    
# class Seat(Base):
#     __tablename__ = "seats"
#     id = Column(Integer, primary_key=True, index=True)  # Seat number from 1 to 100
#     shift1_student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
#     shift2_student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
#     shift3_student_id = Column(Integer, ForeignKey("students.id"), nullable=True)

class Seat(Base):
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)
    shift1_student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    shift2_student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    shift3_student_id = Column(Integer, ForeignKey("students.id"), nullable=True)

    seat_number = Column(Integer, nullable=False)  # 1 to max_seats (unique per library)
    library_id = Column(Integer, ForeignKey("libraries.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint('library_id', 'seat_number', name='uq_library_seat_number'),
)
    library = relationship("Library", back_populates="seats")

    