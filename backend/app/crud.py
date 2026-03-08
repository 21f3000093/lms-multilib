# crud.py
from sqlalchemy.orm import Session , joinedload 
from app import models, schemas
# from fastapi import HTTPException
from sqlalchemy import func 
from datetime import date , datetime, timedelta
from app.models import Student ,MonthlyPayment 
import csv
from io import StringIO
from fastapi.responses import StreamingResponse
import time
import calendar





##### ======================================================================================================
###                                 Student Registration CRUD OPERATIONS
##### ======================================================================================================


def get_available_seats(db: Session, shift1: bool, shift2: bool, shift3: bool, library_id: int, student_id: int | None = None):
    seats = db.query(models.Seat).filter_by(library_id=library_id).order_by(models.Seat.seat_number).all()
    available = []

   

    for seat in seats:
        shift1_ok = not shift1 or seat.shift1_student_id is None or seat.shift1_student_id == student_id
        shift2_ok = not shift2 or seat.shift2_student_id is None or seat.shift2_student_id == student_id
        shift3_ok = not shift3 or seat.shift3_student_id is None or seat.shift3_student_id == student_id

        if shift1_ok and shift2_ok and shift3_ok: # type: ignore
            available.append({
                "id": seat.id,
                "seat_number": seat.seat_number
            })

    return available



