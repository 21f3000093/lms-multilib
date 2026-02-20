# Frontend (Vue 3)

## Purpose

Vue client for LMS MultiLib. It provides:
- admin and superadmin login flows
- dashboard, student, seat, payment, expense, and reminder screens
- route-based access control with role checks

## Prerequisites

- Node.js 18+ (recommended)
- npm 9+

## Install

```bash
npm install
```

## Run (Development)

```bash
npm run serve
```

Default local URL: `http://localhost:8080`

## Build (Production)

```bash
npm run build
```

## Lint

```bash
npm run lint
```

## Key Files

- `src/api.js`: Axios client and response interceptor (auth/session handling)
- `src/router/index.js`: route definitions + auth guard
- `src/views/AdminLogin.vue`: login entry point
- `src/components/*`: feature UI modules

## Backend Connectivity

The API base URL is currently hardcoded in `src/api.js`.
If you deploy to a different backend, update `baseURL` there before building.
