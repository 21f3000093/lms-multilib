# backend/app/auth.py
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app import crud, models, schemas
from app.auth_security import (
    APPROVED,
    EXPIRED,
    GOOGLE_ONBOARDING,
    PENDING_APPROVAL,
    PENDING_EMAIL_VERIFICATION,
    REJECTED,
    RESET_LINK,
    RESET_OTP,
    SIGNUP_RESUBMIT,
    SIGNUP_VERIFY,
    consume_token_by_value,
    create_signup_request,
    enforce_auth_protection,
    expire_signup_request_if_needed,
    evaluate_signup_review_reason,
    get_client_ip,
    get_google_client_id,
    get_google_onboarding_expiry_minutes,
    get_open_signup_request_by_email_or_username,
    get_reset_link_expiry_minutes,
    get_reset_otp_expiry_minutes,
    get_reset_otp_max_attempts,
    get_signup_activation_mode,
    get_signup_request_by_public_id,
    get_token_by_value,
    get_token_payload,
    get_verify_email_expiry_minutes,
    is_google_auth_enabled,
    get_turnstile_site_key,
    hash_raw_token,
    invalidate_tokens,
    is_turnstile_enabled,
    issue_auth_token,
    issue_otp_token,
    log_security_event,
    normalize_email,
    normalize_phone,
    normalize_username,
    record_auth_failure,
    record_auth_success,
    send_reset_link_email,
    send_reset_otp_email,
    send_signup_verification_email,
    suggest_username_from_google,
    utcnow,
    validate_admin_username,
    verify_google_credential,
)
from app.dependencies import (
    build_admin_jwt_subject,
    get_current_admin,
    get_db,
    get_subscription_trial_days,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


def _get_login_identifier(data: schemas.AdminLogin) -> str:
    return normalize_username(data.identifier or data.username or "")


def _load_admin_with_library(db: Session, admin_id: int):
    return (
        db.query(models.Admin)
        .options(joinedload(models.Admin.library))
        .filter(models.Admin.id == admin_id)
        .first()
    )


def _next_route_for_admin(admin: models.Admin | None) -> str:
    if not admin:
        return "/dashboard"
    return "/superadmin" if admin.role == "superadmin" else "/dashboard"


def _set_admin_login_cookie(Authorize: AuthJWT, admin_id: int) -> None:
    access_token = Authorize.create_access_token(subject=build_admin_jwt_subject(admin_id))  # type: ignore
    Authorize.set_access_cookies(access_token)


def _auth_action_with_admin(
    *,
    db: Session,
    admin_id: int,
    message: str,
    public_id: str | None = None,
    status: str | None = None,
    action: str = "logged_in",
) -> schemas.AuthActionResponse:
    loaded_admin = _load_admin_with_library(db, admin_id)
    return schemas.AuthActionResponse(
        ok=True,
        message=message,
        public_id=public_id,
        status=status,
        action=action,
        next_route=_next_route_for_admin(loaded_admin),
        admin=loaded_admin,
    )


def _google_scopes(request: Request, email: str) -> list[tuple[str, str]]:
    return [
        ("ip", get_client_ip(request)),
        ("email", normalize_email(email)),
    ]


def _signup_status_payload(signup_request: models.SignupRequest) -> schemas.SignupRequestStatusOut:
    return schemas.SignupRequestStatusOut(
        public_id=signup_request.public_id,
        status=signup_request.status,
        signup_method=signup_request.signup_method or "password",
        library_name=signup_request.library_name,
        contact_phone=signup_request.contact_phone,
        address=signup_request.address,
        admin_username=signup_request.admin_username,
        admin_email=signup_request.admin_email,
        max_seats=signup_request.max_seats,
        submitted_at=signup_request.submitted_at,
        verification_sent_at=signup_request.verification_sent_at,
        verified_at=signup_request.verified_at,
        approved_at=signup_request.approved_at,
        rejected_at=signup_request.rejected_at,
        rejection_reason=signup_request.rejection_reason,
        review_reason=signup_request.review_reason,
        expires_at=signup_request.expires_at,
    )


def _validate_new_passwords(new_password: str, confirm_password: str) -> None:
    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")


def _login_scopes(request: Request, identifier: str) -> list[tuple[str, str]]:
    return [
        ("ip", get_client_ip(request)),
        ("identifier", identifier.lower()),
    ]


def _signup_scopes(request: Request, email: str, username: str) -> list[tuple[str, str]]:
    return [
        ("ip", get_client_ip(request)),
        ("email", normalize_email(email)),
        ("identifier", normalize_username(username).lower()),
    ]


def _reset_scopes(request: Request, email: str) -> list[tuple[str, str]]:
    return [
        ("ip", get_client_ip(request)),
        ("email", normalize_email(email)),
    ]


def _activate_or_queue_signup(
    *,
    db: Session,
    signup_request: models.SignupRequest,
    request: Request,
    event_type: str,
    Authorize: AuthJWT | None = None,
):
    activation_mode = get_signup_activation_mode()
    scopes = _signup_scopes(request, signup_request.admin_email, signup_request.admin_username)
    review_reason: str | None = None

    if activation_mode == "manual":
        review_reason = "Manual review is enabled for new signups."
    elif activation_mode == "risk_based":
        review_reason = evaluate_signup_review_reason(
            db,
            signup_request=signup_request,
            scopes=scopes,
        )

    if review_reason:
        signup_request.status = PENDING_APPROVAL  # type: ignore
        signup_request.review_reason = review_reason  # type: ignore
        signup_request.expires_at = None  # type: ignore
        log_security_event(
            db,
            event_type=event_type,
            outcome="queued_for_review",
            ip_address=get_client_ip(request),
            identifier=signup_request.admin_username,
            target_email=signup_request.admin_email,
            signup_request_id=signup_request.id,
            metadata={"review_reason": review_reason, "activation_mode": activation_mode},
        )
        db.commit()
        return schemas.AuthActionResponse(
            ok=True,
            message="Email verified. Your signup has been flagged for manual review.",
            public_id=signup_request.public_id,
            status=signup_request.status,
            action="pending_approval",
            next_route=f"/signup/status/{signup_request.public_id}",
        )

    try:
        _, new_admin = crud.activate_signup_request(
            db,
            signup_request=signup_request,
            trial_days=get_subscription_trial_days(),
            approved_at=utcnow(),
        )
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc))

    log_security_event(
        db,
        event_type=event_type,
        outcome="auto_approved",
        ip_address=get_client_ip(request),
        identifier=signup_request.admin_username,
        target_email=signup_request.admin_email,
        signup_request_id=signup_request.id,
        admin_id=new_admin.id,
        metadata={"activation_mode": activation_mode, "library_id": new_admin.library_id},
    )
    db.commit()
    if Authorize is not None:
        _set_admin_login_cookie(Authorize, new_admin.id)
    return _auth_action_with_admin(
        db=db,
        admin_id=new_admin.id,
        message="Email verified and your workspace is ready.",
        public_id=signup_request.public_id,
        status=APPROVED,
    )


