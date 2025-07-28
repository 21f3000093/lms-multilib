# backend/app/superadmin.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.dependencies import get_db , get_current_admin
from fastapi_jwt_auth import AuthJWT
from typing import List
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")




superadmin_router = APIRouter(prefix="/superadmin", tags=["superadmin"])


# routes for superadmin to manage libraries 
@superadmin_router.get("/libraries", response_model=list[schemas.LibraryOut])
def get_libraries(db: Session = Depends(get_db),admin = Depends(get_current_admin)):
    if admin.role != "superadmin":
        raise HTTPException(status_code=403, detail="Only superadmin can access this")
    return db.query(models.Library).all()

@superadmin_router.post("/libraries", response_model=schemas.LibraryOut)
def create_library(library: schemas.LibraryCreate, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    if admin.role != "superadmin":
        raise HTTPException(status_code=403, detail="Only superadmin can access this")
    
    new_library = models.Library(
        name=library.name,
        address=library.address,
        contact_email=library.contact_email,
        contact_phone=library.contact_phone,
        max_seats=library.max_seats
        
    )
    db.add(new_library)
    db.commit()
    db.refresh(new_library)

    for seat_number in range(1, library.max_seats + 1):
        seat = models.Seat(seat_number=seat_number, library_id=new_library.id)
        db.add(seat)
    db.commit() 

    return new_library


# routes for superadmin to manage admins
@superadmin_router.get("/admins", response_model=List[schemas.AdminOut])
def list_admins(db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    if admin.role != "superadmin":
        raise HTTPException(status_code=403, detail="Only superadmin can access this")
    return db.query(models.Admin).filter_by(role="admin").all()

@superadmin_router.post("/admins", response_model=schemas.AdminOut)
def create_admin(admin_data: schemas.AdminCreate, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    if admin.role != "superadmin":
        raise HTTPException(status_code=403, detail="Only superadmin can access this")

    existing = db.query(models.Admin).filter_by(username=admin_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Admin username already exists")
    
    hashed_password = pwd_context.hash(admin_data.password) 


    new_admin = models.Admin(
        username=admin_data.username,
        password=hashed_password,  # 🛑 Consider hashing here!
        role="admin",
        library_id=admin_data.library_id
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin

@superadmin_router.patch("/admins/{admin_id}/status")
def update_admin_status(admin_id: int, status: str, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    if admin.role != "superadmin":
        raise HTTPException(status_code=403, detail="Only superadmin can access this")

    target = db.query(models.Admin).filter_by(id=admin_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Admin not found")

    if status not in ["active", "inactive", "blocked"]:
        raise HTTPException(status_code=400, detail="Invalid status value")

    target.status = status # type: ignore
    db.commit()
    return {"message": f"Admin status updated to '{status}'"}

@superadmin_router.get("/libraries/{library_id}", response_model=schemas.LibraryOut)
def get_library(library_id: int, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    if admin.role != "superadmin":
        raise HTTPException(status_code=403, detail="Only superadmin can access this")
    library = db.query(models.Library).filter_by(id=library_id).first()
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    return library

@superadmin_router.delete("/admins/{admin_id}")
def delete_admin(admin_id: int, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    if admin.role != "superadmin":
        raise HTTPException(status_code=403, detail="Only superadmin can access this")

    target = db.query(models.Admin).filter_by(id=admin_id, role="admin").first()
    if not target:
        raise HTTPException(status_code=404, detail="Admin not found")

    db.delete(target)
    db.commit()
    return {"message": f"Admin with ID {admin_id} has been deleted successfully."}

@superadmin_router.get("/libraries/{library_id}/students", response_model=List[schemas.StudentOut])
def get_students_by_library(library_id: int, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    if admin.role != "superadmin":
        raise HTTPException(status_code=403, detail="Only superadmin can access this")
    
    students = db.query(models.Student).filter(models.Student.library_id == library_id).all()
    return students
