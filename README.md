# Smart Library App

Smart Library App is a multi-tenant SaaS/PWA for study libraries and reading rooms. It helps library owners manage student admissions, seat allocation by shift, monthly fee records, reminders, receipts, expenses, analytics, subscriptions, and platform-level superadmin workflows.

The repository contains a Vue 3 frontend and a FastAPI backend backed by PostgreSQL.

## Highlights

- Multi-library tenancy with backend-enforced `library_id` isolation.
- Admin and superadmin roles with HttpOnly JWT cookie authentication.
- Student registration, searchable student list, student profile, and left-student tracking.
- Seat map with shift-wise occupancy for morning, afternoon, and evening shifts.
- Monthly fee generation, paid/unpaid toggles, bulk advance-month records, CSV export, and public receipt links.
- WhatsApp, SMS, and call reminder workflows using device/browser deep links.
- Dashboard analytics for occupancy, collections, student movement, and quick insights.
- SaaS subscription billing with Razorpay checkout and superadmin plan/subscription management.
- In-app notification center and optional web push notifications.
- PWA support with Workbox service worker caching for static app assets.

## Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend | Vue 3, Vue Router, Axios, Vue CLI PWA plugin, Lucide icons |
| Backend | FastAPI, SQLAlchemy, Alembic, Pydantic, `fastapi-jwt-auth` |
| Database | PostgreSQL |
| Billing | Razorpay checkout and webhooks |
| Email/Auth helpers | Resend email, Google OAuth, Cloudflare Turnstile |
| Notifications | In-app DB notifications, optional Web Push/VAPID |
| Deployment targets | Vercel/static host for frontend, Railway/FastAPI host for backend |

## Repository Layout

```text
backend/
  app/                 FastAPI feature modules, models, schemas, auth, billing
  alembic/             Database migrations
  main.py              App bootstrap and primary route registration

frontend/
  public/              PWA assets, icons, screenshots, service-worker helper
  src/
    components/        Feature modules and admin/superadmin screens
    views/             Public/auth route-level views
    router/            Vue Router route map and guards
    styles/            Theme tokens
    utils/             Auth/session, theme, push helpers

docs/                  Architecture, setup, deployment, security, roadmap docs
```

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

FastAPI docs:

- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run serve
```

Default frontend URL: `http://localhost:8080`

## Configuration

Backend configuration is documented in [backend/.env.example](backend/.env.example). Frontend configuration is documented in [frontend/.env.example](frontend/.env.example).

Important production settings:

- `JWT_SECRET_KEY` must be a strong random secret.
- `ALLOWED_ORIGINS` must include only trusted frontend origins.
- `AUTHJWT_COOKIE_DOMAIN`, `AUTHJWT_COOKIE_SAMESITE`, and HTTPS settings must match your deployment.
- `SUBSCRIPTION_ENFORCEMENT_MODE=enforce` is required to block expired subscriptions.
- Do not commit real `.env` files, database dumps, private keys, or production credentials.

## Documentation

- [Development Guide](docs/development.md)
- [Architecture](docs/architecture.md)
- [Deployment Guide](docs/deployment.md)
- [Security Audit Notes](docs/security-audit.md)
- [Open Source Readiness Checklist](docs/open-source-checklist.md)
- [Student Photo Feature Plan](docs/student-photo-feature-plan.md)
- [Contributing Guide](CONTRIBUTING.md)
- [Security Policy](SECURITY.md)

## Current Open-Source Status

This project is close to being publishable, but do not announce it publicly until the items in [Open Source Readiness Checklist](docs/open-source-checklist.md) are complete. The most important blockers are dependency audit remediation, Python dependency audit setup, removal/rotation of any credentials that may have existed outside tracked files, and a final review of public branding/contact details.

## Security

Please do not open public issues for suspected vulnerabilities. Follow [SECURITY.md](SECURITY.md).

## License

Apache License 2.0. See [LICENSE](LICENSE).