def _generic_reset_response(message: str) -> schemas.AuthActionResponse:
    return schemas.AuthActionResponse(ok=True, message=message)


@router.get("/turnstile/config", response_model=schemas.TurnstileConfigOut)
def get_turnstile_config():
    return {
        "enabled": is_turnstile_enabled(),
        "site_key": get_turnstile_site_key(),
    }


@router.get("/google/config", response_model=schemas.GoogleConfigOut)
def get_google_config():
    return {
        "enabled": is_google_auth_enabled(),
        "client_id": get_google_client_id(),
    }


@router.post("/login", response_model=schemas.AdminOut)
def login(
    data: schemas.AdminLogin,
    request: Request,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    identifier = _get_login_identifier(data)
    if not identifier:
        raise HTTPException(status_code=400, detail="username_or_email_required")

    scopes = _login_scopes(request, identifier)
    enforce_auth_protection(
        db,
        request=request,
        scopes=scopes,
        captcha_token=data.captcha_token,
        event_type="login",
        identifier=identifier,
    )

    admin = crud.authenticate_admin(db, identifier, data.password)
    if not admin:
        record_auth_failure(
            db,
            scopes=scopes,
            event_type="login",
            request=request,
            identifier=identifier,
        )
        raise HTTPException(status_code=401, detail="invalid_credentials")

    if admin.status != "active":  # type: ignore
        log_security_event(
            db,
            event_type="login",
            outcome="inactive_account",
            ip_address=get_client_ip(request),
            identifier=identifier,
            target_email=admin.email,
            admin_id=admin.id,
        )
        db.commit()
        raise HTTPException(status_code=403, detail="Your account is inactive")

    record_auth_success(db, scopes=scopes)
    _set_admin_login_cookie(Authorize, admin.id)

    loaded_admin = _load_admin_with_library(db, admin.id)
    if not loaded_admin:
        raise HTTPException(status_code=500, detail="Admin could not be loaded")
    return loaded_admin


@router.post("/signup", response_model=schemas.AuthActionResponse)
def signup(
    data: schemas.SelfServeSignupRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    library_name = normalize_username(data.library_name)
    admin_username = validate_admin_username(data.admin_username)
    admin_email = normalize_email(data.admin_email)
    contact_phone = normalize_phone(data.contact_phone)
    address = normalize_username(data.address or "") or None

    if not library_name:
        raise HTTPException(status_code=400, detail="Library name is required")
    if not admin_email:
        raise HTTPException(status_code=400, detail="Email is required")
    if not contact_phone:
        raise HTTPException(status_code=400, detail="Contact phone is required")
    _validate_new_passwords(data.password, data.confirm_password)

    scopes = _signup_scopes(request, admin_email, admin_username)
    enforce_auth_protection(
        db,
        request=request,
        scopes=scopes,
        captcha_token=data.captcha_token,
        event_type="signup",
        identifier=admin_username,
        target_email=admin_email,
    )

    if crud.get_admin_by_username(db, admin_username) or crud.get_admin_by_email(db, admin_email):
        record_auth_failure(
            db,
            scopes=scopes,
            event_type="signup",
            request=request,
            identifier=admin_username,
            target_email=admin_email,
            metadata={"reason": "duplicate_admin"},
        )
        raise HTTPException(status_code=409, detail="An account with that username or email already exists")

    existing_request = get_open_signup_request_by_email_or_username(
        db,
        normalized_email=admin_email,
        normalized_username=admin_username,
    )
    if existing_request:
        record_auth_failure(
            db,
            scopes=scopes,
            event_type="signup",
            request=request,
            identifier=admin_username,
            target_email=admin_email,
            signup_request_id=existing_request.id,
            metadata={"reason": "open_signup_request"},
        )
        raise HTTPException(status_code=409, detail="A signup request is already pending for that username or email")

    try:
        signup_request = create_signup_request(
            db,
            library_name=library_name,
            max_seats=data.max_seats,
            contact_phone=contact_phone,
            address=address,
            admin_username=admin_username,
            admin_email=admin_email,
            password_hash=crud.pwd_context.hash(data.password),
        )
        invalidate_tokens(db, purpose=SIGNUP_VERIFY, signup_request_id=signup_request.id)
        raw_token, _ = issue_auth_token(
            db,
            purpose=SIGNUP_VERIFY,
            target_email=admin_email,
            signup_request_id=signup_request.id,
            expires_minutes=get_verify_email_expiry_minutes(),
        )
        signup_request.verification_sent_at = utcnow()  # type: ignore
        signup_request.expires_at = utcnow() + timedelta(minutes=get_verify_email_expiry_minutes())  # type: ignore
        if not send_signup_verification_email(signup_request, raw_token):
            raise HTTPException(status_code=500, detail="Email delivery failed")
        log_security_event(
            db,
            event_type="signup",
            outcome="submitted",
            ip_address=get_client_ip(request),
            identifier=admin_username,
            target_email=admin_email,
            signup_request_id=signup_request.id,
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="A signup request already exists for that username or email")

    record_auth_success(db, scopes=scopes)
    return schemas.AuthActionResponse(
        ok=True,
        message="Signup submitted. Please verify your email to continue.",
        public_id=signup_request.public_id,
        status=signup_request.status,
        action="verify_email",
        next_route=f"/signup/status/{signup_request.public_id}",
    )


@router.post("/signup/verify-email", response_model=schemas.AuthActionResponse)
def verify_signup_email(
    payload: schemas.SignupVerifyRequest,
    request: Request,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    token = consume_token_by_value(db, purpose=SIGNUP_VERIFY, raw_token=payload.token)
    if not token or token.signup_request_id is None:
        raise HTTPException(
            status_code=400,
            detail={"code": "invalid_or_expired_token", "message": "Verification link is invalid or expired."},
        )

    signup_request = db.query(models.SignupRequest).filter(models.SignupRequest.id == token.signup_request_id).first()
    if not signup_request:
        raise HTTPException(status_code=404, detail="Signup request not found")

    expire_signup_request_if_needed(db, signup_request)
    if signup_request.status not in {PENDING_EMAIL_VERIFICATION, EXPIRED}:
        db.commit()
        return schemas.AuthActionResponse(
            ok=True,
            message="Email already verified.",
            public_id=signup_request.public_id,
            status=signup_request.status,
            action="status",
            next_route=f"/signup/status/{signup_request.public_id}",
        )

    signup_request.verified_at = utcnow()  # type: ignore
    signup_request.expires_at = None  # type: ignore
    signup_request.review_reason = None  # type: ignore
    invalidate_tokens(db, purpose=SIGNUP_VERIFY, signup_request_id=signup_request.id)
    return _activate_or_queue_signup(
        db=db,
        signup_request=signup_request,
        request=request,
        event_type="signup_verification",
        Authorize=Authorize,
    )


@router.post("/signup/resend-verification", response_model=schemas.AuthActionResponse)
def resend_signup_verification(
    payload: schemas.SignupResendVerificationRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    signup_request = get_signup_request_by_public_id(db, payload.public_id)
    if not signup_request:
        raise HTTPException(status_code=404, detail="Signup request not found")

    scopes = _signup_scopes(request, signup_request.admin_email, signup_request.admin_username)
    enforce_auth_protection(
        db,
        request=request,
        scopes=scopes,
        captcha_token=payload.captcha_token,
        event_type="signup_resend_verification",
        identifier=signup_request.admin_username,
        target_email=signup_request.admin_email,
        signup_request_id=signup_request.id,
    )

    if signup_request.status not in {PENDING_EMAIL_VERIFICATION, EXPIRED}:
        raise HTTPException(status_code=400, detail="Verification resend is only available before approval")

    invalidate_tokens(db, purpose=SIGNUP_VERIFY, signup_request_id=signup_request.id)
    raw_token, _ = issue_auth_token(
        db,
        purpose=SIGNUP_VERIFY,
        target_email=signup_request.admin_email,
        signup_request_id=signup_request.id,
        expires_minutes=get_verify_email_expiry_minutes(),
    )
    signup_request.status = PENDING_EMAIL_VERIFICATION  # type: ignore
    signup_request.verification_sent_at = utcnow()  # type: ignore
    signup_request.expires_at = utcnow() + timedelta(minutes=get_verify_email_expiry_minutes())  # type: ignore
    if not send_signup_verification_email(signup_request, raw_token):
        raise HTTPException(status_code=500, detail="Email delivery failed")

    log_security_event(
        db,
        event_type="signup_resend_verification",
        outcome="sent",
        ip_address=get_client_ip(request),
        identifier=signup_request.admin_username,
        target_email=signup_request.admin_email,
        signup_request_id=signup_request.id,
    )
    db.commit()
    record_auth_success(db, scopes=scopes)
    return schemas.AuthActionResponse(
        ok=True,
        message="A new verification email has been sent.",
        public_id=signup_request.public_id,
        status=signup_request.status,
        action="verify_email",
        next_route=f"/signup/status/{signup_request.public_id}",
    )


@router.get("/signup-requests/{public_id}", response_model=schemas.SignupRequestStatusOut)
def get_signup_request_status(public_id: str, db: Session = Depends(get_db)):
    signup_request = get_signup_request_by_public_id(db, public_id)
    if not signup_request:
        raise HTTPException(status_code=404, detail="Signup request not found")
    db.commit()
    return _signup_status_payload(signup_request)


@router.post("/signup/resubmit", response_model=schemas.AuthActionResponse)
def resubmit_signup_request(
    payload: schemas.SignupResubmitRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    token = consume_token_by_value(db, purpose=SIGNUP_RESUBMIT, raw_token=payload.token)
    if not token or token.signup_request_id is None:
        raise HTTPException(
            status_code=400,
            detail={"code": "invalid_or_expired_token", "message": "Resubmit link is invalid or expired."},
        )

    signup_request = db.query(models.SignupRequest).filter(models.SignupRequest.id == token.signup_request_id).first()
    if not signup_request:
        raise HTTPException(status_code=404, detail="Signup request not found")
    if signup_request.status != REJECTED:
        raise HTTPException(status_code=400, detail="Only rejected signup requests can be resubmitted")

    library_name = normalize_username(payload.library_name)
    admin_username = validate_admin_username(payload.admin_username)
    admin_email = normalize_email(payload.admin_email)
    contact_phone = normalize_phone(payload.contact_phone)
    address = normalize_username(payload.address or "") or None
    if not library_name or not admin_username or not admin_email or not contact_phone:
        raise HTTPException(status_code=400, detail="All required fields must be provided")
    if (signup_request.signup_method or "password") == "password":
        _validate_new_passwords(payload.password or "", payload.confirm_password or "")

    scopes = _signup_scopes(request, admin_email, admin_username)
    enforce_auth_protection(
        db,
        request=request,
        scopes=scopes,
        captcha_token=payload.captcha_token,
        event_type="signup_resubmit",
        identifier=admin_username,
        target_email=admin_email,
        signup_request_id=signup_request.id,
    )

    conflicting_admin = crud.get_admin_by_username(db, admin_username) or crud.get_admin_by_email(db, admin_email)
    if conflicting_admin:
        raise HTTPException(status_code=409, detail="An account with that username or email already exists")

    conflicting_request = get_open_signup_request_by_email_or_username(
        db,
        normalized_email=admin_email,
        normalized_username=admin_username,
    )
    if conflicting_request and conflicting_request.id != signup_request.id:
        raise HTTPException(status_code=409, detail="Another signup request is already pending for that username or email")

    signup_request.library_name = library_name  # type: ignore
    signup_request.max_seats = payload.max_seats  # type: ignore
    signup_request.contact_phone = contact_phone  # type: ignore
    signup_request.address = address  # type: ignore
    signup_request.admin_username = admin_username  # type: ignore
    signup_request.admin_email = admin_email  # type: ignore
    if (signup_request.signup_method or "password") == "password":
        signup_request.password_hash = crud.pwd_context.hash(payload.password or "")  # type: ignore
    signup_request.normalized_username = admin_username  # type: ignore
    signup_request.normalized_email = admin_email  # type: ignore
    signup_request.normalized_phone = contact_phone  # type: ignore
    signup_request.status = PENDING_EMAIL_VERIFICATION  # type: ignore
    signup_request.rejection_reason = None  # type: ignore
    signup_request.review_reason = None  # type: ignore
    signup_request.rejected_at = None  # type: ignore
    signup_request.verified_at = None  # type: ignore
    signup_request.verification_sent_at = utcnow()  # type: ignore
    signup_request.expires_at = utcnow() + timedelta(minutes=get_verify_email_expiry_minutes())  # type: ignore

    invalidate_tokens(db, purpose=SIGNUP_VERIFY, signup_request_id=signup_request.id)
    raw_verify_token, _ = issue_auth_token(
        db,
        purpose=SIGNUP_VERIFY,
        target_email=admin_email,
        signup_request_id=signup_request.id,
        expires_minutes=get_verify_email_expiry_minutes(),
    )
    if not send_signup_verification_email(signup_request, raw_verify_token):
        raise HTTPException(status_code=500, detail="Email delivery failed")

    log_security_event(
        db,
        event_type="signup_resubmit",
        outcome="submitted",
        ip_address=get_client_ip(request),
        identifier=admin_username,
        target_email=admin_email,
        signup_request_id=signup_request.id,
    )
    db.commit()
    record_auth_success(db, scopes=scopes)
    return schemas.AuthActionResponse(
        ok=True,
        message="Signup updated. Please verify your email again to continue.",
        public_id=signup_request.public_id,
        status=signup_request.status,
        action="verify_email",
        next_route=f"/signup/status/{signup_request.public_id}",
    )


@router.post("/google/exchange", response_model=schemas.AuthActionResponse)
def google_exchange(
    payload: schemas.GoogleExchangeRequest,
    request: Request,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    google_profile = verify_google_credential(payload.credential)
    email = google_profile["email"]
    scopes = _google_scopes(request, email)
    enforce_auth_protection(
        db,
        request=request,
        scopes=scopes,
        captcha_token=payload.captcha_token,
        event_type="google_exchange",
        target_email=email,
    )

    identity = crud.get_admin_auth_identity(
        db,
        provider="google",
        provider_subject=google_profile["provider_subject"],
    )
    if identity:
        linked_admin = _load_admin_with_library(db, identity.admin_id)
        if not linked_admin or linked_admin.status != "active":  # type: ignore
            raise HTTPException(status_code=403, detail="Your account is inactive")
        if not linked_admin.email_verified_at:
            linked_admin.email_verified_at = utcnow()  # type: ignore
        _set_admin_login_cookie(Authorize, linked_admin.id)
        log_security_event(
            db,
            event_type="google_exchange",
            outcome="logged_in",
            ip_address=get_client_ip(request),
            target_email=email,
            admin_id=linked_admin.id,
            metadata={"provider": "google", "intent": payload.intent},
        )
        db.commit()
        record_auth_success(db, scopes=scopes)
        return _auth_action_with_admin(
            db=db,
            admin_id=linked_admin.id,
            message="Signed in with Google successfully.",
            status=APPROVED,
        )

    existing_admin = crud.get_admin_by_email(db, email)
    if existing_admin:
        if existing_admin.status != "active":  # type: ignore
            raise HTTPException(status_code=403, detail="Your account is inactive")
        try:
            crud.link_admin_auth_identity(
                db,
                admin_id=existing_admin.id,
                provider="google",
                provider_subject=google_profile["provider_subject"],
                provider_email=email,
            )
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc))
        if not existing_admin.email_verified_at:
            existing_admin.email_verified_at = utcnow()  # type: ignore
        _set_admin_login_cookie(Authorize, existing_admin.id)
        log_security_event(
            db,
            event_type="google_exchange",
            outcome="auto_linked",
            ip_address=get_client_ip(request),
            target_email=email,
            admin_id=existing_admin.id,
            metadata={"provider": "google", "intent": payload.intent},
        )
        db.commit()
        record_auth_success(db, scopes=scopes)
        return _auth_action_with_admin(
            db=db,
            admin_id=existing_admin.id,
            message="Signed in with Google successfully.",
            status=APPROVED,
        )

    suggested_username = suggest_username_from_google(
        email=email,
        name=google_profile.get("given_name") or google_profile.get("name"),
    )
    invalidate_tokens(db, purpose=GOOGLE_ONBOARDING, target_email=email)
    onboarding_token, _ = issue_auth_token(
        db,
        purpose=GOOGLE_ONBOARDING,
        target_email=email,
        expires_minutes=get_google_onboarding_expiry_minutes(),
        payload={
            "provider": "google",
            "provider_subject": google_profile["provider_subject"],
            "email": email,
            "name": google_profile.get("name") or "",
            "suggested_username": suggested_username,
        },
    )
    log_security_event(
        db,
        event_type="google_exchange",
        outcome="signup_required" if payload.intent == "login" else "onboarding_started",
        ip_address=get_client_ip(request),
        target_email=email,
        metadata={"provider": "google", "intent": payload.intent},
    )
    db.commit()
    record_auth_success(db, scopes=scopes)
    action = "signup_required" if payload.intent == "login" else "complete_signup"
    return schemas.AuthActionResponse(
        ok=True,
        message="Complete a few library details to finish setting up your workspace.",
        status=PENDING_EMAIL_VERIFICATION,
        action=action,
        next_route="/signup?google=1",
        onboarding_token=onboarding_token,
        prefill_email=email,
        suggested_username=suggested_username,
        provider="google",
    )


@router.post("/google/complete-signup", response_model=schemas.AuthActionResponse)
def complete_google_signup(
    payload: schemas.GoogleCompleteSignupRequest,
    request: Request,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    library_name = normalize_username(payload.library_name)
    admin_username = validate_admin_username(payload.admin_username)
    contact_phone = normalize_phone(payload.contact_phone)
    address = normalize_username(payload.address or "") or None

    if not library_name:
        raise HTTPException(status_code=400, detail="Library name is required")
    if not contact_phone:
        raise HTTPException(status_code=400, detail="Contact phone is required")

    token = get_token_by_value(db, purpose=GOOGLE_ONBOARDING, raw_token=payload.onboarding_token)
    if not token:
        raise HTTPException(
            status_code=400,
            detail={"code": "invalid_or_expired_token", "message": "Google signup session is invalid or expired."},
        )

    token_payload = get_token_payload(token)
    admin_email = normalize_email(str(token_payload.get("email") or token.target_email or ""))
    provider_subject = str(token_payload.get("provider_subject") or "").strip()
    if not admin_email or not provider_subject:
        raise HTTPException(
            status_code=400,
            detail={"code": "invalid_or_expired_token", "message": "Google signup session is invalid or expired."},
        )

    scopes = _signup_scopes(request, admin_email, admin_username)
    enforce_auth_protection(
        db,
        request=request,
        scopes=scopes,
        captcha_token=payload.captcha_token,
        event_type="google_complete_signup",
        identifier=admin_username,
        target_email=admin_email,
    )

    if crud.get_admin_by_username(db, admin_username) or crud.get_admin_by_email(db, admin_email):
        record_auth_failure(
            db,
            scopes=scopes,
            event_type="google_complete_signup",
            request=request,
            identifier=admin_username,
            target_email=admin_email,
            metadata={"reason": "duplicate_admin"},
        )
        raise HTTPException(status_code=409, detail="An account with that username or email already exists")

    existing_request = get_open_signup_request_by_email_or_username(
        db,
        normalized_email=admin_email,
        normalized_username=admin_username,
    )
    if existing_request:
        record_auth_failure(
            db,
            scopes=scopes,
            event_type="google_complete_signup",
            request=request,
            identifier=admin_username,
            target_email=admin_email,
            signup_request_id=existing_request.id,
            metadata={"reason": "open_signup_request"},
        )
        raise HTTPException(status_code=409, detail="A signup request is already pending for that username or email")

    signup_request = create_signup_request(
        db,
        library_name=library_name,
        max_seats=payload.max_seats,
        contact_phone=contact_phone,
        address=address,
        admin_username=admin_username,
        admin_email=admin_email,
        password_hash=crud.generate_unusable_password_hash(),
        signup_method="google",
        provider="google",
        provider_subject=provider_subject,
    )
    signup_request.verified_at = utcnow()  # type: ignore
    signup_request.verification_sent_at = signup_request.verified_at  # type: ignore
    signup_request.expires_at = None  # type: ignore
    token.consumed_at = utcnow()  # type: ignore
    invalidate_tokens(db, purpose=GOOGLE_ONBOARDING, target_email=admin_email)

    response = _activate_or_queue_signup(
        db=db,
        signup_request=signup_request,
        request=request,
        event_type="google_complete_signup",
        Authorize=Authorize,
    )
    record_auth_success(db, scopes=scopes)
    return response


@router.post("/password-reset/request-link", response_model=schemas.AuthActionResponse)
def request_password_reset_link(
    payload: schemas.ForgotPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    email = normalize_email(payload.email)
    scopes = _reset_scopes(request, email)
    enforce_auth_protection(
        db,
        request=request,
        scopes=scopes,
        captcha_token=payload.captcha_token,
        event_type="password_reset_request_link",
        target_email=email,
    )

    admin = crud.get_admin_by_email(db, email)
    if admin and admin.email_verified_at:
        invalidate_tokens(db, purpose=RESET_LINK, admin_id=admin.id)
        raw_token, _ = issue_auth_token(
            db,
            purpose=RESET_LINK,
            target_email=email,
            admin_id=admin.id,
            expires_minutes=get_reset_link_expiry_minutes(),
        )
        send_reset_link_email(admin, raw_token)
        log_security_event(
            db,
            event_type="password_reset_request_link",
            outcome="sent",
            ip_address=get_client_ip(request),
            target_email=email,
            admin_id=admin.id,
        )
        db.commit()
        record_auth_success(db, scopes=scopes)
    else:
        record_auth_failure(
            db,
            scopes=scopes,
            event_type="password_reset_request_link",
            request=request,
            target_email=email,
            metadata={"reason": "unknown_or_unverified_email"},
        )
    return _generic_reset_response("If that email is eligible, a password reset link has been sent.")


@router.post("/password-reset/request-otp", response_model=schemas.AuthActionResponse)
def request_password_reset_otp(
    payload: schemas.ForgotPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    email = normalize_email(payload.email)
    scopes = _reset_scopes(request, email)
    enforce_auth_protection(
        db,
        request=request,
        scopes=scopes,
        captcha_token=payload.captcha_token,
        event_type="password_reset_request_otp",
        target_email=email,
    )

    admin = crud.get_admin_by_email(db, email)
    if admin and admin.email_verified_at:
        invalidate_tokens(db, purpose=RESET_OTP, admin_id=admin.id)
        raw_otp, _ = issue_otp_token(
            db,
            target_email=email,
            admin_id=admin.id,
            expires_minutes=get_reset_otp_expiry_minutes(),
            max_attempts=get_reset_otp_max_attempts(),
        )
        send_reset_otp_email(admin, raw_otp)
        log_security_event(
            db,
            event_type="password_reset_request_otp",
            outcome="sent",
            ip_address=get_client_ip(request),
            target_email=email,
            admin_id=admin.id,
        )
        db.commit()
        record_auth_success(db, scopes=scopes)
    else:
        record_auth_failure(
            db,
            scopes=scopes,
            event_type="password_reset_request_otp",
            request=request,
            target_email=email,
            metadata={"reason": "unknown_or_unverified_email"},
        )
    return _generic_reset_response("If that email is eligible, a password reset code has been sent.")


@router.post("/password-reset/confirm-link", response_model=schemas.AuthActionResponse)
def confirm_password_reset_link(
    payload: schemas.PasswordResetConfirmLinkRequest,
    db: Session = Depends(get_db),
):
    _validate_new_passwords(payload.new_password, payload.confirm_password)
    token = consume_token_by_value(db, purpose=RESET_LINK, raw_token=payload.token)
    if not token or token.admin_id is None:
        raise HTTPException(
            status_code=400,
            detail={"code": "invalid_or_expired_token", "message": "Reset link is invalid or expired."},
        )

    admin = crud.get_admin(db, token.admin_id)
    if not admin or not admin.email_verified_at:
        raise HTTPException(
            status_code=400,
            detail={"code": "email_not_verified", "message": "Password reset is only available for verified email accounts."},
        )

    admin.password = crud.pwd_context.hash(payload.new_password)  # type: ignore
    invalidate_tokens(db, purpose=RESET_LINK, admin_id=admin.id)
    invalidate_tokens(db, purpose=RESET_OTP, admin_id=admin.id)
    db.commit()
    return schemas.AuthActionResponse(ok=True, message="Password reset successful. You can now log in.")


@router.post("/password-reset/confirm-otp", response_model=schemas.AuthActionResponse)
def confirm_password_reset_otp(
    payload: schemas.PasswordResetConfirmOtpRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    email = normalize_email(payload.email)
    _validate_new_passwords(payload.new_password, payload.confirm_password)
    scopes = _reset_scopes(request, email)
    enforce_auth_protection(
        db,
        request=request,
        scopes=scopes,
        captcha_token=payload.captcha_token,
        event_type="password_reset_confirm_otp",
        target_email=email,
    )

    token = (
        db.query(models.AuthActionToken)
        .filter(models.AuthActionToken.purpose == RESET_OTP)
        .filter(models.AuthActionToken.target_email == email)
        .filter(models.AuthActionToken.consumed_at.is_(None))
        .filter(models.AuthActionToken.expires_at > utcnow())
        .order_by(models.AuthActionToken.created_at.desc())
        .first()
    )
    if not token or token.admin_id is None:
        record_auth_failure(
            db,
            scopes=scopes,
            event_type="password_reset_confirm_otp",
            request=request,
            target_email=email,
            metadata={"reason": "missing_token"},
        )
        raise HTTPException(
            status_code=400,
            detail={"code": "invalid_or_expired_token", "message": "Reset code is invalid or expired."},
        )

    if hash_raw_token(payload.otp) != token.token_hash:
        token.attempt_count = int(token.attempt_count or 0) + 1  # type: ignore
        if token.attempt_count >= token.max_attempts:  # type: ignore
            token.consumed_at = utcnow()  # type: ignore
        record_auth_failure(
            db,
            scopes=scopes,
            event_type="password_reset_confirm_otp",
            request=request,
            target_email=email,
            admin_id=token.admin_id,
            metadata={"reason": "invalid_otp", "attempt_count": token.attempt_count},
        )
        raise HTTPException(
            status_code=400,
            detail={"code": "invalid_or_expired_token", "message": "Reset code is invalid or expired."},
        )

    admin = crud.get_admin(db, token.admin_id)
    if not admin or not admin.email_verified_at:
        raise HTTPException(
            status_code=400,
            detail={"code": "email_not_verified", "message": "Password reset is only available for verified email accounts."},
        )

    token.consumed_at = utcnow()  # type: ignore
    admin.password = crud.pwd_context.hash(payload.new_password)  # type: ignore
    invalidate_tokens(db, purpose=RESET_LINK, admin_id=admin.id)
    invalidate_tokens(db, purpose=RESET_OTP, admin_id=admin.id)
    db.commit()
    record_auth_success(db, scopes=scopes)
    return schemas.AuthActionResponse(ok=True, message="Password reset successful. You can now log in.")


@router.post("/logout")
def logout(Authorize: AuthJWT = Depends()):
    Authorize.unset_jwt_cookies()
    return {"msg": "Logged out"}


@router.put("/change-password")
def change_password(
    data: schemas.AdminChangePassword,
    db: Session = Depends(get_db),
    admin = Depends(get_current_admin),
):
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="New passwords do not match")

    if data.current_password == data.new_password:
        raise HTTPException(status_code=400, detail="New password must be different from current password")

    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="New password must be at least 6 characters long")

    result = crud.change_admin_password(db, admin.id, data.current_password, data.new_password)

    if result is None:
        raise HTTPException(status_code=404, detail="Admin not found")
    elif result is False:
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    return {"message": "Password changed successfully"}
