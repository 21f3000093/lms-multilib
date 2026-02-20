# Backend (FastAPI)

## Stack

- FastAPI
- SQLAlchemy ORM
- Alembic migrations
- `fastapi-jwt-auth` for cookie-based JWT authentication
- PostgreSQL (via `psycopg2-binary`)

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

## Environment Variables

- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `SUPERADMIN_USERNAME`
- `SUPERADMIN_PASSWORD`
- `ALLOWED_ORIGINS`

## Request Flow

1. `main.py` registers routers and middleware.
2. Auth endpoints issue JWT in HttpOnly cookies.
3. Protected routes use `get_current_admin` from `app/dependencies.py`.
4. Business logic is implemented in `app/crud.py`.

## Modules

- `app/auth.py`: login/logout/password change
- `app/seats.py`: seat map and seat occupancy details
- `app/superadmin.py`: library/admin management by superadmin
- `app/whatsapp_reminder.py`: unpaid fee reminder data
- `app/models.py`: DB schema
- `app/schemas.py`: API contracts
- `app/crud.py`: reusable DB operations

## Migrations

- Alembic config: `alembic.ini`
- Revision scripts: `alembic/versions/`

Create migration:

```bash
alembic revision -m "describe change"
```

Apply migration:

```bash
alembic upgrade head
```
