import hashlib
import json
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone

import requests
from fastapi import HTTPException, Request
from sqlalchemy.orm import Session

from app import crud
from app import models
from app.emailer import send_email

try:
    from google.auth import exceptions as google_auth_exceptions
    from google.auth.transport import requests as google_transport_requests
    from google.oauth2 import id_token as google_id_token
except ImportError:  # pragma: no cover - runtime fallback when dependency is not installed yet
    google_auth_exceptions = None
    google_transport_requests = None
    google_id_token = None

logger = logging.getLogger(__name__)

SIGNUP_VERIFY = "signup_verify"
SIGNUP_RESUBMIT = "signup_resubmit"
RESET_LINK = "reset_link"
RESET_OTP = "reset_otp"
GOOGLE_ONBOARDING = "google_onboarding"

PENDING_EMAIL_VERIFICATION = "pending_email_verification"
PENDING_APPROVAL = "pending_approval"
APPROVED = "approved"
REJECTED = "rejected"
EXPIRED = "expired"

TURNSTILE_VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def _read_positive_int_env(name: str, default: int) -> int:
    raw = (os.getenv(name) or "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
        return value if value > 0 else default
    except ValueError:
        return default


def get_app_public_url() -> str:
    return (os.getenv("APP_PUBLIC_URL") or "http://localhost:8080").strip().rstrip("/")


def get_turnstile_site_key() -> str | None:
    value = (os.getenv("TURNSTILE_SITE_KEY") or "").strip()
    return value or None


def get_turnstile_secret_key() -> str | None:
    value = (os.getenv("TURNSTILE_SECRET_KEY") or "").strip()
    return value or None


def get_google_client_id() -> str | None:
    value = (os.getenv("GOOGLE_OAUTH_CLIENT_ID") or "").strip()
    return value or None


def is_turnstile_enabled() -> bool:
    return bool(get_turnstile_site_key() and get_turnstile_secret_key())


def is_google_auth_enabled() -> bool:
    return bool(get_google_client_id() and google_id_token and google_transport_requests)


def get_verify_email_expiry_minutes() -> int:
    return _read_positive_int_env("AUTH_VERIFY_EMAIL_EXPIRES_MINUTES", 60)


def get_reset_link_expiry_minutes() -> int:
    return _read_positive_int_env("AUTH_RESET_LINK_EXPIRES_MINUTES", 30)


def get_reset_otp_expiry_minutes() -> int:
    return _read_positive_int_env("AUTH_RESET_OTP_EXPIRES_MINUTES", 10)


def get_reset_otp_max_attempts() -> int:
    return _read_positive_int_env("AUTH_RESET_OTP_MAX_ATTEMPTS", 5)


def get_lockout_threshold() -> int:
    return _read_positive_int_env("AUTH_LOCKOUT_THRESHOLD", 5)


def get_lockout_minutes() -> int:
    return _read_positive_int_env("AUTH_LOCKOUT_MINUTES", 15)


def get_captcha_threshold() -> int:
    threshold = _read_positive_int_env("AUTH_CAPTCHA_THRESHOLD", 3)
    return min(threshold, get_lockout_threshold())


def get_google_onboarding_expiry_minutes() -> int:
    return _read_positive_int_env("AUTH_GOOGLE_ONBOARDING_EXPIRES_MINUTES", 30)


def get_signup_activation_mode() -> str:
    mode = (os.getenv("SIGNUP_ACTIVATION_MODE") or "risk_based").strip().lower()
    if mode not in {"manual", "risk_based", "auto"}:
        return "risk_based"
    return mode


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def normalize_username(value: str) -> str:
    return " ".join((value or "").strip().split())


def normalize_email(value: str) -> str:
    return (value or "").strip().lower()


def normalize_phone(value: str) -> str:
    return "".join(ch for ch in (value or "").strip() if ch.isdigit() or ch == "+")


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def serialize_metadata(metadata: dict | None) -> str | None:
    if not metadata:
        return None
    try:
        return json.dumps(metadata, default=str)
    except TypeError:
        return json.dumps({"unserializable": True})


def log_security_event(
    db: Session,
    *,
    event_type: str,
    outcome: str,
    ip_address: str | None = None,
    identifier: str | None = None,
    target_email: str | None = None,
    signup_request_id: int | None = None,
    admin_id: int | None = None,
    metadata: dict | None = None,
) -> None:
    db.add(
        models.AuthSecurityEvent(
            event_type=event_type,
            outcome=outcome,
            ip_address=ip_address,
            identifier=identifier,
            target_email=target_email,
            signup_request_id=signup_request_id,
            admin_id=admin_id,
            metadata_json=serialize_metadata(metadata),
        )
    )
    db.flush()


def _get_tracker(db: Session, scope_type: str, scope_key: str) -> models.AuthAttemptTracker:
    tracker = (
        db.query(models.AuthAttemptTracker)
        .filter(models.AuthAttemptTracker.scope_type == scope_type, models.AuthAttemptTracker.scope_key == scope_key)
        .first()
    )
    if tracker:
        return tracker
    tracker = models.AuthAttemptTracker(scope_type=scope_type, scope_key=scope_key)
    db.add(tracker)
    db.flush()
    return tracker


def _normalize_failure_window(tracker: models.AuthAttemptTracker, now_utc: datetime) -> None:
    if tracker.last_failure_at and now_utc - tracker.last_failure_at > timedelta(minutes=get_lockout_minutes()):
        tracker.failure_count = 0
        tracker.locked_until = None
        tracker.captcha_required_until = None


def _build_auth_error(code: str, message: str, *, requires_captcha: bool = False, retry_after_seconds: int | None = None):
    detail = {
        "code": code,
        "message": message,
        "requires_captcha": requires_captcha,
    }
    if retry_after_seconds is not None:
        detail["retry_after_seconds"] = retry_after_seconds
    return detail


def get_scope_state(db: Session, scopes: list[tuple[str, str]]) -> tuple[bool, bool, int | None]:
    now_utc = utcnow()
    requires_captcha = False
    locked = False
    retry_after_seconds: int | None = None

    for scope_type, scope_key in scopes:
        tracker = (
            db.query(models.AuthAttemptTracker)
            .filter(models.AuthAttemptTracker.scope_type == scope_type, models.AuthAttemptTracker.scope_key == scope_key)
            .first()
        )
        if not tracker:
            continue
        _normalize_failure_window(tracker, now_utc)
        if tracker.locked_until and tracker.locked_until > now_utc:
            locked = True
            retry_after_seconds = max(retry_after_seconds or 0, int((tracker.locked_until - now_utc).total_seconds()))
        if tracker.captcha_required_until and tracker.captcha_required_until > now_utc:
            requires_captcha = True

    return locked, requires_captcha, retry_after_seconds


def verify_turnstile_token(captcha_token: str | None, request_ip: str | None) -> bool:
    if not is_turnstile_enabled():
        return True
    if not captcha_token:
        return False

    secret = get_turnstile_secret_key()
    if not secret:
        return False

    try:
        response = requests.post(
            TURNSTILE_VERIFY_URL,
            data={
                "secret": secret,
                "response": captcha_token,
                "remoteip": request_ip,
            },
            timeout=10,
        )
        payload = response.json()
    except requests.RequestException:
        logger.exception("Turnstile verification failed")
        return False
    except ValueError:
        return False

    return bool(payload.get("success"))


def enforce_auth_protection(
    db: Session,
    *,
    request: Request,
    scopes: list[tuple[str, str]],
    captcha_token: str | None,
    event_type: str,
    identifier: str | None = None,
    target_email: str | None = None,
    signup_request_id: int | None = None,
) -> None:
    request_ip = get_client_ip(request)
    locked, requires_captcha, retry_after_seconds = get_scope_state(db, scopes)

    if locked:
        log_security_event(
            db,
            event_type=event_type,
            outcome="temporarily_locked",
            ip_address=request_ip,
            identifier=identifier,
            target_email=target_email,
            signup_request_id=signup_request_id,
            metadata={"retry_after_seconds": retry_after_seconds},
        )
        db.commit()
        raise HTTPException(
            status_code=429,
            detail=_build_auth_error(
                "temporarily_locked",
                "Too many attempts. Please try again later.",
                requires_captcha=True,
                retry_after_seconds=retry_after_seconds,
            ),
        )

    if requires_captcha and not verify_turnstile_token(captcha_token, request_ip):
        log_security_event(
            db,
            event_type=event_type,
            outcome="captcha_required",
            ip_address=request_ip,
            identifier=identifier,
            target_email=target_email,
            signup_request_id=signup_request_id,
        )
        db.commit()
        raise HTTPException(
            status_code=429,
            detail=_build_auth_error(
                "captcha_required",
                "CAPTCHA verification is required to continue.",
                requires_captcha=True,
            ),
        )


def record_auth_failure(
    db: Session,
    *,
    scopes: list[tuple[str, str]],
    event_type: str,
    request: Request,
    identifier: str | None = None,
    target_email: str | None = None,
    signup_request_id: int | None = None,
    admin_id: int | None = None,
    metadata: dict | None = None,
) -> None:
    now_utc = utcnow()
    lockout_threshold = get_lockout_threshold()
    captcha_threshold = get_captcha_threshold()
    lockout_minutes = get_lockout_minutes()

    for scope_type, scope_key in scopes:
        tracker = _get_tracker(db, scope_type, scope_key)
        _normalize_failure_window(tracker, now_utc)
        tracker.failure_count = int(tracker.failure_count or 0) + 1
        tracker.last_failure_at = now_utc

        if tracker.failure_count >= captcha_threshold:
            tracker.captcha_required_until = now_utc + timedelta(minutes=lockout_minutes * 2)
        if tracker.failure_count >= lockout_threshold:
            tracker.locked_until = now_utc + timedelta(minutes=lockout_minutes)
            tracker.captcha_required_until = now_utc + timedelta(minutes=lockout_minutes * 2)

    log_security_event(
        db,
        event_type=event_type,
        outcome="failure",
        ip_address=get_client_ip(request),
        identifier=identifier,
        target_email=target_email,
        signup_request_id=signup_request_id,
        admin_id=admin_id,
        metadata=metadata,
    )
    db.commit()


def record_auth_success(db: Session, *, scopes: list[tuple[str, str]]) -> None:
    for scope_type, scope_key in scopes:
        tracker = (
            db.query(models.AuthAttemptTracker)
            .filter(models.AuthAttemptTracker.scope_type == scope_type, models.AuthAttemptTracker.scope_key == scope_key)
            .first()
        )
        if not tracker:
            continue
        tracker.failure_count = 0
        tracker.locked_until = None
        tracker.captcha_required_until = None
        tracker.last_failure_at = None
    db.commit()


def hash_raw_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def issue_auth_token(
    db: Session,
    *,
    purpose: str,
    target_email: str,
    signup_request_id: int | None = None,
    admin_id: int | None = None,
    expires_minutes: int,
    max_attempts: int = 1,
    payload: dict | None = None,
    raw_token: str | None = None,
) -> tuple[str, models.AuthActionToken]:
    token_value = raw_token or secrets.token_urlsafe(32)
    token = models.AuthActionToken(
        purpose=purpose,
        token_hash=hash_raw_token(token_value),
        target_email=target_email,
        signup_request_id=signup_request_id,
        admin_id=admin_id,
        expires_at=utcnow() + timedelta(minutes=expires_minutes),
        max_attempts=max_attempts,
        payload_json=serialize_metadata(payload),
    )
    db.add(token)
    db.flush()
    return token_value, token


def issue_otp_token(
    db: Session,
    *,
    target_email: str,
    admin_id: int,
    expires_minutes: int,
    max_attempts: int,
) -> tuple[str, models.AuthActionToken]:
    otp = f"{secrets.randbelow(1000000):06d}"
    return issue_auth_token(
        db,
        purpose=RESET_OTP,
        target_email=target_email,
        admin_id=admin_id,
        expires_minutes=expires_minutes,
        max_attempts=max_attempts,
        raw_token=otp,
    )


def _active_token_query(db: Session, purpose: str):
    now_utc = utcnow()
    return (
        db.query(models.AuthActionToken)
        .filter(models.AuthActionToken.purpose == purpose)
        .filter(models.AuthActionToken.consumed_at.is_(None))
        .filter(models.AuthActionToken.expires_at > now_utc)
    )


def consume_token_by_value(db: Session, *, purpose: str, raw_token: str) -> models.AuthActionToken | None:
    token_hash = hash_raw_token(raw_token)
    token = _active_token_query(db, purpose).filter(models.AuthActionToken.token_hash == token_hash).first()
    if not token:
        return None
    token.consumed_at = utcnow()
    db.flush()
    return token


def get_token_by_value(db: Session, *, purpose: str, raw_token: str) -> models.AuthActionToken | None:
    token_hash = hash_raw_token(raw_token)
    return _active_token_query(db, purpose).filter(models.AuthActionToken.token_hash == token_hash).first()


def invalidate_tokens(
    db: Session,
    *,
    purpose: str | None = None,
    signup_request_id: int | None = None,
    admin_id: int | None = None,
    target_email: str | None = None,
) -> None:
    query = db.query(models.AuthActionToken).filter(models.AuthActionToken.consumed_at.is_(None))
    if purpose is not None:
        query = query.filter(models.AuthActionToken.purpose == purpose)
    if signup_request_id is not None:
        query = query.filter(models.AuthActionToken.signup_request_id == signup_request_id)
    if admin_id is not None:
        query = query.filter(models.AuthActionToken.admin_id == admin_id)
    if target_email is not None:
        query = query.filter(models.AuthActionToken.target_email == target_email)
    for token in query.all():
        token.consumed_at = utcnow()
    db.flush()


def get_token_payload(token: models.AuthActionToken | None) -> dict:
    if not token or not token.payload_json:
        return {}
    try:
        payload = json.loads(token.payload_json)
        return payload if isinstance(payload, dict) else {}
    except json.JSONDecodeError:
        return {}


def verify_google_credential(raw_credential: str) -> dict[str, str]:
    client_id = get_google_client_id()
    if not is_google_auth_enabled() or not client_id or not google_id_token or not google_transport_requests:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "google_auth_not_configured",
                "message": "Google sign-in is not configured yet.",
            },
        )

    try:
        payload = google_id_token.verify_oauth2_token(
            raw_credential,
            google_transport_requests.Request(),
            client_id,
        )
    except Exception:
        logger.exception("Google credential verification failed")
        raise HTTPException(
            status_code=400,
            detail={
                "code": "invalid_google_token",
                "message": "Google sign-in could not be verified. Please try again.",
            },
        )

    email = normalize_email(str(payload.get("email") or ""))
    provider_subject = str(payload.get("sub") or "").strip()
    if not email or not provider_subject or not payload.get("email_verified"):
        raise HTTPException(
            status_code=400,
            detail={
                "code": "invalid_google_token",
                "message": "Google account email could not be verified.",
            },
        )

    return {
        "email": email,
        "provider_subject": provider_subject,
        "name": str(payload.get("name") or "").strip(),
        "given_name": str(payload.get("given_name") or "").strip(),
    }


