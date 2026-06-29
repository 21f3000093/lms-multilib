from fastapi import HTTPException
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, crud, auth, seats, superadmin, whatsapp_reminder, notifications, billing, upload
from app.services.storage import delete_student_photo
from fastapi_jwt_auth import AuthJWT
from app.database import engine, SessionLocal
from pydantic import BaseSettings , BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
import base64
import hashlib
import hmac
import logging
import struct

# ✅ Dependency to get current admin and database
from app.dependencies import get_db, require_active_subscription


import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


# models.Base.metadata.create_all(bind=engine)


def _get_receipt_share_secret() -> str:
    secret = os.getenv("RECEIPT_SHARE_SECRET") or os.getenv("JWT_SECRET_KEY")
    if not secret:
        raise ValueError("JWT_SECRET_KEY must be set for receipt sharing")
    return secret


def _get_receipt_share_expiry_hours() -> int:
    raw_value = os.getenv("RECEIPT_SHARE_EXPIRES_HOURS", "72")
    try:
        return max(1, int(raw_value))
    except ValueError:
        return 72


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _build_receipt_share_token(payment_id: int, library_id: int) -> tuple[str, datetime]:
    """
    Compact token format (shorter than JWT):
    base64url(version+payment_id+library_id+exp).base64url(sig8)
    """
    now_utc = datetime.now(timezone.utc)
    expires_at = now_utc + timedelta(hours=_get_receipt_share_expiry_hours())
    exp_ts = int(expires_at.timestamp())
    data = struct.pack(">BIII", 1, payment_id, library_id, exp_ts)
    signature = hmac.new(
        _get_receipt_share_secret().encode("utf-8"),
        data,
        hashlib.sha256
    ).digest()[:8]
    token = f"{_b64url_encode(data)}.{_b64url_encode(signature)}"
    return token, expires_at


def _decode_receipt_share_token(token: str) -> tuple[int, int]:
    # Backward compatibility for previously issued JWT links.
    if token.count(".") == 2:
        try:
            payload = jwt.decode(token, _get_receipt_share_secret(), algorithms=["HS256"])
        except ExpiredSignatureError:
            raise HTTPException(status_code=410, detail="Receipt link has expired")
        except InvalidTokenError:
            raise HTTPException(status_code=400, detail="Invalid receipt link")

        if payload.get("scope") != "public_receipt":
            raise HTTPException(status_code=400, detail="Invalid receipt scope")

        payment_id = payload.get("payment_id")
        library_id = payload.get("library_id")
        if not isinstance(payment_id, int) or not isinstance(library_id, int):
            raise HTTPException(status_code=400, detail="Invalid receipt payload")
        return payment_id, library_id

    try:
        data_part, sig_part = token.split(".", 1)
        data = _b64url_decode(data_part)
        signature = _b64url_decode(sig_part)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid receipt link")

    if len(data) != 13 or len(signature) != 8:
        raise HTTPException(status_code=400, detail="Invalid receipt payload")

    expected_signature = hmac.new(
        _get_receipt_share_secret().encode("utf-8"),
        data,
        hashlib.sha256
    ).digest()[:8]
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=400, detail="Invalid receipt signature")

    try:
        version, payment_id, library_id, exp_ts = struct.unpack(">BIII", data)
    except struct.error:
        raise HTTPException(status_code=400, detail="Invalid receipt payload")

    if version != 1:
        raise HTTPException(status_code=400, detail="Unsupported receipt token version")

    if datetime.now(timezone.utc).timestamp() > exp_ts:
        raise HTTPException(status_code=410, detail="Receipt link has expired")

    return payment_id, library_id





def _get_cookie_samesite() -> str:
    raw = (os.getenv("AUTHJWT_COOKIE_SAMESITE") or "none").strip().lower()
    return raw if raw in {"none", "lax", "strict"} else "none"


def _get_cookie_domain() -> str | None:
    raw = (os.getenv("AUTHJWT_COOKIE_DOMAIN") or "").strip()
    return raw or None


class Settings(BaseModel):
    authjwt_secret_key: str = os.getenv("JWT_SECRET_KEY") # type: ignore
    authjwt_token_location: set = {"cookies"}  # <- Important!
    authjwt_cookie_csrf_protect: bool = False  # Optional
    authjwt_access_token_expires: int = 60 * 60 * 24 * 7  # 7 days
    authjwt_cookie_max_age: int = 60 * 60 * 24 * 7  # 7 days
    authjwt_cookie_samesite: str = _get_cookie_samesite()
    authjwt_cookie_secure: bool = True
    authjwt_cookie_domain: str | None = _get_cookie_domain()
    

