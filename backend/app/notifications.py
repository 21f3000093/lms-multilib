from datetime import datetime
import json
import logging
import os
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import case, func
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.dependencies import get_current_admin, get_db

router = APIRouter(prefix="/notifications", tags=["notifications"])
logger = logging.getLogger(__name__)

try:
    from pywebpush import WebPushException, webpush
except ImportError:  # pragma: no cover - optional dependency guard
    WebPushException = Exception  # type: ignore[assignment]
    webpush = None  # type: ignore[assignment]


def _load_push_settings() -> tuple[str, str, str] | None:
    public_key = (os.getenv("PUSH_VAPID_PUBLIC_KEY") or "").strip()
    private_key = (os.getenv("PUSH_VAPID_PRIVATE_KEY") or "").strip()
    subject = (os.getenv("PUSH_VAPID_SUBJECT") or "").strip()

    if not public_key or not private_key or not subject:
        return None
    return public_key, private_key, subject


def _is_push_enabled() -> bool:
    return _load_push_settings() is not None and webpush is not None


def _normalize_click_url(click_url: str | None, fallback: str = "/notifications") -> str:
    normalized = (click_url or fallback).strip()
    if normalized.startswith(("/", "http://", "https://")):
        return normalized
    raise HTTPException(status_code=400, detail="click_url must start with / or http(s)://")


def _send_push_to_admins(
    db: Session,
    admin_ids: list[int],
    title: str,
    body: str,
    click_url: str,
) -> None:
    if not admin_ids or not _is_push_enabled():
        return

    settings = _load_push_settings()
    if not settings:
        return

    _, vapid_private_key, vapid_subject = settings

    subscriptions = (
        db.query(models.PushSubscription)
        .filter(models.PushSubscription.admin_id.in_(admin_ids))
        .all()
    )
    if not subscriptions:
        return

    now = datetime.utcnow()
    payload = json.dumps(
        {
            "title": title,
            "body": body,
            "url": click_url,
        },
        ensure_ascii=False,
    )

    mutated = False
    for subscription in subscriptions:
        subscription_info = {
            "endpoint": subscription.endpoint,
            "keys": {
                "p256dh": subscription.p256dh,
                "auth": subscription.auth,
            },
        }
        if subscription.expiration_time:
            subscription_info["expirationTime"] = subscription.expiration_time

        try:
            webpush(
                subscription_info=subscription_info,  # type: ignore[arg-type]
                data=payload,
                vapid_private_key=vapid_private_key,
                vapid_claims={"sub": vapid_subject},
                ttl=60 * 60 * 24,
            )
            subscription.last_seen_at = now
            subscription.updated_at = now
            mutated = True
        except WebPushException as exc:  # type: ignore[misc]
            status_code = getattr(getattr(exc, "response", None), "status_code", None)
            if status_code in (404, 410):
                db.delete(subscription)
                mutated = True
            else:
                logger.warning("Push delivery failed for endpoint=%s status=%s", subscription.endpoint, status_code)
        except Exception as exc:  # pragma: no cover - defensive guard
            logger.warning("Unexpected push delivery failure for endpoint=%s error=%s", subscription.endpoint, exc)

    if mutated:
        db.commit()


def _require_superadmin(admin: models.Admin) -> None:
    if admin.role != "superadmin":
        raise HTTPException(status_code=403, detail="Only superadmin can access this")


def _require_admin(admin: models.Admin) -> None:
    if admin.role != "admin":
        raise HTTPException(status_code=403, detail="Only library admins can access this")


def _serialize_notification(
    notification: models.Notification,
    recipient_count: int = 0,
    unread_count: int = 0,
    sender_username: str | None = None,
) -> dict:
    resolved_sender_username = sender_username
    if resolved_sender_username is None and notification.sender is not None:
        resolved_sender_username = notification.sender.username

    return {
        "id": notification.id,
        "title": notification.title,
        "message": notification.message,
        "category": notification.category,
        "sender_admin_id": notification.sender_admin_id,
        "sender_username": resolved_sender_username,
        "target_type": notification.target_type,
        "target_library_id": notification.target_library_id,
        "is_active": notification.is_active,
        "created_at": notification.created_at,
        "expires_at": notification.expires_at,
        "recipient_count": int(recipient_count or 0),
        "unread_count": int(unread_count or 0),
    }