def suggest_username_from_google(*, email: str, name: str | None = None) -> str:
    base_source = (name or "").strip() or email.split("@", 1)[0]
    cleaned = "".join(ch.lower() if ch.isalnum() else "_" for ch in base_source)
    while "__" in cleaned:
        cleaned = cleaned.replace("__", "_")
    cleaned = cleaned.strip("_")
    return cleaned or "library_admin"


def evaluate_signup_review_reason(
    db: Session,
    *,
    signup_request: models.SignupRequest,
    scopes: list[tuple[str, str]] | None = None,
) -> str | None:
    if crud.get_admin_by_username(db, signup_request.admin_username):
        return "The requested username now conflicts with an existing account."
    if crud.get_admin_by_email(db, signup_request.admin_email):
        return "The requested email now conflicts with an existing account."

    conflicting_request = (
        db.query(models.SignupRequest)
        .filter(models.SignupRequest.id != signup_request.id)
        .filter(models.SignupRequest.status.in_([PENDING_EMAIL_VERIFICATION, PENDING_APPROVAL]))
        .filter(
            (models.SignupRequest.normalized_email == signup_request.normalized_email)
            | (models.SignupRequest.normalized_username == signup_request.normalized_username)
        )
        .first()
    )
    if conflicting_request:
        return "Another open signup request already exists for this username or email."

    if scopes:
        locked, requires_captcha, _ = get_scope_state(db, scopes)
        if locked:
            return "Recent abuse protection locked this signup for manual review."
        if requires_captcha:
            return "Recent abuse signals require manual review before activation."

    risky_event = (
        db.query(models.AuthSecurityEvent)
        .filter(models.AuthSecurityEvent.signup_request_id == signup_request.id)
        .filter(models.AuthSecurityEvent.outcome.in_(["failure", "captcha_required", "temporarily_locked"]))
        .order_by(models.AuthSecurityEvent.created_at.desc())
        .first()
    )
    if risky_event:
        if risky_event.outcome == "temporarily_locked":
            return "This signup was temporarily locked by abuse protection."
        if risky_event.outcome == "captcha_required":
            return "This signup triggered CAPTCHA escalation and needs review."
        return "Recent failed verification or signup attempts require manual review."

    return None