def create_student(db: Session, student: schemas.StudentCreate):
    # Fetch the selected seat
    seat = db.query(models.Seat).filter(models.Seat.id == student.seat_id).first()
    if not seat:
        raise Exception("Selected seat does not exist.")

    if seat.library_id != student.library_id: # type: ignore
        raise Exception("Seat does not belong to the specified library.")

    # Check availability of that seat for selected shifts
    if student.shift1 and seat.shift1_student_id is not None:
        raise Exception("Selected seat is already booked in Shift 1.")
    if student.shift2 and seat.shift2_student_id is not None:
        raise Exception("Selected seat is already booked in Shift 2.")
    if student.shift3 and seat.shift3_student_id is not None:
        raise Exception("Selected seat is already booked in Shift 3.")

    # Calculate fee
    # if student.custom_fees is not None:
    #     total_fee = student.custom_fees
    # else:
    #     total_shifts = sum([student.shift1, student.shift2, student.shift3])
    #     total_fee = total_shifts * SHIFT_PRICE

    # Save student
    db_student = models.Student(
        name=student.name,
        contact=student.contact,
        shift1=student.shift1,
        shift2=student.shift2,
        shift3=student.shift3,
        # paid=student.paid,
        custom_fees=student.custom_fees,
        # total_fee=total_fee,
        seat_id=student.seat_id,  # link seat
        date_of_joining=student.date_of_joining or date.today(),
        library_id=student.library_id
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


##### ======================================================================================================
###                                              Students List Page CRUD
##### ======================================================================================================


# To get all active students of a library
def get_students(db: Session, library_id: int):
    
    """
    Basic optimization - leverages existing composite index
    """
    start_time = time.time()
    
    # Use the composite index idx_students_library_status more effectively
    result = (db.query(Student)
              .filter(Student.library_id == library_id, Student.status == "active")
              .order_by(Student.seat_id.nulls_last())  # Handle NULL seat_ids properly
              .all())
    
    end_time = time.time()
    print(f"Basic optimized query time: {end_time - start_time} seconds, returned {len(result)} students")
    return result

    
    


# To get a single student
def get_student(db: Session, student_id: int, library_id: int):
    return (
        db.query(models.Student)
        .filter(
            models.Student.id == student_id,
            models.Student.library_id == library_id
        )
        .first()
    )

# To update a student
def update_student(db: Session, student_id: int, updated_data: schemas.StudentCreate, library_id: int):
    student = (
        db.query(models.Student)
        .filter(
            models.Student.id == student_id,
            models.Student.library_id == library_id
        )
        .first()
    )
    if not student:
        return None

    # Resolve target seat and shifts before mutating DB state.
    target_seat_id = updated_data.seat_id
    target_shift1 = updated_data.shift1
    target_shift2 = updated_data.shift2
    target_shift3 = updated_data.shift3

    target_seat = None
    if target_seat_id is not None:
        target_seat = (
            db.query(models.Seat)
            .filter(
                models.Seat.id == target_seat_id,
                models.Seat.library_id == library_id
            )
            .first()
        )
        if not target_seat:
            raise ValueError("Selected seat does not exist.")

        # Prevent overwriting another student's shift slot on update.
        if target_shift1 and target_seat.shift1_student_id not in (None, student.id):
            raise ValueError("Selected seat is already booked in Shift 1.")
        if target_shift2 and target_seat.shift2_student_id not in (None, student.id):
            raise ValueError("Selected seat is already booked in Shift 2.")
        if target_shift3 and target_seat.shift3_student_id not in (None, student.id):
            raise ValueError("Selected seat is already booked in Shift 3.")

    # Clear previous seat assignment references for this student first.
    for s in (
        db.query(models.Seat)
        .filter(models.Seat.library_id == library_id)
        .filter(
            (models.Seat.shift1_student_id == student.id) |
            (models.Seat.shift2_student_id == student.id) |
            (models.Seat.shift3_student_id == student.id)
        )
        .all()
    ):
        if s.shift1_student_id == student.id: # type: ignore
            s.shift1_student_id = None # type: ignore
        if s.shift2_student_id == student.id: # type: ignore
            s.shift2_student_id = None # type: ignore
        if s.shift3_student_id == student.id: # type: ignore
            s.shift3_student_id = None # type: ignore

    # Never trust client-provided tenant ID.
    for field, value in updated_data.dict(exclude={"library_id"}).items():
        setattr(student, field, value)
    student.library_id = library_id # type: ignore

    # Apply new seat assignment only after conflict checks pass.
    if target_seat is not None:
        if student.shift1: # type: ignore
            target_seat.shift1_student_id = student.id
        if student.shift2: # type: ignore
            target_seat.shift2_student_id = student.id
        if student.shift3: # type: ignore
            target_seat.shift3_student_id = student.id

    db.commit()
    db.refresh(student)
    
    return student

# To mark a student as left
def mark_student_as_left(db: Session, student_id: int, library_id: int):
    student = (
        db.query(models.Student)
        .filter(
            models.Student.id == student_id,
            models.Student.library_id == library_id
        )
        .first()
    )
    if not student:
        return None

    # Mark status as 'left'
    student.status = "left" # type: ignore
    if not student.left_at:
        student.left_at = datetime.now(ZoneInfo("Asia/Kolkata")) # type: ignore
    student.seat_id = None # type: ignore
    
    # Clear seat assignments in all 3 shifts
    seats = (
        db.query(models.Seat)
        .filter(models.Seat.library_id == library_id)
        .filter(
            (models.Seat.shift1_student_id == student.id) |
            (models.Seat.shift2_student_id == student.id) |
            (models.Seat.shift3_student_id == student.id)
        )
        .all()
    )

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


##### ======================================================================================================
###                                            DASHBOARD DATA                                                    
##### ======================================================================================================

from zoneinfo import ZoneInfo

# To get dashboard data for a library
def get_dashboard_data(db: Session, library_id: int):
    shift1_count = db.query(models.Student).filter(models.Student.shift1 == True, models.Student.status == "active", models.Student.library_id == library_id).count()
    shift2_count = db.query(models.Student).filter(models.Student.shift2 == True, models.Student.status == "active", models.Student.library_id == library_id).count()
    shift3_count = db.query(models.Student).filter(models.Student.shift3 == True, models.Student.status == "active", models.Student.library_id == library_id).count()
    total_students = db.query(models.Student).filter(models.Student.status == "active", models.Student.library_id == library_id).count()


    revenue = db.query(func.coalesce(func.sum(models.Student.custom_fees), 0)).filter(models.Student.status == "active", models.Student.library_id == library_id).scalar()

    # current_month = datetime.now().strftime('%Y-%m')
    
    # Use Indian timezone (Asia/Kolkata)
    india_tz = ZoneInfo("Asia/Kolkata")
    current_month = datetime.now(india_tz).strftime('%Y-%m')

    monthly_collected = db.query(func.coalesce(func.sum(MonthlyPayment.amount), 0)).filter(
        MonthlyPayment.month == current_month,
        MonthlyPayment.paid == True,
        MonthlyPayment.library_id == library_id
    ).scalar()
    
    max_seats = db.query(models.Library).filter(models.Library.id == library_id).first().max_seats # type: ignore
    
    return {
        "shift1_count": shift1_count,
        "shift2_count": shift2_count,
        "shift3_count": shift3_count,
        "total_students": total_students,
        "revenue": revenue,
        "monthly_collected": monthly_collected,
        "max_seats": max_seats
    }
    




##### ======================================================================================================
###                             MONTHLY FEE PAYMENTS
##### ======================================================================================================


def _get_due_date_for_month(year: int, month_num: int, joining_date: date | None) -> date:
    due_day = joining_date.day if joining_date else 1
    last_day = calendar.monthrange(year, month_num)[1]
    return date(year, month_num, min(due_day, last_day))


def _get_billing_period_and_next_due(month: str, joining_date: date | None) -> tuple[date, date, date]:
    year, month_num = map(int, month.split('-'))
    current_due_date = _get_due_date_for_month(year, month_num, joining_date)

    if month_num == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month_num + 1

    next_due_date = _get_due_date_for_month(next_year, next_month, joining_date)
    period_start = current_due_date
    period_end = next_due_date - timedelta(days=1)
    return period_start, period_end, next_due_date


def create_monthly_payments_for_all(db: Session, month: str, library_id: int):
    # Parse 'YYYY-MM' → year, month
    year, month_num = map(int, month.split('-'))
    last_day = calendar.monthrange(year, month_num)[1]
    end_of_month = date(year, month_num, last_day)
    students = db.query(models.Student).filter(
        models.Student.status == "active",
        models.Student.library_id == library_id,
        models.Student.date_of_joining <= end_of_month,  # <-- Only joined on or before month
    ).all()

    for student in students:
        exists = db.query(models.MonthlyPayment).filter_by(student_id=student.id, month=month).first()
        if not exists:
            period_start, period_end, next_due_date = _get_billing_period_and_next_due(
                month,
                student.date_of_joining
            )
            db.add(models.MonthlyPayment(
                student_id=student.id,
                month=month,
                paid=False,
                amount=student.custom_fees,
                library_id=library_id,
                paid_at=None,
                period_start=period_start,
                period_end=period_end,
                next_due_date=next_due_date
            ))
    db.commit()






    
# To mark a monthly payment as paid
def mark_monthly_payment_as_paid(db: Session, payment_id: int, library_id: int):
    payment = (
        db.query(models.MonthlyPayment)
        .filter(
            models.MonthlyPayment.id == payment_id,
            models.MonthlyPayment.library_id == library_id
        )
        .first()
    )
    if payment:
        if not payment.paid: # type: ignore
            payment.paid = True  # type: ignore
            payment.paid_at = datetime.now(ZoneInfo("Asia/Kolkata")) # type: ignore
        elif not payment.paid_at:
            payment.paid_at = datetime.now(ZoneInfo("Asia/Kolkata")) # type: ignore
        db.commit()
        db.refresh(payment)
    return payment

    

# def get_monthly_payments(db: Session, month: str, library_id: int):
#     """
#     Optimized query leveraging existing indexes:
#     - Uses idx_payments_library_month for fast filtering
#     - Uses idx_seats_library_number for efficient seat ordering
#     - Prevents N+1 queries with eager loading
#     """
#     start_time = time.time()
#     results = (
#         db.query(models.MonthlyPayment)
#         .join(models.MonthlyPayment.student)
#         .join(models.Student.seat, isouter=True)  # LEFT JOIN for students without seats
#         .options(
#             joinedload(models.MonthlyPayment.student)
#             .joinedload(models.Student.seat)  # Eager load to prevent N+1 queries
#         )
#         .filter(
#             models.MonthlyPayment.library_id == library_id,
#             models.MonthlyPayment.month == month
#         )
#         .order_by(
#             models.Seat.seat_number.asc().nulls_last(),  # Uses idx_seats_library_number
#             models.Student.id.asc()  # Secondary sort for consistent ordering
#         )
#         .all()
#     )
#     end_time = time.time()
#     print(f"Query time: {end_time - start_time} seconds")
#     return results

# ''' Optimized query to get monthly payments with only required fields '''
def get_monthly_payments(db: Session, month: str, library_id: int):
    """
    Optimized query that selects only required fields
    This reduces memory usage and transfer time significantly
    """
    start_time = time.time()
    
    results = (
        db.query(
            models.MonthlyPayment.id,
            models.MonthlyPayment.amount,
            models.MonthlyPayment.paid,
            models.MonthlyPayment.paid_at,
            models.MonthlyPayment.period_start,
            models.MonthlyPayment.period_end,
            models.MonthlyPayment.next_due_date,
            models.Student.name.label('student_name'),
            models.Student.date_of_joining,
            models.Student.contact,
            models.Seat.seat_number,
            models.Student.id.label('student_id')
        )
        .join(models.MonthlyPayment.student)  # INNER JOIN to students
        .join(models.Student.seat, isouter=True)  # LEFT JOIN to seats
        .filter(
            models.MonthlyPayment.library_id == library_id,
            models.MonthlyPayment.month == month
        )
        .order_by(
            models.Seat.seat_number.asc().nulls_last(),  # Uses your idx_seats_library_number
            models.Student.id.asc()
        )
        .all()
    )
    
    end_time = time.time()
    print(f"Query time: {end_time - start_time} seconds, returned {len(results)} records")
    
    # Transform to your desired JSON structure
    transformed_results = []
    for row in results:
        payment_data = {
            "id": row.id,
            "amount": row.amount,
            "paid": row.paid,
            "paid_at": row.paid_at.isoformat() if row.paid_at else None,
            "period_start": row.period_start.isoformat() if row.period_start else None,
            "period_end": row.period_end.isoformat() if row.period_end else None,
            "next_due_date": row.next_due_date.isoformat() if row.next_due_date else None,
            "student": {
                "name": row.student_name,
                "id": row.student_id,
                "contact": row.contact if row.contact else None,
                "date_of_joining": row.date_of_joining.isoformat() if row.date_of_joining else None,
                "seat": {
                    "seat_number": row.seat_number
                } if row.seat_number is not None else None
            }
        }
        transformed_results.append(payment_data)
    
    return transformed_results

# To toggle the status of a monthly payment between paid and not paid
def toggle_monthly_payment_status(db: Session, payment_id: int, library_id: int):
    payment = (
        db.query(models.MonthlyPayment)
        .filter(
            models.MonthlyPayment.id == payment_id,
            models.MonthlyPayment.library_id == library_id
        )
        .first()
    )
    if payment:
        payment.paid = not payment.paid # type: ignore
        payment.paid_at = datetime.now(ZoneInfo("Asia/Kolkata")) if payment.paid else None # type: ignore
        db.commit()
        db.refresh(payment)
    return payment

# To delete a monthly payment record
def delete_monthly_payment(db: Session, payment_id: int, library_id: int):
    payment = (
        db.query(models.MonthlyPayment)
        .filter(
            models.MonthlyPayment.id == payment_id,
            models.MonthlyPayment.library_id == library_id
        )
        .first()
    )
    if payment:
        db.delete(payment)
        db.commit()
    return payment

# To get payments for a specific student 
def get_student_payments(db: Session, student_id: int, library_id: int):
    return (
        db.query(models.MonthlyPayment)
        .join(models.Student, models.MonthlyPayment.student_id == models.Student.id)
        .filter(
            models.MonthlyPayment.student_id == student_id,
            models.MonthlyPayment.library_id == library_id,
            models.Student.library_id == library_id
        )
        .order_by(models.MonthlyPayment.month.desc())
        .all()
    )


# To export monthly payments to CSV 
def export_monthly_payments_csv(db: Session, month: str, library_id: int):
    payments = db.query(models.MonthlyPayment).filter_by(month=month, library_id=library_id).order_by(models.MonthlyPayment.student_id).all()

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

##### ======================================================================================================
###         INITIALIZE DATABASE WITH DEFAULT ADMIN ACCOUNT 
##### ======================================================================================================


from .models import Admin
from sqlalchemy.orm import Session
from passlib.context import CryptContext
# Password hasher
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

# To create an admin 
def create_admin(db: Session, username: str, password: str, role: str = "admin", library_id: int = None): # type: ignore
    new_admin = models.Admin(username=username, password=password, role=role, library_id=library_id)
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin


# To create a library 
def init_library(db: Session , name: str, address: str, contact_email: str, contact_phone: str, max_seats: int): # type: ignore
    new_library = models.Library(name=name, address=address, contact_email=contact_email, contact_phone=contact_phone, max_seats=max_seats)
    db.add(new_library)
    db.flush()
    
    for seat_number in range(1, max_seats + 1):
        seat = models.Seat(seat_number=seat_number, library_id=new_library.id)
        db.add(seat)
        
    db.commit()
    db.refresh(new_library)
    
    return new_library



##### ======================================================================================================
###         Change password function
##### ======================================================================================================

def change_admin_password(db: Session, admin_id: int, current_password: str, new_password: str):
    """
    Change admin password after verifying current password
    """
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        return None
    
    # Verify current password
    if not verify_password(current_password, admin.password):
        return False
    
    # Hash new password
    hashed_new_password = pwd_context.hash(new_password)
    
    # Update password
    admin.password = hashed_new_password # type: ignore
    db.commit()
    db.refresh(admin)
    
    return admin

##### ======================================================================================================
###         Monthly expense functions
##### ======================================================================================================


def add_monthly_expense(db: Session, library_id: int, expense: schemas.MonthlyExpenseCreate):
    month = expense.date.strftime('%Y-%m')
    db_expense = models.MonthlyExpense(
        library_id=library_id,
        month=month,
        name=expense.name,
        date=expense.date,
        amount=expense.amount,
        description=expense.description,
        category=expense.category,
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def get_expenses_for_month(db: Session, library_id: int, month: str):
    return (
        db.query(models.MonthlyExpense)
        .filter(models.MonthlyExpense.library_id == library_id,
                models.MonthlyExpense.month == month)
        .order_by(models.MonthlyExpense.date.desc())
        .all()
    )

def get_monthly_expenses(db: Session, library_id: int):
    return (
        db.query(models.MonthlyExpense)
        .filter(models.MonthlyExpense.library_id == library_id)
        .order_by(models.MonthlyExpense.date.desc())
        .all()
    )
    
def delete_monthly_expense(db: Session, expense_id: int, library_id: int):
    expense = db.query(models.MonthlyExpense).filter(
        models.MonthlyExpense.id == expense_id,
        models.MonthlyExpense.library_id == library_id
    ).first()
    if not expense:
        return False
    db.delete(expense)
    db.commit()
    return True
