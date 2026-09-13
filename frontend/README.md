# Frontend — Next.js Admin Dashboard

See the [root README](../README.md) and [`docs/`](../docs) for full project
documentation. This file covers frontend-specific commands only.

## Setup

```bash
npm install
cp .env.example .env.local
npm run dev
```

## Environment

- `NEXT_PUBLIC_API_BASE_URL` — Django API base URL, no trailing slash.
- `NEXT_PUBLIC_ONESIGNAL_APP_ID` — public OneSignal App ID (safe to expose;
  the REST API key stays server-side only).

## Pages

```
app/login/                              centered auth card
app/dashboard/                          protected layout (redirects to /login if unauthenticated)
app/dashboard/page.tsx                  overview / stats
app/dashboard/notifications/page.tsx    the trigger × channel matrix (hero feature)
app/dashboard/notifications/logs/       filterable notification log table
app/dashboard/users/                    read-only user directory
app/dashboard/settings/                 provider status + Web Push browser subscription
```

## Design system

Reusable components live in `components/`: `Button`, `Form` (Input, Textarea,
Select, Switch, Badge), `Drawer`, `Feedback` (ConfirmDialog, EmptyState,
LoadingState), `ChannelIcon`, `DashboardShell` (sidebar + top nav).

## Commands

```bash
npm run dev      # local dev server
npm run build    # production build (also type-checks with `tsc --strict`)
npm run start    # serve a production build
npm run lint     # eslint
```
