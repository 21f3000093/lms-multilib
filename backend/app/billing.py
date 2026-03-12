import calendar
import json
import os
import uuid
from datetime import date, datetime, time, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.dependencies import get_current_admin, get_db

try:
    import razorpay
except ImportError:  # pragma: no cover - dependency guard
    razorpay = None  # type: ignore[assignment]


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
        raise HTTPException(status_code=500, detail="Razorpay SDK is not installed")
    key_id, key_secret = _get_razorpay_credentials()
    return razorpay.Client(auth=(key_id, key_secret)), key_id


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
    subscription = db.query(models.Subscription).filter(models.Subscription.library_id == library_id).first()
    if subscription:
        return subscription

    subscription = models.Subscription(
        library_id=library_id,
        status="inactive",
        auto_renew=False,
        cancel_at_period_end=False,
        is_trial=False,
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription


def _load_subscription_with_plan(db: Session, subscription_id: int):
    return (
        db.query(models.Subscription)
        .options(joinedload(models.Subscription.plan_config))
        .filter(models.Subscription.id == subscription_id)
        .first()
    )


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

    if payment_data:
        payment_status = str(payment_data.get("status") or "").lower()
        payment_amount = int(payment_data.get("amount") or 0)
        payment_currency = str(payment_data.get("currency") or "INR")

        if payment_amount != tx.amount_paise:
            raise HTTPException(status_code=400, detail="Payment amount mismatch")
        if payment_currency.upper() != str(tx.currency).upper():
            raise HTTPException(status_code=400, detail="Payment currency mismatch")
        if payment_status not in {"captured", "authorized"}:
            tx.status = "failed"
            tx.gateway_payload_json = json.dumps(
                {"verify_request": signature_payload, "payment": payment_data},
                ensure_ascii=False,
            )
            db.commit()
            raise HTTPException(status_code=400, detail=f"Payment status is {payment_status or 'unknown'}")

    plan = db.query(models.SubscriptionPlan).filter(models.SubscriptionPlan.id == tx.plan_id).first()
    if not plan:
        raise HTTPException(status_code=500, detail="Plan not found for transaction")

    subscription = _get_or_create_subscription(db, admin.library_id)  # type: ignore[arg-type]
    start_date = _get_subscription_start_date(subscription)
    total_months = int(tx.billing_months) + max(0, int(plan.bonus_months))
    period_end = _compute_period_end(start_date, total_months)
    now_utc = datetime.utcnow()

    tx.subscription_id = subscription.id
    tx.plan_id = plan.id
    tx.status = "captured"
    tx.gateway_payment_id = payload.razorpay_payment_id
    tx.gateway_signature = payload.razorpay_signature
    tx.period_start = start_date
    tx.period_end = period_end
    tx.paid_at = now_utc

    payload_store = {"verify_request": signature_payload}
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
    subscription.payment_gateway_id = payload.razorpay_payment_id

    if payment_data and payment_data.get("customer_id"):
        subscription.gateway_customer_id = str(payment_data.get("customer_id"))

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
