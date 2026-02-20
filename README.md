# LMS MultiLib

Multi-tenant Library Management System with:
- `backend/`: FastAPI + SQLAlchemy + Alembic
- `frontend/`: Vue 3 + Vue Router + Axios

## Overview

This project manages:
- student registrations and seat allocation by shift
- monthly fee generation and payment tracking
- monthly expense tracking
- superadmin management for libraries and admin accounts

Authentication is cookie-based JWT (`fastapi-jwt-auth`) with role-aware access (`admin`, `superadmin`).

## Repository Structure

```text
backend/
  app/
    auth.py              # login/logout/change-password endpoints
    crud.py              # core business logic
    dependencies.py      # DB session + current admin dependency
    models.py            # SQLAlchemy models
    schemas.py           # Pydantic request/response schemas
    seats.py             # seat map APIs
    superadmin.py        # superadmin APIs
    whatsapp_reminder.py # fee reminder APIs
  alembic/               # DB migrations
  main.py                # FastAPI app + API routes

frontend/
  src/
    api.js               # Axios instance + global error interceptor
    router/index.js      # route map + auth guard
    components/          # dashboard and feature components
    views/               # page-level route views
```

## Backend Setup

1. Create virtual environment and install dependencies:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Create env file:

```bash
cp .env.example .env
```

3. Run migrations (recommended):

```bash
alembic upgrade head
```

4. Start API:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Frontend Setup

```bash
cd frontend
npm install
npm run serve
```

Default dev URL is usually `http://localhost:8080`.

## Configuration

Backend environment variables (see `backend/.env.example`):
- `DATABASE_URL`: SQLAlchemy DB URL
- `JWT_SECRET_KEY`: JWT signing key
- `SUPERADMIN_USERNAME`: bootstrap superadmin username
- `SUPERADMIN_PASSWORD`: bootstrap superadmin password
- `ALLOWED_ORIGINS`: optional comma-separated origins (currently not fully wired in middleware)

## API Surface (High-Level)

Auth:
- `POST /auth/login`
- `POST /auth/logout`
- `PUT /auth/change-password`

Students:
- `POST /students/`
- `GET /students/`
- `GET /students/{student_id}`
- `PUT /students/{student_id}`
- `PUT /students/{student_id}/mark-left`
- `DELETE /students/{student_id}`

Seats:
- `GET /available-seats`
- `GET /seats/view`
- `GET /seats/{seat_number}/details`

Payments:
- `POST /generate-monthly-payments/{month}`
- `GET /monthly-payments/{month}`
- `PUT /monthly-payments/{payment_id}`
- `PUT /monthly-payments/toggle/{payment_id}`
- `DELETE /monthly-payments/{payment_id}`
- `GET /monthly-payments/single/{payment_id}`
- `GET /students/{student_id}/payments`
- `GET /export-monthly-payments/{month}`

Expenses:
- `POST /monthly-expenses/`
- `GET /monthly-expenses/{month}`
- `DELETE /monthly-expenses/{expense_id}`

Superadmin:
- `/superadmin/libraries*`
- `/superadmin/admins*`

Reminders:
- `GET /reminders/pending-fees`
- `GET /reminders/pending-fees/{month}`

## Notes for Contributors

- Prefer migrations over `Base.metadata.create_all` for schema lifecycle.
- Keep authorization checks scoped to `library_id` for all tenant data reads/writes.
- Do not rely on frontend local storage for security decisions; enforce on backend.
- Add tests for authz boundaries, seat assignment integrity, and payment ownership.
