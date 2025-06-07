# models.py
from sqlalchemy import Column, Integer, String, Boolean , ForeignKey
from app.database import Base
from sqlalchemy import Date
from datetime import date
from sqlalchemy.orm import relationship


class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    
class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    contact = Column(String)
    seat_id = Column(Integer, ForeignKey("seats.id"),nullable=True)
    shift1 = Column(Boolean, default=False)
    shift2 = Column(Boolean, default=False)
    shift3 = Column(Boolean, default=False)
    total_fee = Column(Integer)
    paid = Column(Boolean, default=False)
    custom_fees = Column(Integer, nullable=True)
    date_of_joining = Column(Date, default=date.today)
    status = Column(String, default="active")  # values: active, left
    
    monthly_payments = relationship("MonthlyPayment", back_populates="student")

    
    
class MonthlyPayment(Base):
    __tablename__ = 'monthly_payments'
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    month = Column(String, index=True)  # format: '2025-07'
    amount = Column(Integer)
    paid = Column(Boolean, default=False)

    student = relationship("Student", back_populates="monthly_payments")


    
class Seat(Base):
    __tablename__ = "seats"
    id = Column(Integer, primary_key=True, index=True)  # Seat number from 1 to 100
    shift1_student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    shift2_student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    shift3_student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
