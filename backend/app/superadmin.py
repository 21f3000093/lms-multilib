# backend/app/superadmin.py

from datetime import datetime, time, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from app import models, schemas
from app.dependencies import (
    ensure_subscription_for_library,
    get_current_admin,
    get_db,
    get_subscription_grace_days,
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


def _resolve_subscription_plan(
    db: Session,
    plan_id: int | None,
    plan_code: str | None,
) -> models.SubscriptionPlan | None:
    if plan_id is not None and plan_code is not None:
        raise HTTPException(status_code=400, detail="Provide either plan_id or plan_code, not both")

    plan: models.SubscriptionPlan | None = None
    if plan_id is not None:
        plan = db.query(models.SubscriptionPlan).filter(models.SubscriptionPlan.id == plan_id).first()
    elif plan_code:
        normalized_code = plan_code.strip().lower()
        plan = db.query(models.SubscriptionPlan).filter(models.SubscriptionPlan.code == normalized_code).first()

    if (plan_id is not None or plan_code) and not plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found")

    return plan


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


@superadmin_router.get("/subscription-plans", response_model=List[schemas.SubscriptionPlanOut])
def list_subscription_plans_for_superadmin(
    include_inactive: bool = Query(default=True),
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin),
):
    _require_superadmin(admin)

    query = db.query(models.SubscriptionPlan)
    if not include_inactive:
        query = query.filter(models.SubscriptionPlan.is_active.is_(True))

    return query.order_by(models.SubscriptionPlan.sort_order.asc(), models.SubscriptionPlan.id.asc()).all()


@superadmin_router.patch(
    "/subscriptions/{library_id}",
    response_model=schemas.SuperadminSubscriptionPatchOut,
)
def patch_subscription(
    library_id: int,
    payload: schemas.SuperadminSubscriptionPatchRequest,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin),
):
    _require_superadmin(admin)

    library = db.query(models.Library).filter(models.Library.id == library_id).first()
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")

    subscription = ensure_subscription_for_library(db, library_id)
    plan = _resolve_subscription_plan(db, payload.plan_id, payload.plan_code)

    if payload.valid_until is not None and payload.extend_days is not None:
        raise HTTPException(status_code=400, detail="Provide either valid_until or extend_days, not both")

    if plan:
        subscription.plan_id = plan.id # type: ignore
        subscription.plan = plan.code # type: ignore

    now_utc = datetime.utcnow()
    if payload.valid_until is not None:
        subscription.valid_until = payload.valid_until # type: ignore
    elif payload.extend_days is not None:
        base_dt = subscription.valid_until if subscription.valid_until and subscription.valid_until > now_utc else now_utc # type: ignore
        subscription.valid_until = base_dt + timedelta(days=payload.extend_days) # type: ignore

    if payload.clear_trial:
        subscription.is_trial = False # type: ignore
        subscription.trial_valid_until = None # type: ignore

    if payload.status:
        normalized_status = payload.status.strip().lower()
        allowed_statuses = {"active", "inactive", "grace", "expired", "trialing", "canceled"}
        if normalized_status not in allowed_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {sorted(allowed_statuses)}")

        subscription.status = normalized_status # type: ignore

        if normalized_status == "trialing":
            if not subscription.trial_valid_until: # type: ignore
                trial_days = get_subscription_trial_days()
                subscription.trial_valid_until = datetime.combine( # type: ignore
                    datetime.utcnow().date() + timedelta(days=trial_days),
                    time(23, 59, 59),
                )
            subscription.is_trial = True # type: ignore

        if normalized_status == "active":
            subscription.is_trial = False # type: ignore
            subscription.trial_valid_until = None # type: ignore
            subscription.grace_until = None # type: ignore
            if not subscription.valid_until: # type: ignore
                subscription.valid_until = now_utc + timedelta(days=30) # type: ignore

        if normalized_status == "grace":
            grace_days = get_subscription_grace_days()
            if subscription.valid_until: # type: ignore
                subscription.grace_until = subscription.valid_until + timedelta(days=grace_days) # type: ignore
            else:
                subscription.grace_until = now_utc + timedelta(days=grace_days) # type: ignore

        if normalized_status in {"inactive", "expired", "canceled"}:
            subscription.is_trial = False # type: ignore
            subscription.trial_valid_until = None # type: ignore

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
        "message": "Subscription updated successfully",
        "subscription": subscription,
    }
