# Backend (FastAPI) - Smart Library App

## Purpose

This backend provides:

- Cookie-based authentication and role authorization.
- Multi-tenant library data isolation (`library_id` scoped).
- Student, seat, payments, expenses, reminders, and receipt APIs.
- Superadmin control panel APIs for libraries/admins.
- Notification center APIs (in-app + web push subscription/delivery).

## Stack

- FastAPI
- SQLAlchemy ORM
- Alembic migrations
- PostgreSQL (`psycopg2-binary`)
- `fastapi-jwt-auth` for HttpOnly cookie JWT auth
- `pywebpush` for Web Push notification delivery

## Local Run

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Docs endpoints:

- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Environment Variables

Core:

- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `SUPERADMIN_USERNAME`
- `SUPERADMIN_PASSWORD`
- `ALLOWED_ORIGINS`

Receipt sharing:

- `RECEIPT_SHARE_SECRET`
- `RECEIPT_SHARE_EXPIRES_HOURS`
- `PUBLIC_RECEIPT_BASE_URL`

Push notifications:

- `PUSH_VAPID_PUBLIC_KEY`
- `PUSH_VAPID_PRIVATE_KEY`
- `PUSH_VAPID_SUBJECT`

Subscriptions:

- `SUBSCRIPTION_TRIAL_DAYS`: number of free trial days for new libraries. Set to `0` to disable trials.
- `SUBSCRIPTION_GRACE_DAYS`: number of post-expiry grace days. Set to `0` to expire immediately after `valid_until`.
- `SUBSCRIPTION_ENFORCEMENT_MODE`: use `enforce` to block expired libraries, or `monitor` to log only.

## App Structure

- `main.py`: app bootstrap, middleware, startup bootstrap, main feature endpoints.
- `app/auth.py`: login/logout/change-password.
- `app/dependencies.py`: DB session and current-admin resolver.
- `app/crud.py`: business rules and DB mutations.
- `app/seats.py`: seat-map endpoints.
- `app/superadmin.py`: superadmin admin/library management.
- `app/notifications.py`: in-app notifications + push subscriptions + push dispatch.
- `app/whatsapp_reminder.py`: pending fee reminder data.
- `app/models.py`: SQLAlchemy entities.
- `app/schemas.py`: request/response DTOs.

## Request and Security Flow

1. Client calls auth endpoint (`/auth/login`) with credentials.
2. Backend issues access token into HttpOnly cookie.
3. Protected routes call `get_current_admin`.
4. Role checks are enforced per endpoint.
5. Tenant isolation is enforced using `admin.library_id` in queries and mutations.

Important: frontend `localStorage` role checks are UX-only. Real security is backend enforcement.

## API Surface (Grouped)

### Auth

- `POST /auth/login`
- `POST /auth/logout`
- `PUT /auth/change-password`

### Student Management

- `POST /students/`
- `GET /students/`
- `GET /students/{student_id}`
- `PUT /students/{student_id}`
- `PUT /students/{student_id}/mark-left`
- `DELETE /students/{student_id}`

### Seat Management

- `GET /available-seats`
- `GET /seats/view`
- `GET /seats/{seat_number}/details`

### Dashboard

- `GET /dashboard/`

### Payments and Receipts

- `POST /generate-monthly-payments/{month}`
- `GET /monthly-payments/{month}`
- `PUT /monthly-payments/{payment_id}`
- `PUT /monthly-payments/toggle/{payment_id}`
- `DELETE /monthly-payments/{payment_id}`
- `GET /monthly-payments/single/{payment_id}`
- `GET /students/{student_id}/payments`
- `POST /students/{student_id}/payments/bulk`
- `GET /export-monthly-payments/{month}`
- `GET /monthly-payments/{payment_id}/share-link`
- `GET /public-receipts/{token}`

### Expenses

- `POST /monthly-expenses/`
- `GET /monthly-expenses/{month}`
- `DELETE /monthly-expenses/{expense_id}`

### Reminders

- `GET /reminders/pending-fees`
- `GET /reminders/pending-fees/{month}`

### Superadmin

- `GET /superadmin/libraries`
- `POST /superadmin/libraries`
- `GET /superadmin/libraries/{library_id}`
- `GET /superadmin/libraries/{library_id}/students`
- `GET /superadmin/admins`
- `POST /superadmin/admins`
- `PATCH /superadmin/admins/{admin_id}/status`
- `DELETE /superadmin/admins/{admin_id}`

### Notifications (In-App + Push)

- `POST /notifications/` (superadmin broadcast)
- `GET /notifications/sent` (superadmin)
- `GET /notifications/inbox` (admin)
- `GET /notifications/inbox/unread-count` (admin)
- `PATCH /notifications/inbox/{notification_id}/read` (admin)
- `PATCH /notifications/inbox/read-all` (admin)

Push subscription and delivery:

- `GET /notifications/push/config`
- `POST /notifications/push/subscriptions`
- `POST /notifications/push/subscriptions/unsubscribe`

## Data Model Summary

Core:

- `libraries`
- `admins`
- `students`
- `seats`
- `monthly_payments`
- `monthly_expenses`
- `subscriptions`

Notifications:

- `notifications`
- `notification_recipients`
- `push_subscriptions`

## Migrations

Alembic assets:

- Config: `alembic.ini`
- Env: `alembic/env.py`
- Revisions: `alembic/versions/`

Common commands:

```bash
cd backend
alembic current
alembic history
alembic upgrade head
alembic downgrade -1
```

Create new revision:

```bash
alembic revision -m "describe_change"
```

## Operational Notes

- Startup currently bootstraps superadmin and demo admin if missing.
- CORS allowlist is currently hardcoded in `main.py`; keep env and code aligned.
- Push delivery is best-effort: expired endpoints are cleaned on 404/410 responses.
- Public receipt links are signed and time-bound.

## Troubleshooting

- `python-dotenv could not parse statement`: remove spaces around `=` in `.env`.
- `DuplicateTable` during migration: DB schema and alembic revision are out of sync. Align with `alembic stamp ...` only after verifying schema state.
- Push not delivered:
  - verify VAPID env vars are set in production backend
  - verify subscription exists in `push_subscriptions`
  - verify browser permission is granted
  - verify service worker is active in deployed frontend
