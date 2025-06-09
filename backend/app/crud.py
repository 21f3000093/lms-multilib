# crud.py
from sqlalchemy.orm import Session
from app import models, schemas
# from fastapi import HTTPException
from sqlalchemy import func
from datetime import date , datetime
from app.models import Student ,MonthlyPayment
import csv
from io import StringIO
from fastapi.responses import StreamingResponse

import os 
from dotenv import load_dotenv
load_dotenv()

SHIFT_PRICE = 500
MAX_SEATS = os.getenv("MAX_SEATS", 100)

# crud.py

# def get_available_seats(db: Session, shift1: bool, shift2: bool, shift3: bool):
#     seats = db.query(models.Seat).all()
#     available = []
#     for seat in seats:
#         if (
#             (not shift1 or seat.shift1_student_id is None) and
#             (not shift2 or seat.shift2_student_id is None) and
#             (not shift3 or seat.shift3_student_id is None)
#         ):
#             available.append(seat.id)
#     return available


def get_available_seats(db: Session, shift1: bool, shift2: bool, shift3: bool, student_id: int | None = None):
    seats = db.query(models.Seat).all()
    available = []

    # Get current seat if student_id is provided
    current_student = db.query(models.Student).filter_by(id=student_id).first() if student_id else None
    current_seat_id = current_student.seat_id if current_student else None

    for seat in seats:
        shift1_ok = not shift1 or seat.shift1_student_id is None or seat.shift1_student_id == student_id
        shift2_ok = not shift2 or seat.shift2_student_id is None or seat.shift2_student_id == student_id
        shift3_ok = not shift3 or seat.shift3_student_id is None or seat.shift3_student_id == student_id

        if shift1_ok and shift2_ok and shift3_ok: # type: ignore
            available.append(seat.id)

    return available



def create_student(db: Session, student: schemas.StudentCreate):
    # Fetch the selected seat
    seat = db.query(models.Seat).filter(models.Seat.id == student.seat_id).first()
    if not seat:
        raise Exception("Selected seat does not exist.")

    # Check availability of that seat for selected shifts
    if student.shift1 and seat.shift1_student_id is not None:
        raise Exception("Selected seat is already booked in Shift 1.")
    if student.shift2 and seat.shift2_student_id is not None:
        raise Exception("Selected seat is already booked in Shift 2.")
    if student.shift3 and seat.shift3_student_id is not None:
        raise Exception("Selected seat is already booked in Shift 3.")

    # Calculate fee
    if student.custom_fees is not None:
        total_fee = student.custom_fees
    else:
        total_shifts = sum([student.shift1, student.shift2, student.shift3])
        total_fee = total_shifts * SHIFT_PRICE

    # Save student
    db_student = models.Student(
        name=student.name,
        contact=student.contact,
        shift1=student.shift1,
        shift2=student.shift2,
        shift3=student.shift3,
        paid=student.paid,
        custom_fees=student.custom_fees,
        total_fee=total_fee,
        seat_id=student.seat_id,  # link seat
        date_of_joining=student.date_of_joining or date.today()
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)

    # Update seat assignment
    if student.shift1:
        seat.shift1_student_id = db_student.id
    if student.shift2:
        seat.shift2_student_id = db_student.id
    if student.shift3:
        seat.shift3_student_id = db_student.id
    db.commit()

    return db_student


def get_students(db: Session):
    # return db.query(Student).all() 
    return db.query(Student).filter(Student.status == "active").all()

def get_student(db: Session, student_id: int):
    return db.query(models.Student).filter(models.Student.id == student_id).first()


def update_student(db: Session, student_id: int, updated_data: schemas.StudentCreate):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        return None

    for field, value in updated_data.dict().items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)
    
        # Update seats table
    seat = db.query(models.Seat).filter(models.Seat.id == student.seat_id).first()
    if seat:
        # Clear old entries for this student
        for s in db.query(models.Seat).all():
            if s.shift1_student_id == student.id: # type: ignore
                s.shift1_student_id = None # type: ignore
            if s.shift2_student_id == student.id: # type: ignore
                s.shift2_student_id = None # type: ignore
            if s.shift3_student_id == student.id: # type: ignore
                s.shift3_student_id = None # type: ignore

        # Set new values based on shifts
        if student.shift1: # type: ignore
            seat.shift1_student_id = student.id 
        if student.shift2: # type: ignore
            seat.shift2_student_id = student.id 
        if student.shift3: # type: ignore
            seat.shift3_student_id = student.id
            
        db.commit()
    else:
        raise Exception("Selected seat does not exist.")    

    
    return student


