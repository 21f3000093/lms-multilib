# backend/app/auth.py

from fastapi import APIRouter, Depends, HTTPException 
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from . import schemas, crud
from app.dependencies import get_db, get_current_admin

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=schemas.AdminLoginOut)
def login(
    data: schemas.AdminLogin,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    admin = crud.authenticate_admin(db, data.username, data.password)
    if not admin:
        raise HTTPException(status_code=401, detail="invalid_credentials")

    if admin.status != "active": # type: ignore
        raise HTTPException(status_code=403, detail="Your account is inactive")

    access_token = Authorize.create_access_token(subject=admin.username) # type: ignore
    Authorize.set_access_cookies(access_token)
    
    # ✅ Eagerly load the related library for response
    db.refresh(admin)  # This ensures `admin.library` is populated

    csrf_token = Authorize.get_csrf_token(access_token)
    return {
        "id": admin.id,
        "username": admin.username,
        "role": admin.role,
        "library_id": admin.library_id,
        "status": admin.status,
        "created_at": admin.created_at,
        "library": admin.library,
        "csrf_token": csrf_token,
    }



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