@AuthJWT.load_config # type:ignore
def get_config():
    return Settings()



app = FastAPI()

app.include_router(auth.router)
app.include_router(seats.router)
app.include_router(superadmin.superadmin_router)
app.include_router(whatsapp_reminder.router)
app.include_router(notifications.router)
app.include_router(billing.router)
app.include_router(upload.router)

def _parse_allowed_origins(raw_origins: str | None) -> list[str]:
    if not raw_origins:
        return []
    parsed: list[str] = []
    for origin in raw_origins.split(","):
        cleaned = origin.strip().strip("'").strip('"')
        if cleaned:
            parsed.append(cleaned)
    return parsed


configured_origins = _parse_allowed_origins(os.getenv("ALLOWED_ORIGINS"))
default_origins = [
    # "http://localhost:8080",
    "https://www.smartlibraryapp.in",
    "https://app.smartlibraryapp.in",
    # "https://lms-git-ios-shubham-nagars-projects-0c121e37.vercel.app",
]

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=configured_origins or default_origins,
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
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db), admin = Depends(require_active_subscription)):
    student.library_id = admin.library_id
    return crud.create_student(db, student)


@app.get("/students/", response_model=List[schemas.StudentOut])
def get_students(db: Session = Depends(get_db), admin = Depends(require_active_subscription)):
    return crud.get_students(db, library_id=admin.library_id)

@app.get("/students/{student_id}", response_model=schemas.StudentOut)
def get_student_by_id(
    student_id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_active_subscription)
):
    student = crud.get_student(db, student_id, admin.library_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@app.get("/dashboard/")
def dashboard(
    collection_trend_months: int = Query(4, description="Supported values: 4 or 6"),
    movement_trend_months: int = Query(4, description="Supported values: 4 or 6"),
    db: Session = Depends(get_db),
    admin = Depends(require_active_subscription)
):
    if collection_trend_months not in (4, 6):
        collection_trend_months = 4
    if movement_trend_months not in (4, 6):
        movement_trend_months = 4
    return crud.get_dashboard_data(
        db,
        library_id=admin.library_id,
        collection_trend_months=collection_trend_months,
        movement_trend_months=movement_trend_months,
    )


@app.get("/available-seats")
def available_seats(
    shift1: bool = False,
    shift2: bool = False,
    shift3: bool = False,
    student_id: int | None = None,
    db: Session = Depends(get_db),
    admin = Depends(require_active_subscription)
):
    return crud.get_available_seats(db, shift1, shift2, shift3, library_id=admin.library_id, student_id=student_id)


@app.put("/students/{student_id}/mark-left")
def mark_left(
    student_id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_active_subscription)
):
    student = crud.mark_student_as_left(db, student_id, admin.library_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": f"Student {student.name} marked as left."}



@app.delete("/students/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_active_subscription)
):
    student = (
        db.query(models.Student)
        .filter(
            models.Student.id == student_id,
            models.Student.library_id == admin.library_id
        )
        .first()
    )
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    if student.photo_url:
        try:
            delete_student_photo(student.photo_url)
        except Exception:
            logger.exception("Failed to delete student photo during student deletion")
    db.delete(student)
    db.commit()
    return {"detail": "Deleted"}



@app.put("/students/{student_id}", response_model=schemas.StudentOut)
def update_student(
    student_id: int,
    updated_data: schemas.StudentCreate,
    db: Session = Depends(get_db),
    admin = Depends(require_active_subscription)
):
    # Enforce tenant ownership from authenticated admin, not client payload.
    updated_data.library_id = admin.library_id
    try:
        student = crud.update_student(db, student_id, updated_data, admin.library_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student




@app.post("/generate-monthly-payments/{month}")
def generate_monthly(month: str, db: Session = Depends(get_db), admin = Depends(require_active_subscription)):
    crud.create_monthly_payments_for_all(db, month, library_id=admin.library_id)
    return {"message": f"Monthly records created for {month}"}


@app.get("/monthly-payments/{month}")
def get_payments(month: str, db: Session = Depends(get_db), admin = Depends(require_active_subscription)):
    return crud.get_monthly_payments(db, month, library_id=admin.library_id)

# @app.get("/monthly-payments/{month}", response_model=List[schemas.MonthlyPaymentOut])
# def get_payments(month: str, db: Session = Depends(get_db), admin = Depends(require_active_subscription)):
#     return crud.get_monthly_payments(db, month, library_id=admin.library_id)

@app.put("/monthly-payments/{payment_id}", response_model=schemas.MonthlyPaymentOut)
def mark_paid(
    payment_id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_active_subscription)
):
    updated = crud.mark_monthly_payment_as_paid(db, payment_id, admin.library_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Payment record not found")
    return updated

@app.put("/monthly-payments/toggle/{payment_id}", response_model=schemas.MonthlyPaymentOut)
def toggle_paid(
    payment_id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_active_subscription)
):
    updated = crud.toggle_monthly_payment_status(db, payment_id, admin.library_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Payment not found")
    return updated


@app.delete("/monthly-payments/{payment_id}")
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_active_subscription)
):
    deleted = crud.delete_monthly_payment(db, payment_id, admin.library_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"message": "Deleted successfully"}


