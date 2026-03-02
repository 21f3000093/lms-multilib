from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import case, func
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.dependencies import get_current_admin, get_db

router = APIRouter(prefix="/notifications", tags=["notifications"])


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

    return _serialize_notification(
        notification,
        recipient_count=len(target_admins),
        unread_count=len(target_admins),
        sender_username=admin.username,
    )


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