@router.post("/", response_model=schemas.NotificationOut, status_code=201)
def create_notification(
    payload: schemas.NotificationCreate,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin),
):
    _require_superadmin(admin)
    click_url = _normalize_click_url(payload.click_url)

    target_admin_ids = sorted(set(payload.target_admin_ids or []))

    if payload.target_library_id is not None and target_admin_ids:
        raise HTTPException(
            status_code=400,
            detail="Provide either target_library_id or target_admin_ids, not both",
        )

    admin_query = db.query(models.Admin).filter(models.Admin.role == "admin")
    target_type = "all_admins"

    if target_admin_ids:
        target_type = "admins"
        target_admins = admin_query.filter(models.Admin.id.in_(target_admin_ids)).all()
        found_ids = {target_admin.id for target_admin in target_admins}
        missing_ids = [target_id for target_id in target_admin_ids if target_id not in found_ids]
        if missing_ids:
            raise HTTPException(status_code=400, detail=f"Invalid admin IDs: {missing_ids}")
    elif payload.target_library_id is not None:
        target_type = "library"
        library = (
            db.query(models.Library)
            .filter(models.Library.id == payload.target_library_id)
            .first()
        )
        if not library:
            raise HTTPException(status_code=404, detail="Library not found")
        target_admins = admin_query.filter(
            models.Admin.library_id == payload.target_library_id
        ).all()
    else:
        target_admins = admin_query.all()

    if not target_admins:
        raise HTTPException(status_code=400, detail="No target admins found")

    category = payload.category.strip().lower() or "general"

    notification = models.Notification(
        title=payload.title.strip(),
        message=payload.message.strip(),
        category=category,
        sender_admin_id=admin.id,
        target_type=target_type,
        target_library_id=payload.target_library_id if target_type == "library" else None,
    )

    db.add(notification)
    db.flush()

    recipients = [
        models.NotificationRecipient(notification_id=notification.id, admin_id=target_admin.id)
        for target_admin in target_admins
    ]
    db.add_all(recipients)
    db.commit()
    db.refresh(notification)
    try:
        _send_push_to_admins(
            db=db,
            admin_ids=[target_admin.id for target_admin in target_admins],
            title=notification.title,
            body=notification.message,
            click_url=click_url,
        )
    except Exception as exc:  # pragma: no cover - push must not break in-app notifications
        logger.warning("Push broadcast skipped due to error: %s", exc)

    return _serialize_notification(
        notification,
        recipient_count=len(target_admins),
        unread_count=len(target_admins),
        sender_username=admin.username,
    )


@router.get("/push/config", response_model=schemas.PushConfigOut)
def get_push_config(admin: models.Admin = Depends(get_current_admin)):
    if admin.role not in {"admin", "superadmin"}:
        raise HTTPException(status_code=403, detail="Unauthorized")

    settings = _load_push_settings()
    enabled = settings is not None and webpush is not None
    public_key = settings[0] if settings else None
    return {
        "enabled": enabled,
        "vapid_public_key": public_key,
    }


@router.post("/push/subscriptions", response_model=schemas.PushSubscriptionOut)
def upsert_push_subscription(
    payload: schemas.PushSubscriptionCreate,
    request: Request,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin),
):
    _require_admin(admin)

    endpoint = payload.endpoint.strip()
    if not endpoint:
        raise HTTPException(status_code=400, detail="Invalid subscription endpoint")

    now = datetime.utcnow()
    existing = (
        db.query(models.PushSubscription)
        .filter(models.PushSubscription.endpoint == endpoint)
        .first()
    )

    if existing:
        existing.admin_id = admin.id
        existing.p256dh = payload.keys.p256dh
        existing.auth = payload.keys.auth
        existing.expiration_time = payload.expirationTime
        existing.user_agent = request.headers.get("user-agent")
        existing.updated_at = now
        existing.last_seen_at = now
        db.commit()
        db.refresh(existing)
        return existing

    subscription = models.PushSubscription(
        admin_id=admin.id,
        endpoint=endpoint,
        p256dh=payload.keys.p256dh,
        auth=payload.keys.auth,
        expiration_time=payload.expirationTime,
        user_agent=request.headers.get("user-agent"),
        created_at=now,
        updated_at=now,
        last_seen_at=now,
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription


@router.post("/push/subscriptions/unsubscribe")
def unsubscribe_push_subscription(
    payload: schemas.PushSubscriptionDelete,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin),
):
    _require_admin(admin)

    endpoint = payload.endpoint.strip()
    subscription = (
        db.query(models.PushSubscription)
        .filter(
            models.PushSubscription.admin_id == admin.id,
            models.PushSubscription.endpoint == endpoint,
        )
        .first()
    )
    if subscription:
        db.delete(subscription)
        db.commit()

    return {"message": "Push subscription removed"}