def mark_student_as_left(db: Session, student_id: int):
    student = db.query(models.Student).filter_by(id=student_id).first()
    if not student:
        return None

    # Mark status as 'left'
    student.status = "left" # type: ignore
    student.seat_id = None # type: ignore
    
    # Clear seat assignments in all 3 shifts
    seats = db.query(models.Seat).filter(
        (models.Seat.shift1_student_id == student.id) |
        (models.Seat.shift2_student_id == student.id) |
        (models.Seat.shift3_student_id == student.id)
    ).all()

    for seat in seats:
        nullable=True
        if seat.shift1_student_id == student.id: # type: ignore
            seat.shift1_student_id = None   # type: ignore
        if seat.shift2_student_id == student.id: # type: ignore
            seat.shift2_student_id = None  # type: ignore
        if seat.shift3_student_id == student.id: # type: ignore
            seat.shift3_student_id = None  # type: ignore

    db.commit()
    return student

def get_dashboard_data(db: Session):
    shift1_count = db.query(models.Student).filter(
        models.Student.shift1 == True,
        models.Student.status == "active"
    ).count()

    shift2_count = db.query(models.Student).filter(
        models.Student.shift2 == True,
        models.Student.status == "active"
    ).count()

    shift3_count = db.query(models.Student).filter(
        models.Student.shift3 == True,
        models.Student.status == "active"
    ).count()

    total_students = db.query(models.Student).filter(
        models.Student.status == "active"
    ).count()

    revenue = db.query(func.coalesce(func.sum(models.Student.custom_fees), 0)).filter(
        # models.Student.paid == True,
        models.Student.status == "active"
    ).scalar()
    
    # 👉 Add this: get current month in format 'YYYY-MM'
    current_month = datetime.now().strftime('%Y-%m')

    # 👉 Sum of amounts from paid monthly payments for this month
    monthly_collected = db.query(func.coalesce(func.sum(MonthlyPayment.amount), 0)).filter(
        MonthlyPayment.month == current_month,
        MonthlyPayment.paid == True
    ).scalar()

    return {
        "shift1_count": shift1_count,
        "shift2_count": shift2_count,
        "shift3_count": shift3_count,
        "total_students": total_students,
        "revenue": revenue,
        "monthly_collected": monthly_collected
    }
    
def create_monthly_payments_for_all(db: Session, month: str):
    students = db.query(models.Student).filter(models.Student.status == "active").all()
    for student in students:
        # Check if payment record already exists for this student and month
        exists = db.query(models.MonthlyPayment).filter_by(
            student_id=student.id, month=month
        ).first()
        if not exists:
            db.add(models.MonthlyPayment(student_id=student.id, month=month, paid=False , amount=student.custom_fees))
    db.commit()

def mark_monthly_payment_as_paid(db: Session, payment_id: int):
    payment = db.query(models.MonthlyPayment).get(payment_id)
    if payment:
        payment.paid = True
        db.commit()
        db.refresh(payment)
    return payment

def get_monthly_payments(db: Session, month: str):
    return db.query(models.MonthlyPayment).filter_by(month=month).all()

def toggle_monthly_payment_status(db: Session, payment_id: int):
    payment = db.query(models.MonthlyPayment).get(payment_id)
    if payment:
        payment.paid = not payment.paid
        db.commit()
        db.refresh(payment)
    return payment


def delete_monthly_payment(db: Session, payment_id: int):
    payment = db.query(models.MonthlyPayment).get(payment_id)
    if payment:
        db.delete(payment)
        db.commit()
    return payment

def get_student_payments(db: Session, student_id: int):
    return db.query(models.MonthlyPayment).filter(models.MonthlyPayment.student_id == student_id).all()



def export_monthly_payments_csv(db: Session, month: str):
    payments = db.query(models.MonthlyPayment).filter_by(month=month).all()

    stream = StringIO()
    writer = csv.writer(stream)
    writer.writerow(["Student Name", "Contact","Seat No","Month", "Amount", "Paid"])

    for payment in payments:
        writer.writerow([
            payment.student.name,
            payment.student.contact,
            payment.student.seat_id,
            payment.month,
            payment.amount,
            "Paid" if payment.paid else "Unpaid" # type: ignore
        ])

    stream.seek(0)
    return StreamingResponse(
        stream,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=monthly_payments_{month}.csv"}
    )

from .models import Admin
from sqlalchemy.orm import Session
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_admin_by_username(db: Session, username: str):
    return db.query(Admin).filter(Admin.username == username).first()

def authenticate_admin(db: Session, username: str, password: str):
    admin = get_admin_by_username(db, username)
    if not admin or not verify_password(password, admin.password):
        return None
    return admin

def get_admin(db: Session, admin_id: int):
    return db.query(Admin).filter(Admin.id == admin_id).first()

def create_admin(db: Session, username: str, password: str):
    new_admin = models.Admin(username=username, password=password)
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin
