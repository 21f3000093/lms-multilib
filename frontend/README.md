# Frontend (Vue 3) - Smart Library App

## Purpose

This frontend is a Vue 3 web app + PWA shell for:

- Admin and superadmin login.
- Dashboard, student, seat, payments, expenses, reminders, and receipts.
- Notification center (in-app) and push subscription setup.
- Mobile-first navigation with responsive desktop/sidebar layouts.

## Stack

- Vue 3
- Vue Router
- Axios
- Vue CLI PWA plugin (Workbox GenerateSW)
- Lucide Vue icons
- Vue Toast Notification

## Setup

### Install

```bash
cd frontend
npm install
```

### Development

```bash
npm run serve
```

Default URL: `http://localhost:8080`

### Production Build

```bash
npm run build
```

### Lint

```bash
npm run lint
```

## Route Map

Public:

- `/login`
- `/about`
- `/pricing-plans`
- `/public-receipts/:token`

Admin (requires auth):

- `/dashboard`
- `/register`
- `/students`
- `/students/:id`
- `/monthly-payments`
- `/monthly-expenses`
- `/seat-map`
- `/reminders`
- `/notifications`
- `/change-password`
- `/receipts/:paymentId`

Superadmin (requires auth + role):

- `/superadmin`
- `/superadmin/library/:library_id/students`
- `/superadmin/notifications`

Route guard behavior:

- `guestOnly` routes redirect authenticated users to role home.
- Superadmin is redirected away from admin-only pages.
- Non-superadmin blocked from `/superadmin*`.

## Key Files and Responsibilities

- `src/main.js`: app bootstrap.
- `src/App.vue`: global layout wrapper and route outlet.
- `src/router/index.js`: routes, guard rules, scroll reset.
- `src/api.js`: axios instance, `withCredentials`, global auth error handling.
- `src/views/AdminLogin.vue`: login flow and push subscription trigger for admins.
- `src/components/NavBar.vue`: topbar/sidebar/bottom-nav and logout flow.
- `src/components/SuperadminNotifications.vue`: compose/broadcast notifications.
- `src/components/NotificationCenter.vue`: admin inbox, unread management.
- `src/utils/pushNotifications.js`: browser push registration/subscription lifecycle.
- `public/sw-push.js`: service-worker push and notification click handlers.
- `vue.config.js`: PWA/workbox config and cache policy.

## Auth and Session UX

- Backend auth is cookie-based; frontend sends cookies via Axios `withCredentials`.
- Role metadata is stored in `localStorage` for route UX and nav rendering.
- Session expiry handling in `api.js` redirects to `/login` on token errors.

## PWA and Push Notifications

Configured behavior:

- Workbox generates `service-worker.js` for production.
- `sw-push.js` is imported into generated service worker.
- On admin login, app requests push config from backend, requests permission if needed, creates push subscription, and stores it server-side.
- On logout, app attempts to unsubscribe device subscription and remove it from backend.
- Notification click deep-links to route provided in payload URL.

Push prerequisites:

- Backend VAPID env vars must be configured.
- App must run on secure context (HTTPS, or localhost for local tests).

## Theming and UI System

- Dark enterprise visual system used across core pages.
- Shared glassmorphism surfaces and gradient mesh backgrounds.
- Responsive layouts with dedicated mobile nav experience.

## Backend Connectivity

The API base URL is currently hardcoded in `src/api.js`.

Before production build, set it to your production API endpoint (for example Railway custom domain).

## Common Developer Workflows

1. Start backend (`localhost:8000`) and frontend (`localhost:8080`).
2. Login as admin/superadmin.
3. Validate role guard paths.
4. Validate payment, seat, and notification features.
5. Run lint before commit.

## Known Implementation Notes

- Login flow currently clears service workers/caches before login; push setup then re-registers subscription as needed.
- Public receipt route hides navigation (`meta.hideNav`).
- Monthly payments and student detail now include row-level action loading states.

## Recommended Next Frontend Documentation Artifacts

For deeper Docs-as-Code, add:

- `docs/frontend-routing.md`: route intent and guard matrix.
- `docs/ui-system.md`: design tokens and reusable patterns.
- `docs/pwa-push.md`: push lifecycle and browser compatibility notes.
- `docs/error-handling.md`: global API interceptor behavior.
