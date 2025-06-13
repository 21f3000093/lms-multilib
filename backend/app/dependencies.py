# app/dependencies.py
from app.database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends
from fastapi_jwt_auth import AuthJWT
from fastapi import HTTPException
from app import crud

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_admin(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()
    admin = crud.get_admin_by_username(db, username) # type: ignore
    if not admin or admin.status != "active": # type: ignore
        raise HTTPException(status_code=403, detail="Unauthorized")
    return admin