@router.get("/sent", response_model=List[schemas.NotificationOut])
def list_sent_notifications(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin),
):
    _require_superadmin(admin)

    recipient_counts = (
        db.query(
            models.NotificationRecipient.notification_id.label("notification_id"),
            func.count(models.NotificationRecipient.id).label("recipient_count"),
            func.sum(
                case(
                    (models.NotificationRecipient.is_read.is_(False), 1),
                    else_=0,
                )
            ).label("unread_count"),
        )
        .group_by(models.NotificationRecipient.notification_id)
        .subquery()
    )

    notification_rows = (
        db.query(
            models.Notification,
            recipient_counts.c.recipient_count,
            recipient_counts.c.unread_count,
        )
        .outerjoin(
            recipient_counts,
            recipient_counts.c.notification_id == models.Notification.id,
        )
        .options(joinedload(models.Notification.sender))
        .order_by(models.Notification.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        _serialize_notification(notification, recipient_count, unread_count)
        for notification, recipient_count, unread_count in notification_rows
    ]


@router.get("/inbox", response_model=List[schemas.NotificationInboxItem])
def list_inbox_notifications(
    unread_only: bool = False,
    limit: int = Query(default=100, ge=1, le=300),
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin),
):
    _require_admin(admin)

    query = (
        db.query(models.NotificationRecipient)
        .join(
            models.Notification,
            models.Notification.id == models.NotificationRecipient.notification_id,
        )
        .options(
            joinedload(models.NotificationRecipient.notification).joinedload(
                models.Notification.sender
            )
        )
        .filter(
            models.NotificationRecipient.admin_id == admin.id,
            models.Notification.is_active.is_(True),
        )
    )

    if unread_only:
        query = query.filter(models.NotificationRecipient.is_read.is_(False))

    recipients = (
        query.order_by(models.Notification.created_at.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "recipient_id": recipient.id,
            "notification_id": recipient.notification_id,
            "title": recipient.notification.title,
            "message": recipient.notification.message,
            "category": recipient.notification.category,
            "created_at": recipient.notification.created_at,
            "sender_username": (
                recipient.notification.sender.username
                if recipient.notification.sender is not None
                else None
            ),
            "target_library_id": recipient.notification.target_library_id,
            "is_read": recipient.is_read,
            "read_at": recipient.read_at,
        }
        for recipient in recipients
    ]


@router.get("/inbox/unread-count", response_model=schemas.NotificationUnreadCount)
def get_unread_count(
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin),
):
    _require_admin(admin)

    unread_count = (
        db.query(func.count(models.NotificationRecipient.id))
        .join(
            models.Notification,
            models.Notification.id == models.NotificationRecipient.notification_id,
        )
        .filter(
            models.NotificationRecipient.admin_id == admin.id,
            models.NotificationRecipient.is_read.is_(False),
            models.Notification.is_active.is_(True),
        )
        .scalar()
        or 0
    )

    return {"unread_count": int(unread_count)}


@router.patch("/inbox/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin),
):
    _require_admin(admin)

    recipient = (
        db.query(models.NotificationRecipient)
        .join(
            models.Notification,
            models.Notification.id == models.NotificationRecipient.notification_id,
        )
        .filter(
            models.NotificationRecipient.admin_id == admin.id,
            models.NotificationRecipient.notification_id == notification_id,
            models.Notification.is_active.is_(True),
        )
        .first()
    )

    if not recipient:
        raise HTTPException(status_code=404, detail="Notification not found")

    if not recipient.is_read:
        recipient.is_read = True
        recipient.read_at = datetime.utcnow()
        db.commit()

    return {"message": "Notification marked as read"}


@router.patch("/inbox/read-all")
def mark_all_notifications_read(
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin),
):
    _require_admin(admin)

    recipients = (
        db.query(models.NotificationRecipient)
        .join(
            models.Notification,
            models.Notification.id == models.NotificationRecipient.notification_id,
        )
        .filter(
            models.NotificationRecipient.admin_id == admin.id,
            models.NotificationRecipient.is_read.is_(False),
            models.Notification.is_active.is_(True),
        )
        .all()
    )

    now = datetime.utcnow()
    for recipient in recipients:
        recipient.is_read = True
        recipient.read_at = now

    db.commit()

    return {
        "message": "All notifications marked as read",
        "updated_count": len(recipients),
    }
