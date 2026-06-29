# Security Policy

## Supported Versions

This repository is currently pre-1.0. Security fixes should target the default branch unless a stable release branch is created later.

## Reporting Vulnerabilities

Please do not report vulnerabilities in public GitHub issues.

Use a private channel controlled by the project maintainer. Until a dedicated security email is configured, use:

```text
support@smartlibraryapp.in
```

Include:

- Affected component or endpoint.
- Steps to reproduce.
- Expected vs actual impact.
- Whether real user data or credentials may be involved.
- Suggested remediation, if known.

## Security Boundaries

- Backend authorization is authoritative.
- Frontend route guards and localStorage role values are UX hints only.
- Admin-scoped data must always be filtered by authenticated `library_id`.
- Superadmin APIs must require the `superadmin` role.
- Auth uses HttpOnly JWT cookies with `withCredentials` from the frontend.
- Public receipt links are signed and time-bound.

## Sensitive Data Rules

Never commit:

- `.env` files with real values.
- Database dumps or exported customer records.
- Private keys, VAPID private keys, OAuth client secrets, Razorpay secrets, Resend API keys, or JWT secrets.
- Screenshots containing real student, admin, payment, phone, or email data.

## Current Known Security Work

See [docs/security-audit.md](docs/security-audit.md). The project should not be announced as production-grade open source until those items are triaged.
