from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session
from . import schemas, crud
from app.dependencies import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=schemas.AdminOut)
def login(data: schemas.AdminLogin, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    admin = crud.authenticate_admin(db, data.username, data.password)
    if not admin:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = Authorize.create_access_token(subject=admin.username) # type: ignore
    Authorize.set_access_cookies(access_token)
    return admin

@router.post("/logout")
def logout(Authorize: AuthJWT = Depends()):
    Authorize.unset_jwt_cookies()
    return {"msg": "Logged out"}
