import calendar
import hashlib
import hmac
import json
import os
import uuid
from datetime import date, datetime, time, timedelta
from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.dependencies import ensure_subscription_for_library, get_current_admin, get_db

_RAZORPAY_IMPORT_ERROR: Exception | None = None
try:
    import razorpay
except Exception as exc:  # pragma: no cover - dependency guard
    razorpay = None  # type: ignore[assignment]
    _RAZORPAY_IMPORT_ERROR = exc


router = APIRouter(prefix="/billing", tags=["billing"])


def _require_admin(admin: models.Admin) -> None:
    if admin.role != "admin":
        raise HTTPException(status_code=403, detail="Only library admins can access this")
    if admin.library_id is None:
        raise HTTPException(status_code=400, detail="Admin is not assigned to any library")


def _get_razorpay_credentials() -> tuple[str, str]:
    key_id = (os.getenv("RAZORPAY_KEY_ID") or "").strip()
    key_secret = (os.getenv("RAZORPAY_KEY_SECRET") or "").strip()
    if not key_id or not key_secret:
        raise HTTPException(status_code=500, detail="Razorpay credentials are not configured")
    return key_id, key_secret


def _get_razorpay_client():
    if razorpay is None:
        if _RAZORPAY_IMPORT_ERROR:
            raise HTTPException(
                status_code=500,
                detail=f"Razorpay SDK import failed: {_RAZORPAY_IMPORT_ERROR}",
            )
        raise HTTPException(status_code=500, detail="Razorpay SDK is not installed")
    key_id, key_secret = _get_razorpay_credentials()
    return razorpay.Client(auth=(key_id, key_secret)), key_id


def _get_razorpay_webhook_secret() -> str:
    secret = (os.getenv("RAZORPAY_WEBHOOK_SECRET") or "").strip()
    if not secret:
        raise HTTPException(status_code=500, detail="Razorpay webhook secret is not configured")
    return secret


def _verify_webhook_signature(raw_body: bytes, signature: str | None) -> None:
    if not signature:
        raise HTTPException(status_code=401, detail="Missing Razorpay signature header")

    expected = hmac.new(
        _get_razorpay_webhook_secret().encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected, signature.strip()):
        raise HTTPException(status_code=401, detail="Invalid Razorpay webhook signature")


