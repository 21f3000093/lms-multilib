# backend/app/auth.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app import crud, models, schemas
from app.dependencies import (
    build_admin_jwt_subject,
    get_current_admin,
    get_db,
    get_subscription_trial_days,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


def _get_login_identifier(data: schemas.AdminLogin) -> str:
    return (data.identifier or data.username or "").strip()


def _load_admin_with_library(db: Session, admin_id: int):
    return (
        db.query(models.Admin)
        .options(joinedload(models.Admin.library))
        .filter(models.Admin.id == admin_id)
        .first()
    )


@router.post("/login", response_model=schemas.AdminOut)
def login(
    data: schemas.AdminLogin,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    identifier = _get_login_identifier(data)
    if not identifier:
        raise HTTPException(status_code=400, detail="username_or_email_required")

    admin = crud.authenticate_admin(db, identifier, data.password)
    if not admin:
        raise HTTPException(status_code=401, detail="invalid_credentials")

    if admin.status != "active": # type: ignore
        raise HTTPException(status_code=403, detail="Your account is inactive")

    access_token = Authorize.create_access_token(subject=build_admin_jwt_subject(admin.id)) # type: ignore
    Authorize.set_access_cookies(access_token)

    loaded_admin = _load_admin_with_library(db, admin.id)
    if not loaded_admin:
        raise HTTPException(status_code=500, detail="Admin could not be loaded")
    return loaded_admin


@router.post("/signup", response_model=schemas.AdminOut)
def signup(
    data: schemas.SelfServeSignupRequest,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    admin_username = data.admin_username.strip()
    admin_email = data.admin_email.strip().lower()
    contact_phone = data.contact_phone.strip()
    library_name = data.library_name.strip()
    address = data.address.strip() if isinstance(data.address, str) else None

    if not library_name:
        raise HTTPException(status_code=400, detail="Library name is required")
    if not admin_username:
        raise HTTPException(status_code=400, detail="Username is required")
    if not admin_email:
        raise HTTPException(status_code=400, detail="Email is required")
    if not contact_phone:
        raise HTTPException(status_code=400, detail="Contact phone is required")
    if data.password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    if len(data.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")

    if crud.get_admin_by_username(db, admin_username):
        raise HTTPException(status_code=409, detail="Username already exists")
    if crud.get_admin_by_email(db, admin_email):
        raise HTTPException(status_code=409, detail="Email already exists")

    try:
        _, admin = crud.provision_library_owner_signup(
            db,
            library_name=library_name,
            max_seats=data.max_seats,
            contact_phone=contact_phone,
            address=address,
            admin_username=admin_username,
            admin_email=admin_email,
            password=data.password,
            trial_days=get_subscription_trial_days(),
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Username or email already exists")
    except Exception:
        db.rollback()
        raise

    admin = _load_admin_with_library(db, admin.id)
    if not admin:
        raise HTTPException(status_code=500, detail="Signup completed but admin could not be loaded")

    access_token = Authorize.create_access_token(subject=build_admin_jwt_subject(admin.id))
    Authorize.set_access_cookies(access_token)
    return admin



@router.post("/logout")
def logout( Authorize: AuthJWT = Depends()):
    Authorize.unset_jwt_cookies()
    return {"msg": "Logged out"}



# To change admin password
@router.put("/change-password")
def change_password(
    data: schemas.AdminChangePassword,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin)
):
    # Validate new password confirmation
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="New passwords do not match")
    
    # Check if new password is different from current
    if data.current_password == data.new_password:
        raise HTTPException(status_code=400, detail="New password must be different from current password")
    
    # Validate password strength (optional)
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters long")
    
    # Change password
    result = crud.change_admin_password(db, admin.id, data.current_password, data.new_password)
    
    if result is None:
        raise HTTPException(status_code=404, detail="Admin not found")
    elif result is False:
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    return {"message": "Password changed successfully"}