def expire_signup_request_if_needed(db: Session, signup_request: models.SignupRequest) -> models.SignupRequest:
    if (
        signup_request.status == PENDING_EMAIL_VERIFICATION
        and signup_request.expires_at is not None
        and signup_request.expires_at <= utcnow()
    ):
        signup_request.status = EXPIRED
        db.flush()
    return signup_request


def get_open_signup_request_by_email_or_username(db: Session, *, normalized_email: str, normalized_username: str):
    return (
        db.query(models.SignupRequest)
        .filter(models.SignupRequest.status.in_([PENDING_EMAIL_VERIFICATION, PENDING_APPROVAL]))
        .filter(
            (models.SignupRequest.normalized_email == normalized_email)
            | (models.SignupRequest.normalized_username == normalized_username)
        )
        .first()
    )


def get_signup_request_by_public_id(db: Session, public_id: str) -> models.SignupRequest | None:
    signup_request = (
        db.query(models.SignupRequest)
        .filter(models.SignupRequest.public_id == public_id)
        .first()
    )
    if signup_request:
        expire_signup_request_if_needed(db, signup_request)
        db.flush()
    return signup_request


def create_signup_request(
    db: Session,
    *,
    library_name: str,
    max_seats: int,
    contact_phone: str,
    address: str | None,
    admin_username: str,
    admin_email: str,
    password_hash: str,
    signup_method: str = "password",
    provider: str | None = None,
    provider_subject: str | None = None,
) -> models.SignupRequest:
    signup_request = models.SignupRequest(
        public_id=secrets.token_urlsafe(12),
        library_name=library_name,
        max_seats=max_seats,
        contact_phone=contact_phone,
        address=address,
        admin_username=admin_username,
        admin_email=admin_email,
        password_hash=password_hash,
        signup_method=signup_method,
        provider=provider,
        provider_subject=provider_subject,
        normalized_username=normalize_username(admin_username),
        normalized_email=normalize_email(admin_email),
        normalized_phone=normalize_phone(contact_phone),
        status=PENDING_EMAIL_VERIFICATION,
        verification_sent_at=utcnow(),
        expires_at=utcnow() + timedelta(minutes=get_verify_email_expiry_minutes()),
    )
    db.add(signup_request)
    db.flush()
    return signup_request


