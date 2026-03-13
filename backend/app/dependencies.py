# app/dependencies.py
import logging
import os
from datetime import datetime, time, timedelta

from fastapi import Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from sqlalchemy.orm import Session

from app import crud, models
from app.database import SessionLocal

logger = logging.getLogger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _read_positive_int_env(name: str, default: int) -> int:
    raw_value = (os.getenv(name) or "").strip()
    if not raw_value:
        return default
    try:
        parsed = int(raw_value)
        return parsed if parsed > 0 else default
    except ValueError:
        return default


def get_subscription_trial_days() -> int:
    return _read_positive_int_env("SUBSCRIPTION_TRIAL_DAYS", 14)


def get_subscription_grace_days() -> int:
    return _read_positive_int_env("SUBSCRIPTION_GRACE_DAYS", 3)


def get_subscription_enforcement_mode() -> str:
    mode = (os.getenv("SUBSCRIPTION_ENFORCEMENT_MODE") or "monitor").strip().lower()
    if mode not in {"monitor", "enforce"}:
        return "monitor"
    return mode


def get_current_admin(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    try:
        Authorize.jwt_required()
        username = Authorize.get_jwt_subject()
        admin = crud.get_admin_by_username(db, username)  # type: ignore
        if not admin or admin.status != "active":  # type: ignore
            raise HTTPException(status_code=403, detail="Unauthorized")
        return admin
    except AuthJWTException:
        raise HTTPException(status_code=401, detail="token_expired_or_invalid")


def ensure_subscription_for_library(db: Session, library_id: int) -> models.Subscription:
    subscription = (
        db.query(models.Subscription)
        .filter(models.Subscription.library_id == library_id)
        .first()
    )
    if subscription:
        return subscription

    library = db.query(models.Library).filter(models.Library.id == library_id).first()
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")

    trial_days = get_subscription_trial_days()
    created_date = library.created_at or datetime.utcnow().date()

    if trial_days > 0:
        trial_until_date = created_date + timedelta(days=trial_days)
        trial_valid_until = datetime.combine(trial_until_date, time(23, 59, 59))
        status = "trialing"
        is_trial = True
    else:
        trial_valid_until = None
        status = "inactive"
        is_trial = False

    subscription = models.Subscription(
        library_id=library_id,
        status=status,
        auto_renew=False,
        cancel_at_period_end=False,
        is_trial=is_trial,
        trial_valid_until=trial_valid_until,
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription


def evaluate_subscription_access(subscription: models.Subscription) -> tuple[bool, str, str, bool]:
    now_utc = datetime.utcnow()
    grace_days = get_subscription_grace_days()

    changed = False
    effective_status = (subscription.status or "inactive").strip().lower()
    allowed = False
    reason = effective_status or "inactive"

    if subscription.is_trial and subscription.trial_valid_until:
        if now_utc <= subscription.trial_valid_until:
            effective_status = "trialing"
            allowed = True
            reason = "trialing"
        else:
            subscription.is_trial = False
            changed = True
            if effective_status == "trialing":
                effective_status = "inactive"

    if not allowed:
        if subscription.valid_until:
            if now_utc <= subscription.valid_until:
                effective_status = "active"
                allowed = True
                reason = "active"
            else:
                computed_grace_until = subscription.valid_until + timedelta(days=grace_days)
                if subscription.grace_until != computed_grace_until:
                    subscription.grace_until = computed_grace_until
                    changed = True

                if now_utc <= computed_grace_until:
                    effective_status = "grace"
                    allowed = True
                    reason = "grace"
                else:
                    effective_status = "expired"
                    allowed = False
                    reason = "expired"
        else:
            if effective_status in {"active", "trialing", "grace"}:
                allowed = True
                reason = effective_status
            else:
                allowed = False
                reason = effective_status or "inactive"

    if subscription.status != effective_status:
        subscription.status = effective_status
        changed = True

    return allowed, effective_status, reason, changed


def require_active_subscription(
    admin: models.Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if admin.role == "superadmin":
        return admin

    if admin.library_id is None:
        raise HTTPException(status_code=403, detail="Library admin is not assigned to any library")

    subscription = ensure_subscription_for_library(db, admin.library_id)
    allowed, effective_status, reason, changed = evaluate_subscription_access(subscription)

    if changed:
        db.commit()

    enforcement_mode = get_subscription_enforcement_mode()

    if allowed:
        return admin

    if enforcement_mode == "monitor":
        logger.warning(
            "Subscription monitor-mode bypass: admin_id=%s library_id=%s status=%s reason=%s",
            admin.id,
            admin.library_id,
            effective_status,
            reason,
        )
        return admin

    raise HTTPException(
        status_code=402,
        detail={
            "code": "subscription_expired",
            "message": "Subscription inactive or expired. Please renew to continue.",
            "status": effective_status,
            "library_id": admin.library_id,
        },
    )
