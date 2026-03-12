# backend/app/superadmin.py

from datetime import datetime, time, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from app import models, schemas
from app.dependencies import (
    ensure_subscription_for_library,
    get_current_admin,
    get_db,
    get_subscription_trial_days,
)
from fastapi_jwt_auth import AuthJWT
from typing import List
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")




superadmin_router = APIRouter(prefix="/superadmin", tags=["superadmin"])


def _require_superadmin(admin: models.Admin) -> None:
    if admin.role != "superadmin":
        raise HTTPException(status_code=403, detail="Only superadmin can access this")


# routes for superadmin to manage libraries 
@superadmin_router.get("/libraries", response_model=list[schemas.LibraryOut])
def get_libraries(db: Session = Depends(get_db),admin = Depends(get_current_admin)):
    _require_superadmin(admin)
    return db.query(models.Library).all()

@superadmin_router.post("/libraries", response_model=schemas.LibraryOut)
def create_library(library: schemas.LibraryCreate, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    _require_superadmin(admin)
    if library.max_seats < 1 or library.max_seats > 200:
        raise HTTPException(status_code=400, detail="max_seats must be between 1 and 200")
    
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
    _require_superadmin(admin)
    return db.query(models.Admin).filter_by(role="admin").all()

@superadmin_router.post("/admins", response_model=schemas.AdminOut)
def create_admin(admin_data: schemas.AdminCreate, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    _require_superadmin(admin)

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
    _require_superadmin(admin)

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
    _require_superadmin(admin)
    library = db.query(models.Library).filter_by(id=library_id).first()
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")
    return library

@superadmin_router.delete("/admins/{admin_id}")
def delete_admin(admin_id: int, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    _require_superadmin(admin)

    target = db.query(models.Admin).filter_by(id=admin_id, role="admin").first()
    if not target:
        raise HTTPException(status_code=404, detail="Admin not found")

    db.delete(target)
    db.commit()
    return {"message": f"Admin with ID {admin_id} has been deleted successfully."}

@superadmin_router.get("/libraries/{library_id}/students", response_model=List[schemas.StudentOut])
def get_students_by_library(library_id: int, db: Session = Depends(get_db), admin = Depends(get_current_admin)):
    _require_superadmin(admin)
    
    students = db.query(models.Student).filter(models.Student.library_id == library_id).all()
    return students


@superadmin_router.get("/subscriptions", response_model=List[schemas.SuperadminSubscriptionRowOut])
def list_subscriptions(
    status: str | None = Query(default=None),
    library_id: int | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin),
):
    _require_superadmin(admin)

    library_query = db.query(models.Library)
    if library_id is not None:
        library_query = library_query.filter(models.Library.id == library_id)
    libraries = library_query.order_by(models.Library.id.asc()).offset(offset).limit(limit).all()
    if not libraries:
        return []

    normalized_status = status.strip().lower() if status else None
    library_ids = [library.id for library in libraries]
    subscriptions = (
        db.query(models.Subscription)
        .options(joinedload(models.Subscription.plan_config))
        .filter(models.Subscription.library_id.in_(library_ids))
        .all()
    )
    subscription_map = {subscription.library_id: subscription for subscription in subscriptions}

    rows: list[dict] = []
    for library in libraries:
        subscription = subscription_map.get(library.id)
        if normalized_status:
            subscription_status = (subscription.status if subscription else "not_configured") # type: ignore
            if subscription_status != normalized_status:
                continue
        rows.append(
            {
                "library": library,
                "subscription": subscription,
            }
        )

    return rows


@superadmin_router.post(
    "/subscriptions/{library_id}/grant-trial",
    response_model=schemas.SubscriptionGrantTrialOut,
)
def grant_subscription_trial(
    library_id: int,
    payload: schemas.SubscriptionGrantTrialRequest,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin),
):
    _require_superadmin(admin)

    library = db.query(models.Library).filter(models.Library.id == library_id).first()
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")

    trial_days = payload.days or get_subscription_trial_days()
    trial_valid_until = datetime.combine(
        datetime.utcnow().date() + timedelta(days=trial_days),
        time(23, 59, 59),
    )

    subscription = ensure_subscription_for_library(db, library_id)
    subscription.status = "trialing" # type: ignore
    subscription.is_trial = True # type: ignore
    subscription.trial_valid_until = trial_valid_until # type: ignore
    subscription.grace_until = None # type: ignore

    db.commit()
    db.refresh(subscription)

    subscription = (
        db.query(models.Subscription)
        .options(joinedload(models.Subscription.plan_config))
        .filter(models.Subscription.id == subscription.id)
        .first()
    )
    if not subscription:
        raise HTTPException(status_code=500, detail="Failed to load updated subscription")

    return {
        "message": f"Trial granted for {trial_days} day(s)",
        "subscription": subscription,
    }
