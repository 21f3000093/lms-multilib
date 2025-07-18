from fastapi import HTTPException
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, crud , auth , seats , superadmin , whatsapp_reminder   
from fastapi_jwt_auth import AuthJWT
from app.database import engine, SessionLocal
from pydantic import BaseSettings , BaseModel
from passlib.context import CryptContext

# ✅ Dependency to get current admin and database
from app.dependencies import get_db , get_current_admin


import os
from dotenv import load_dotenv

load_dotenv()


models.Base.metadata.create_all(bind=engine)





class Settings(BaseModel):
    authjwt_secret_key: str = os.getenv("JWT_SECRET_KEY") # type: ignore
    authjwt_token_location: set = {"cookies"}  # <- Important!
    authjwt_cookie_csrf_protect: bool = False  # Optional
    authjwt_access_token_expires: int = 60 * 60 * 8  # 1 hours
    authjwt_cookie_max_age: int = 60 * 60 * 24
    authjwt_cookie_samesite: str = "none"
    authjwt_cookie_secure: bool = True
    # authjwt_cookie_samesite: str = "lax"   # ✅ allow cross-origin GETs
    # authjwt_cookie_domain: str = "localhost"  # ✅ important for matching frontend
    

@AuthJWT.load_config # type:ignore
def get_config():
    return Settings()



app = FastAPI()

app.include_router(auth.router)
app.include_router(seats.router)
app.include_router(superadmin.superadmin_router)
app.include_router(whatsapp_reminder.router)

origins=os.getenv("ALLOWED_ORIGINS") # type: ignore

# CORS config
app.add_middleware(
    CORSMiddleware,
    # allow_origins=[origins],  # Change to frontend URL in production # type: ignore
    # allow_origins=["http://localhost:8080"],  # Change to frontend URL in production
    allow_origins=["http://localhost:8080","https://lms-virid-three.vercel.app","https://www.smartlibraryapp.in"],  # Change to frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




# Password hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.on_event("startup")
def startup_create_admin():
    db: Session = SessionLocal()
    
    # crud.init_library(db, name="Library", address="Address", contact_email="email", contact_phone="9090909090", max_seats=20)
        
    superadmin_username = os.getenv("SUPERADMIN_USERNAME")
    superadmin_password = os.getenv("SUPERADMIN_PASSWORD")
    
    if not superadmin_username or not superadmin_password:
        raise ValueError("SUPERADMIN_USERNAME and SUPERADMIN_PASSWORD must be set in .env")

    existing_admin = crud.get_admin_by_username(db, superadmin_username) # type: ignore
    if not existing_admin:
        print("Creating default admin user...")
        crud.init_library(db, name="SuperAdmin Library", address="Address", contact_email="shubhamnagar68819@gmail.com", contact_phone="9024600138", max_seats=10)
    
        hashed_password1 = pwd_context.hash(superadmin_password) # type: ignore
        hashed_password2 = pwd_context.hash("password") # type: ignore
        crud.create_admin(db, username=superadmin_username, password=hashed_password1, role="superadmin") # type: ignore
        crud.create_admin(db, username="shubham", password=hashed_password2, role="admin", library_id=1) # type: ignore
    db.close()



@app.post("/students/", response_model=schemas.StudentOut)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    student.library_id = admin.library_id
    return crud.create_student(db, student)


@app.get("/students/", response_model=List[schemas.StudentOut])
def get_students(db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    return crud.get_students(db, library_id=admin.library_id)

@app.get("/students/{student_id}", response_model=schemas.StudentOut)
def get_student_by_id(student_id: int, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@app.get("/dashboard/")
def dashboard(db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    return crud.get_dashboard_data(db, library_id=admin.library_id)


@app.get("/available-seats")
def available_seats(
    shift1: bool = False,
    shift2: bool = False,
    shift3: bool = False,
    student_id: int | None = None,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    return crud.get_available_seats(db, shift1, shift2, shift3, library_id=admin.library_id, student_id=student_id)


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



@app.put("/students/{student_id}", response_model=schemas.StudentOut)
def update_student(student_id: int, updated_data: schemas.StudentCreate, db: Session = Depends(get_db)):
    student = crud.update_student(db, student_id, updated_data)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student




@app.post("/generate-monthly-payments/{month}")
def generate_monthly(month: str, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    crud.create_monthly_payments_for_all(db, month, library_id=admin.library_id)
    return {"message": f"Monthly records created for {month}"}


@app.get("/monthly-payments/{month}", response_model=List[schemas.MonthlyPaymentOut])
def get_payments(month: str, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    return crud.get_monthly_payments(db, month, library_id=admin.library_id)

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
def export_csv(month: str, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    return crud.export_monthly_payments_csv(db, month, library_id=admin.library_id)