def _add_months(base_date: date, months: int) -> date:
    if months < 0:
        raise ValueError("months must be non-negative")
    year = base_date.year + (base_date.month - 1 + months) // 12
    month = (base_date.month - 1 + months) % 12 + 1
    day = min(base_date.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _compute_period_end(start_date: date, total_months: int) -> date:
    if total_months < 1:
        return start_date
    return _add_months(start_date, total_months) - timedelta(days=1)


def _get_subscription_start_date(subscription: models.Subscription) -> date:
    today = date.today()
    if subscription.current_period_end and subscription.current_period_end >= today:
        return subscription.current_period_end + timedelta(days=1)
    if subscription.valid_until and subscription.valid_until.date() >= today:
        return subscription.valid_until.date() + timedelta(days=1)
    return today


def _get_or_create_subscription(db: Session, library_id: int) -> models.Subscription:
    return ensure_subscription_for_library(db, library_id)


def _load_subscription_with_plan(db: Session, subscription_id: int):
    return (
        db.query(models.Subscription)
        .options(joinedload(models.Subscription.plan_config))
        .filter(models.Subscription.id == subscription_id)
        .first()
    )


def _apply_captured_transaction(
    db: Session,
    tx: models.SubscriptionTransaction,
    payment_id: str | None,
    signature: str | None = None,
    payment_data: dict | None = None,
) -> tuple[models.SubscriptionTransaction, models.Subscription]:
    plan = db.query(models.SubscriptionPlan).filter(models.SubscriptionPlan.id == tx.plan_id).first()
    if not plan:
        raise HTTPException(status_code=500, detail="Plan not found for transaction")

    subscription = _get_or_create_subscription(db, tx.library_id)
    start_date = _get_subscription_start_date(subscription)
    total_months = int(tx.billing_months) + max(0, int(plan.bonus_months))
    period_end = _compute_period_end(start_date, total_months)
    now_utc = datetime.utcnow()

    tx.subscription_id = subscription.id
    tx.plan_id = plan.id
    tx.status = "captured"
    if payment_id:
        tx.gateway_payment_id = payment_id
    if signature:
        tx.gateway_signature = signature
    tx.period_start = start_date
    tx.period_end = period_end
    tx.paid_at = now_utc

    payload_store: dict = {}
    if payment_data:
        payload_store["payment"] = payment_data
    tx.gateway_payload_json = json.dumps(payload_store, ensure_ascii=False)

    subscription.plan = plan.code
    subscription.plan_id = plan.id
    subscription.status = "active"
    subscription.current_period_start = start_date
    subscription.current_period_end = period_end
    subscription.valid_until = datetime.combine(period_end, time(23, 59, 59))
    subscription.grace_until = None
    subscription.last_payment_at = now_utc
    subscription.is_trial = False
    subscription.trial_valid_until = None
    if payment_id:
        subscription.payment_gateway_id = payment_id
    if payment_data and payment_data.get("customer_id"):
        subscription.gateway_customer_id = str(payment_data.get("customer_id"))

    return tx, subscription


@router.get("/plans", response_model=List[schemas.SubscriptionPlanOut])
def list_subscription_plans(
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin),
):
    _require_admin(admin)
    return (
        db.query(models.SubscriptionPlan)
        .filter(models.SubscriptionPlan.is_active.is_(True))
        .order_by(models.SubscriptionPlan.sort_order.asc(), models.SubscriptionPlan.id.asc())
        .all()
    )


@router.get("/me", response_model=schemas.SubscriptionOut)
def get_my_subscription(
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin),
):
    _require_admin(admin)
    subscription = _get_or_create_subscription(db, admin.library_id)  # type: ignore[arg-type]
    response_item = _load_subscription_with_plan(db, subscription.id)
    if not response_item:
        raise HTTPException(status_code=500, detail="Failed to load subscription")
    return response_item


