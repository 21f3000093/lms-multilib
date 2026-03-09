# Smart Library App (LMS MultiLib)

Multi-tenant library management platform with role-based access for library admins and superadmin.

## What This App Does

- Manages student registration and seat assignment by shift.
- Generates and tracks monthly payments.
- Tracks monthly expenses.
- Supports WhatsApp reminder workflows for pending fees.
- Supports in-app notification center and web push notifications.
- Supports public receipt links for paid payments.
- Supports superadmin management of libraries and admin accounts.

## Tech Stack

- Backend: FastAPI, SQLAlchemy, Alembic, PostgreSQL, cookie-based JWT auth.
- Frontend: Vue 3, Vue Router, Axios, Vue CLI PWA plugin.
- Infrastructure: Railway (backend/database), Vercel (frontend).

## Architecture At a Glance

```text
Browser (Vue PWA)
  -> Axios (withCredentials cookies)
  -> FastAPI (role + tenant checks)
  -> PostgreSQL (multi-tenant data by library_id)

Superadmin Notifications
  -> In-app notifications persisted in DB
  -> Optional Web Push broadcast to subscribed admin devices

Receipt Sharing
  -> Short signed token URL
  -> Public receipt page (read-only)
```

## Repository Structure

```text
backend/
  app/
    auth.py               # auth endpoints (login/logout/change-password)
    crud.py               # core business logic
    dependencies.py       # DB session + authenticated admin resolver
    models.py             # SQLAlchemy models
    notifications.py      # notification center + push subscription APIs
    schemas.py            # Pydantic contracts
    seats.py              # seat map APIs
    superadmin.py         # superadmin-only APIs
    whatsapp_reminder.py  # pending fee reminders
  alembic/                # migration environment + revisions
  main.py                 # app creation + primary feature routes

frontend/
  public/
    sw-push.js            # push event + notification click handlers
  src/
    api.js                # axios client + global error handling
    router/index.js       # route definitions + role guard
    utils/pushNotifications.js
    components/           # feature modules
    views/                # route-level pages
  vue.config.js           # PWA/workbox config
```

## Local Development Quick Start

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs:
- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 2) Frontend

```bash
cd frontend
npm install
npm run serve
```

Default dev URL: `http://localhost:8080`

## Configuration

Primary backend environment variables (see `backend/.env.example`):

- `DATABASE_URL`: PostgreSQL connection string.
- `JWT_SECRET_KEY`: JWT signing secret (required).
- `SUPERADMIN_USERNAME`: startup bootstrap username.
- `SUPERADMIN_PASSWORD`: startup bootstrap password.
- `ALLOWED_ORIGINS`: comma-separated allowed origins (note: CORS list is currently hardcoded in `backend/main.py`).
- `RECEIPT_SHARE_SECRET`: signing secret for public receipt links.
- `RECEIPT_SHARE_EXPIRES_HOURS`: receipt token expiry.
- `PUBLIC_RECEIPT_BASE_URL`: base URL used for share-link generation.
- `PUSH_VAPID_PUBLIC_KEY`: web push public key.
- `PUSH_VAPID_PRIVATE_KEY`: web push private key.
- `PUSH_VAPID_SUBJECT`: VAPID subject, usually `mailto:...`.

## Auth and Multi-Tenancy Model

- Auth uses HttpOnly JWT cookies (`fastapi-jwt-auth`).
- Frontend stores role metadata in `localStorage` for UX route checks.
- Backend is the source of truth for authorization.
- Most resource access is scoped by `admin.library_id` to isolate tenants.
- Roles:
  - `admin`: manages one library.
  - `superadmin`: platform-wide management + broadcast messaging.

## Core Feature Flows

### Student and Seat Management

- Create/update student with shift selection.
- Validate seat occupancy per shift.
- Mark student as left (`left_at` tracked, seat assignments cleared).

### Monthly Billing

- Generate monthly payment records.
- Toggle paid/unpaid status.
- Bulk add payments per student for multiple months.
- Export CSV by month.

### Notifications

- Superadmin sends notifications to all admins, a specific library, or specific admins.
- Admins view inbox and mark read.
- Push subscriptions are linked to admin user/device.
- Push notifications can deep-link into app routes.

### Receipt Sharing

- Paid payment can generate signed public receipt link.
- Public endpoint validates token and returns read-only receipt payload.

## API Overview

This repository now has detailed backend API documentation in `backend/README.md` and frontend route/flow documentation in `frontend/README.md`.

## Database and Migrations

- Migration tool: Alembic.
- Current migrations include notifications, payment billing windows, `students.left_at`, and push subscriptions.
- Always apply schema changes with migration scripts:

```bash
cd backend
alembic upgrade head
```

## Deployment Notes (Railway + Vercel)

- Backend deploy target: Railway.
- Frontend deploy target: Vercel.
- Ensure `API baseURL` in `frontend/src/api.js` points to production backend before build/deploy.
- Ensure cookie/CORS/domain settings are aligned with production domains.
- For push notifications, configure VAPID env vars in backend environment.

## Documentation Strategy (Recommended)

Yes, use Docs-as-Code.

Recommended setup:

- Keep architecture/runbooks/versioning in Git with code.
- Treat docs changes as part of feature PRs.
- Add a `docs/` folder for long-form docs:
  - `docs/architecture.md`
  - `docs/api-contracts.md`
  - `docs/deployment.md`
  - `docs/runbook.md`
  - `docs/security.md`
- Enforce a PR checklist item: "Docs updated?" for any behavior/API/schema change.
- Add changelog entries for user-facing updates.

## Contribution Guidelines

- Prefer Alembic migrations over ad-hoc schema updates.
- Enforce tenant checks in backend for all data reads/writes.
- Keep auth enforcement server-side.
- Add tests for authorization boundaries and data integrity paths.