def _signup_status_url(public_id: str, query: str) -> str:
    return f"{get_app_public_url()}/signup/status/{public_id}{query}"


def send_signup_verification_email(signup_request: models.SignupRequest, raw_token: str) -> bool:
    verify_url = _signup_status_url(signup_request.public_id, f"?verify_token={raw_token}")
    subject = "Verify your Smart Library signup"
    text = (
        f"Hi {signup_request.admin_username},\n\n"
        f"Please verify your email to continue your library signup.\n\n"
        f"Verify email: {verify_url}\n\n"
        f"If you did not request this, you can ignore this email."
    )
    return send_email(to_email=signup_request.admin_email, subject=subject, text=text)


def send_signup_approval_email(signup_request: models.SignupRequest) -> bool:
    login_url = f"{get_app_public_url()}/login"
    subject = "Your Smart Library workspace is approved"
    text = (
        f"Hi {signup_request.admin_username},\n\n"
        f"Your library signup has been approved. You can now log in and start your trial.\n\n"
        f"Login: {login_url}\n"
        f"Username: {signup_request.admin_username}\n\n"
        f"Thanks,\nSmart Library App"
    )
    return send_email(to_email=signup_request.admin_email, subject=subject, text=text)


def send_signup_rejection_email(signup_request: models.SignupRequest, raw_token: str) -> bool:
    resubmit_url = _signup_status_url(signup_request.public_id, f"?resubmit_token={raw_token}")
    subject = "Action needed for your Smart Library signup"
    text = (
        f"Hi {signup_request.admin_username},\n\n"
        f"Your signup needs changes before approval.\n\n"
        f"Reason: {signup_request.rejection_reason or 'Additional details are required.'}\n\n"
        f"Review and resubmit: {resubmit_url}\n\n"
        f"Thanks,\nSmart Library App"
    )
    return send_email(to_email=signup_request.admin_email, subject=subject, text=text)


def send_reset_link_email(admin: models.Admin, raw_token: str) -> bool:
    reset_url = f"{get_app_public_url()}/reset-password?token={raw_token}"
    subject = "Reset your Smart Library password"
    text = (
        f"Hi {admin.username},\n\n"
        f"Use the link below to reset your password:\n{reset_url}\n\n"
        f"If you did not request this, you can ignore this email."
    )
    return send_email(to_email=admin.email or "", subject=subject, text=text)


def send_reset_otp_email(admin: models.Admin, otp_code: str) -> bool:
    subject = "Your Smart Library reset code"
    text = (
        f"Hi {admin.username},\n\n"
        f"Your password reset code is: {otp_code}\n\n"
        f"This code will expire in {get_reset_otp_expiry_minutes()} minutes."
    )
    return send_email(to_email=admin.email or "", subject=subject, text=text)