@router.get("/transactions", response_model=List[schemas.SubscriptionTransactionOut])
def list_my_transactions(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin),
):
    _require_admin(admin)
    return (
        db.query(models.SubscriptionTransaction)
        .filter(models.SubscriptionTransaction.library_id == admin.library_id)
        .order_by(
            models.SubscriptionTransaction.created_at.desc(),
            models.SubscriptionTransaction.id.desc(),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.post("/checkout-order", response_model=schemas.BillingCheckoutOrderOut)
def create_checkout_order(
    payload: schemas.BillingCheckoutOrderRequest,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin),
):
    _require_admin(admin)

    plan_code = payload.plan_code.strip().lower()
    plan = (
        db.query(models.SubscriptionPlan)
        .filter(
            models.SubscriptionPlan.code == plan_code,
            models.SubscriptionPlan.is_active.is_(True),
        )
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    library = db.query(models.Library).filter(models.Library.id == admin.library_id).first()
    if not library:
        raise HTTPException(status_code=404, detail="Library not found")

    seats_billed = max(1, int(library.max_seats))
    amount_paise = seats_billed * int(plan.price_per_seat_paise) * int(plan.billing_months)
    if amount_paise <= 0:
        raise HTTPException(status_code=400, detail="Invalid billing amount")

    idempotency_key = (payload.idempotency_key or uuid.uuid4().hex).strip()

    existing_tx = (
        db.query(models.SubscriptionTransaction)
        .filter(
            models.SubscriptionTransaction.library_id == admin.library_id,
            models.SubscriptionTransaction.idempotency_key == idempotency_key,
        )
        .first()
    )

    subscription = _get_or_create_subscription(db, admin.library_id)  # type: ignore[arg-type]
    client, key_id = _get_razorpay_client()

    if existing_tx:
        if existing_tx.status == "captured":
            raise HTTPException(status_code=409, detail="idempotency_key already used for captured payment")
        if existing_tx.plan_id and existing_tx.plan_id != plan.id:
            raise HTTPException(status_code=409, detail="idempotency_key already used with another plan")

        order_id = existing_tx.gateway_order_id
        if not order_id:
            try:
                order = client.order.create(
                    {
                        "amount": amount_paise,
                        "currency": "INR",
                        "receipt": f"sub-{library.id}-{idempotency_key[:24]}",
                        "notes": {
                            "library_id": str(library.id),
                            "plan_code": plan.code,
                            "admin_id": str(admin.id),
                            "seats_billed": str(seats_billed),
                            "billing_months": str(plan.billing_months),
                        },
                    }
                )
            except Exception:
                raise HTTPException(status_code=502, detail="Failed to create payment order")
            order_id = order.get("id")
            if not order_id:
                raise HTTPException(status_code=502, detail="Payment gateway did not return order id")

            existing_tx.gateway_order_id = order_id
            existing_tx.amount_paise = amount_paise
            existing_tx.currency = str(order.get("currency") or "INR")
            existing_tx.seats_billed = seats_billed
            existing_tx.billing_months = int(plan.billing_months)
            existing_tx.plan_id = plan.id
            existing_tx.subscription_id = subscription.id
            existing_tx.gateway_payload_json = json.dumps({"order": order}, ensure_ascii=False)
            db.commit()
            db.refresh(existing_tx)

        return {
            "order_id": order_id,
            "key_id": key_id,
            "amount_paise": existing_tx.amount_paise,
            "currency": existing_tx.currency,
            "transaction_id": existing_tx.id,
            "idempotency_key": existing_tx.idempotency_key,
            "subscription_id": subscription.id,
            "plan": plan,
        }

    try:
        order = client.order.create(
            {
                "amount": amount_paise,
                "currency": "INR",
                "receipt": f"sub-{library.id}-{idempotency_key[:24]}",
                "notes": {
                    "library_id": str(library.id),
                    "plan_code": plan.code,
                    "admin_id": str(admin.id),
                    "seats_billed": str(seats_billed),
                    "billing_months": str(plan.billing_months),
                },
            }
        )
    except Exception:
        raise HTTPException(status_code=502, detail="Failed to create payment order")

    order_id = order.get("id")
    if not order_id:
        raise HTTPException(status_code=502, detail="Payment gateway did not return order id")

    start_date = _get_subscription_start_date(subscription)
    total_months = int(plan.billing_months) + max(0, int(plan.bonus_months))
    expected_end = _compute_period_end(start_date, total_months)

    tx = models.SubscriptionTransaction(
        subscription_id=subscription.id,
        library_id=library.id,
        plan_id=plan.id,
        amount_paise=amount_paise,
        currency=str(order.get("currency") or "INR"),
        seats_billed=seats_billed,
        billing_months=int(plan.billing_months),
        status="created",
        gateway_order_id=order_id,
        idempotency_key=idempotency_key,
        period_start=start_date,
        period_end=expected_end,
        gateway_payload_json=json.dumps({"order": order}, ensure_ascii=False),
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    return {
        "order_id": order_id,
        "key_id": key_id,
        "amount_paise": tx.amount_paise,
        "currency": tx.currency,
        "transaction_id": tx.id,
        "idempotency_key": tx.idempotency_key,
        "subscription_id": subscription.id,
        "plan": plan,
    }


@router.post("/verify-payment", response_model=schemas.BillingVerifyPaymentOut)
def verify_payment(
    payload: schemas.BillingVerifyPaymentRequest,
    db: Session = Depends(get_db),
    admin: models.Admin = Depends(get_current_admin),
):
    _require_admin(admin)

    tx = (
        db.query(models.SubscriptionTransaction)
        .filter(
            models.SubscriptionTransaction.library_id == admin.library_id,
            models.SubscriptionTransaction.gateway_order_id == payload.razorpay_order_id,
        )
        .first()
    )
    if not tx:
        raise HTTPException(status_code=404, detail="Order transaction not found")

    if tx.status == "captured":
        if tx.gateway_payment_id and tx.gateway_payment_id != payload.razorpay_payment_id:
            raise HTTPException(status_code=409, detail="Order already captured with another payment id")
        subscription = _load_subscription_with_plan(db, tx.subscription_id) if tx.subscription_id else None
        if not subscription:
            raise HTTPException(status_code=500, detail="Subscription not found for captured payment")
        return {
            "message": "Payment already verified",
            "transaction": tx,
            "subscription": subscription,
        }

    client, _ = _get_razorpay_client()
    signature_payload = {
        "razorpay_order_id": payload.razorpay_order_id,
        "razorpay_payment_id": payload.razorpay_payment_id,
        "razorpay_signature": payload.razorpay_signature,
    }
    try:
        client.utility.verify_payment_signature(signature_payload)
    except Exception:
        tx.status = "failed"
        tx.gateway_payload_json = json.dumps({"verify_request": signature_payload}, ensure_ascii=False)
        db.commit()
        raise HTTPException(status_code=400, detail="Invalid payment signature")

    payment_data = None
    try:
        payment_data = client.payment.fetch(payload.razorpay_payment_id)
    except Exception:
        payment_data = None

    if not payment_data:
        tx.gateway_payload_json = json.dumps({"verify_request": signature_payload}, ensure_ascii=False)
        db.commit()
        raise HTTPException(
            status_code=502,
            detail="Unable to confirm payment capture with gateway. Please retry verification.",
        )

    payment_status = str(payment_data.get("status") or "").lower()
    payment_amount = int(payment_data.get("amount") or 0)
    payment_currency = str(payment_data.get("currency") or "INR")

    if payment_amount != tx.amount_paise:
        raise HTTPException(status_code=400, detail="Payment amount mismatch")
    if payment_currency.upper() != str(tx.currency).upper():
        raise HTTPException(status_code=400, detail="Payment currency mismatch")
    if payment_status == "authorized":
        tx.gateway_payload_json = json.dumps(
            {"verify_request": signature_payload, "payment": payment_data},
            ensure_ascii=False,
        )
        db.commit()
        raise HTTPException(status_code=409, detail="Payment is authorized but not captured yet")
    if payment_status != "captured":
        tx.status = "failed"
        tx.gateway_payload_json = json.dumps(
            {"verify_request": signature_payload, "payment": payment_data},
            ensure_ascii=False,
        )
        db.commit()
        raise HTTPException(status_code=400, detail=f"Payment status is {payment_status or 'unknown'}")

    tx, subscription = _apply_captured_transaction(
        db=db,
        tx=tx,
        payment_id=payload.razorpay_payment_id,
        signature=payload.razorpay_signature,
        payment_data=payment_data,
    )
    payload_store = {"verify_request": signature_payload}
    if payment_data:
        payload_store["payment"] = payment_data
    tx.gateway_payload_json = json.dumps(payload_store, ensure_ascii=False)

    db.commit()
    db.refresh(tx)
    db.refresh(subscription)

    subscription_out = _load_subscription_with_plan(db, subscription.id)
    if not subscription_out:
        raise HTTPException(status_code=500, detail="Failed to load subscription")

    return {
        "message": "Payment verified successfully",
        "transaction": tx,
        "subscription": subscription_out,
    }


@router.post("/webhooks/razorpay")
async def handle_razorpay_webhook(
    request: Request,
    x_razorpay_signature: str | None = Header(default=None, alias="X-Razorpay-Signature"),
    db: Session = Depends(get_db),
):
    raw_body = await request.body()
    _verify_webhook_signature(raw_body, x_razorpay_signature)

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    event_type = str(payload.get("event") or "unknown")
    fallback_event_id = hashlib.sha256(raw_body).hexdigest()
    gateway_event_id = str(payload.get("id") or fallback_event_id)

    existing_event = (
        db.query(models.SubscriptionWebhookEvent)
        .filter(models.SubscriptionWebhookEvent.gateway_event_id == gateway_event_id)
        .first()
    )
    if existing_event:
        return {
            "ok": True,
            "event_id": gateway_event_id,
            "event_type": existing_event.event_type,
            "message": "duplicate_event_ignored",
        }

    event_row = models.SubscriptionWebhookEvent(
        gateway_event_id=gateway_event_id,
        event_type=event_type,
        payload_json=raw_body.decode("utf-8", errors="replace"),
        processed=False,
    )
    db.add(event_row)
    db.flush()

    result_message = "event_ignored"

    try:
        payload_root = payload.get("payload") or {}
        payment_wrapper = payload_root.get("payment") or {}
        payment_entity = payment_wrapper.get("entity") or {}

        if event_type == "payment.captured":
            order_id = str(payment_entity.get("order_id") or "").strip()
            payment_id = str(payment_entity.get("id") or "").strip()
            if not order_id:
                raise ValueError("order_id missing in payment payload")

            tx = (
                db.query(models.SubscriptionTransaction)
                .filter(models.SubscriptionTransaction.gateway_order_id == order_id)
                .first()
            )
            if not tx:
                result_message = f"no_transaction_for_order:{order_id}"
            else:
                if tx.status != "captured":
                    _apply_captured_transaction(
                        db=db,
                        tx=tx,
                        payment_id=payment_id or None,
                        signature=x_razorpay_signature,
                        payment_data=payment_entity,
                    )
                elif payment_id and not tx.gateway_payment_id:
                    tx.gateway_payment_id = payment_id
                result_message = "payment_captured_processed"

        elif event_type == "payment.authorized":
            order_id = str(payment_entity.get("order_id") or "").strip()
            payment_id = str(payment_entity.get("id") or "").strip()
            tx = (
                db.query(models.SubscriptionTransaction)
                .filter(models.SubscriptionTransaction.gateway_order_id == order_id)
                .first()
            ) if order_id else None
            if tx and payment_id and not tx.gateway_payment_id:
                tx.gateway_payment_id = payment_id
            result_message = "payment_authorized_recorded_waiting_capture"

        elif event_type == "payment.failed":
            order_id = str(payment_entity.get("order_id") or "").strip()
            payment_id = str(payment_entity.get("id") or "").strip()
            tx = (
                db.query(models.SubscriptionTransaction)
                .filter(models.SubscriptionTransaction.gateway_order_id == order_id)
                .first()
            ) if order_id else None

            if tx and tx.status != "captured":
                tx.status = "failed"
                if payment_id:
                    tx.gateway_payment_id = payment_id
                tx.gateway_payload_json = json.dumps(
                    {"webhook_event": event_type, "payment": payment_entity},
                    ensure_ascii=False,
                )
                result_message = "payment_failed_recorded"
            else:
                result_message = "payment_failed_ignored"
        else:
            result_message = f"event_ignored:{event_type}"

        event_row.processed = True
        event_row.processed_at = datetime.utcnow()
        event_row.error_message = None
        db.commit()
    except Exception as exc:
        event_row.processed = False
        event_row.processed_at = datetime.utcnow()
        event_row.error_message = str(exc)[:1000]
        db.commit()
        raise HTTPException(status_code=400, detail=f"Webhook processing failed: {exc}")

    return {
        "ok": True,
        "event_id": gateway_event_id,
        "event_type": event_type,
        "message": result_message,
    }