@app.get("/monthly-payments/{payment_id}/share-link")
def get_payment_share_link(
    payment_id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_active_subscription)
):
    payment = (
        db.query(models.MonthlyPayment)
        .filter(
            models.MonthlyPayment.id == payment_id,
            models.MonthlyPayment.library_id == admin.library_id
        )
        .first()
    )
    if not payment:
        raise HTTPException(status_code=404, detail="Payment record not found")
    if not payment.paid:
        raise HTTPException(status_code=400, detail="Only paid records can be shared as receipts")

    token, expires_at = _build_receipt_share_token(payment_id=payment.id, library_id=admin.library_id)
    public_base_url = os.getenv("PUBLIC_RECEIPT_BASE_URL", "").strip().rstrip("/")
    share_url = f"{public_base_url}/public-receipts/{token}" if public_base_url else None
    return {"token": token, "share_url": share_url, "expires_at": expires_at.isoformat()}



@app.get("/students/{student_id}/payments", response_model=List[schemas.MonthlyPaymentOut])
def get_student_payments(
    student_id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_active_subscription)
):
    return crud.get_student_payments(db, student_id, admin.library_id)


@app.post("/students/{student_id}/payments/bulk", response_model=schemas.StudentBulkPaymentResult)
def create_student_bulk_payments(
    student_id: int,
    payload: schemas.StudentBulkPaymentCreate,
    db: Session = Depends(get_db),
    admin = Depends(require_active_subscription)
):
    try:
        return crud.create_bulk_student_payments(db, student_id, admin.library_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/export-monthly-payments/{month}")
def export_csv(month: str, db: Session = Depends(get_db), admin = Depends(require_active_subscription)):
    return crud.export_monthly_payments_csv(db, month, library_id=admin.library_id)



# Add new expense
@app.post("/monthly-expenses/", response_model=schemas.MonthlyExpenseOut)
def add_monthly_expense(
    expense: schemas.MonthlyExpenseCreate,
    db: Session = Depends(get_db),
    admin = Depends(require_active_subscription)
):
    return crud.add_monthly_expense(db, admin.library_id, expense)

# Get expenses for current month
@app.get("/monthly-expenses/{month}", response_model=List[schemas.MonthlyExpenseOut])
def get_expenses(month: str, db: Session = Depends(get_db), admin = Depends(require_active_subscription)):
    return crud.get_expenses_for_month(db, admin.library_id, month)



@app.delete("/monthly-expenses/{expense_id}", status_code=204)
def delete_monthly_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    admin = Depends(require_active_subscription)
):
    success = crud.delete_monthly_expense(db, expense_id, admin.library_id)
    if not success:
        raise HTTPException(status_code=404, detail="Expense not found")
    return None  # Or just use `pass`, since 204 = No Content

# Add to main.py or your payments router

@app.get("/monthly-payments/single/{payment_id}", response_model=schemas.MonthlyPaymentOut)
def get_single_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_admin: models.Admin = Depends(require_active_subscription)
):
    payment = db.query(models.MonthlyPayment)\
        .filter(models.MonthlyPayment.id == payment_id)\
        .filter(models.MonthlyPayment.library_id == current_admin.library_id)\
        .first()
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment record not found")
    
    return crud.serialize_monthly_payment(payment)


@app.get("/public-receipts/{token}", response_model=schemas.PublicReceiptOut)
def get_public_receipt(
    token: str,
    db: Session = Depends(get_db)
):
    payment_id, library_id = _decode_receipt_share_token(token)

    payment = (
        db.query(models.MonthlyPayment)
        .filter(
            models.MonthlyPayment.id == payment_id,
            models.MonthlyPayment.library_id == library_id
        )
        .first()
    )
    if not payment:
        raise HTTPException(status_code=404, detail="Payment record not found")
    if not payment.paid:
        raise HTTPException(status_code=403, detail="Receipt unavailable for unpaid record")

    library = (
        db.query(models.Library)
        .filter(models.Library.id == payment.library_id)
        .first()
    )

    return {
        "payment": payment,
        "library_name": library.name if library else None,
        "library_address": library.address if library else None,
        "library_contact": library.contact_phone if library else None,
    }
