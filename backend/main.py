from fastapi import HTTPException
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, crud , auth , seats
from fastapi_jwt_auth import AuthJWT
from app.database import engine, SessionLocal
from pydantic import BaseSettings , BaseModel
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()


models.Base.metadata.create_all(bind=engine)

# ✅ Insert 100 seats only if not already present

max_seats = 100
def preload_seats():
    db = SessionLocal()
    existing = db.query(models.Seat).count()
    if existing == 0:
        for i in range(1, max_seats + 1):
            seat = models.Seat(id=i)
            db.add(seat)
        db.commit()
    db.close()

preload_seats()  # ✅ Call this once at app start

# class Settings(BaseSettings): # type:ignore
#     authjwt_secret_key: str = "your-secret-key"

class Settings(BaseModel):
    authjwt_secret_key: str = os.getenv("JWT_SECRET_KEY") # type: ignore
    authjwt_token_location: set = {"cookies"}  # <- Important!
    authjwt_cookie_csrf_protect: bool = False  # Optional

@AuthJWT.load_config # type:ignore
def get_config():
    return Settings()



app = FastAPI()

app.include_router(auth.router)
app.include_router(seats.router)


# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080","https://library-management-system-lac-nine.vercel.app"],  # Change to frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

from app.dependencies import get_db


# Password hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.on_event("startup")
def startup_create_admin():
    db: Session = SessionLocal()
    admin_username = os.getenv("ADMIN_USERNAME")
    admin_password = os.getenv("ADMIN_PASSWORD")

    existing_admin = crud.get_admin_by_username(db, admin_username) # type: ignore
    if not existing_admin:
        print("Creating default admin user...")
        hashed_password = pwd_context.hash(admin_password) # type: ignore
        crud.create_admin(db, username=admin_username, password=hashed_password) # type: ignore
    db.close()

@app.post("/students/", response_model=schemas.StudentOut)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    return crud.create_student(db, student)

@app.get("/students/", response_model=list[schemas.StudentOut])
def get_students(db: Session = Depends(get_db)):
    return crud.get_students(db)

@app.get("/dashboard/")
def dashboard(db: Session = Depends(get_db)):
    return crud.get_dashboard_data(db)


# @app.get("/available-seats")
# def available_seats(shift1: bool = False, shift2: bool = False, shift3: bool = False, db: Session = Depends(get_db)):
#     return crud.get_available_seats(db, shift1, shift2, shift3)
@app.get("/available-seats")
def available_seats(
    shift1: bool = False,
    shift2: bool = False,
    shift3: bool = False,
    student_id: int | None = None,
    db: Session = Depends(get_db)
):
    return crud.get_available_seats(db, shift1, shift2, shift3, student_id)


@app.put("/students/{student_id}/mark-left")
def mark_left(student_id: int, db: Session = Depends(get_db)):
    student = crud.mark_student_as_left(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": f"Student {student.name} marked as left."}



@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    db.delete(student)
    db.commit()
    return {"detail": "Deleted"}

# @app.put("/students/{student_id}", response_model=schemas.StudentOut)
# def update_student(student_id: int, updated_data: schemas.StudentCreate, db: Session = Depends(get_db)):
#     student = db.query(models.Student).filter(models.Student.id == student_id).first()
#     if not student:
#         raise HTTPException(status_code=404, detail="Student not found")

#     for field, value in updated_data.dict().items():
#         setattr(student, field, value)
#     db.commit()
#     db.refresh(student)
#     return student

@app.put("/students/{student_id}", response_model=schemas.StudentOut)
def update_student(student_id: int, updated_data: schemas.StudentCreate, db: Session = Depends(get_db)):
    student = crud.update_student(db, student_id, updated_data)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student




@app.post("/generate-monthly-payments/{month}")
def generate_monthly(month: str, db: Session = Depends(get_db)):
    """ Call this on 1st of every month: e.g., /generate-monthly-payments/2025-07 """
    crud.create_monthly_payments_for_all(db, month)
    return {"message": f"Monthly records created for {month}"}


@app.get("/monthly-payments/{month}", response_model=List[schemas.MonthlyPaymentOut])
def get_payments(month: str, db: Session = Depends(get_db)):
    return crud.get_monthly_payments(db, month)

@app.put("/monthly-payments/{payment_id}", response_model=schemas.MonthlyPaymentOut)
def mark_paid(payment_id: int, db: Session = Depends(get_db)):
    updated = crud.mark_monthly_payment_as_paid(db, payment_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Payment record not found")
    return updated

@app.put("/monthly-payments/toggle/{payment_id}", response_model=schemas.MonthlyPaymentOut)
def toggle_paid(payment_id: int, db: Session = Depends(get_db)):
    updated = crud.toggle_monthly_payment_status(db, payment_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Payment not found")
    return updated


@app.delete("/monthly-payments/{payment_id}")
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_monthly_payment(db, payment_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"message": "Deleted successfully"}



@app.get("/students/{student_id}/payments", response_model=List[schemas.MonthlyPaymentOut])
def get_student_payments(student_id: int, db: Session = Depends(get_db)):
    return crud.get_student_payments(db, student_id)


@app.get("/export-monthly-payments/{month}")
def export_csv(month: str, db: Session = Depends(get_db)):
    return crud.export_monthly_payments_csv(db, month)