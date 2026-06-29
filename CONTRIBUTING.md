# Contributing to Smart Library App

Thanks for your interest in contributing. This project is a full-stack SaaS app, so good contributions should preserve tenant isolation, auth boundaries, and mobile-first UX.

## Before You Start

1. Read [README.md](README.md).
2. Set up the project using [docs/development.md](docs/development.md).
3. Review [docs/architecture.md](docs/architecture.md) for data flow and ownership boundaries.
4. Check [docs/security-audit.md](docs/security-audit.md) before changing dependencies or auth/payment code.

## Development Rules

- Keep backend authorization server-side. Frontend route guards are UX only.
- Scope all library data reads/writes by authenticated `admin.library_id`.
- Use Alembic migrations for schema changes.
- Do not commit real `.env` files, database dumps, private keys, screenshots containing real user data, or production credentials.
- Keep UI changes consistent with existing theme tokens in `frontend/src/styles/theme.css`.
- Prefer small, focused pull requests.

## Branch and Commit Style

Use concise Conventional Commit-style messages:

```text
feat(students): add photo upload metadata
fix(auth): validate signup username format
docs: add deployment guide
chore(deps): update axios
```

## Local Checks

Run these before opening a pull request:

```bash
cd frontend
npm run lint -- --no-fix
npm run build
```

```bash
cd backend
python -m py_compile main.py app/*.py
alembic upgrade head
```

For dependency/security work, also run:

```bash
cd frontend
npm audit
```

Python dependency auditing is not currently wired into the repo. Before publishing or merging dependency updates, run `pip-audit -r backend/requirements.txt` in an environment where `pip-audit` is installed.

## Pull Request Checklist

- The PR has a clear problem statement and summary.
- Tests/build/lint were run, or the reason they were not run is documented.
- Database changes include an Alembic migration.
- New env vars are added to the relevant `.env.example`.
- New behavior is documented when it affects setup, deployment, security, or public APIs.
- Screenshots are included for meaningful UI changes.

## Areas That Need Help

- Dependency modernization away from legacy Vue CLI tooling.
- Automated backend tests for tenant isolation and subscription enforcement.
- Student photo upload feature.
- End-to-end tests for admin and superadmin workflows.
- Security headers, CSRF posture review, and production hardening.
