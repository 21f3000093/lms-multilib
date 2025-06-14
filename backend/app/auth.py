# backend/app/auth.py

from fastapi import APIRouter, Depends, HTTPException 
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from . import schemas, crud
from app.dependencies import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=schemas.AdminOut)
def login(
    data: schemas.AdminLogin,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    admin = crud.authenticate_admin(db, data.username, data.password)
    if not admin:
        raise HTTPException(status_code=401, detail="invalid_credentials")

    if admin.status != "active": # type: ignore
        raise HTTPException(status_code=403, detail="Your account is inactive or blocked")

    access_token = Authorize.create_access_token(subject=admin.username) # type: ignore
    Authorize.set_access_cookies(access_token)
    
    # ✅ Eagerly load the related library for response
    db.refresh(admin)  # This ensures `admin.library` is populated

    return admin



@router.post("/logout")
def logout( Authorize: AuthJWT = Depends()):
    Authorize.unset_jwt_cookies()
    return {"msg": "Logged out"}

@router.get("/whoami", response_model=schemas.AdminOut)
def whoami(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()
    admin = crud.get_admin_by_username(db, username) # type: ignore
    if not admin or admin.status != "active": # type: ignore
        raise HTTPException(status_code=403, detail="Unauthorized")
    return admin