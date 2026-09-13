# NotifyHub — Notification Management System

A production-oriented notification management system. Admins configure and
send WhatsApp, Email, and Web Push notifications for any application event
(Login, Logout, and any future trigger) from a single screen — no provider
dashboards required.

## Features

- **One admin screen** to manage every trigger × channel combination
- **Trigger-driven, data-driven architecture** — new triggers (e.g.
  `ORDER_PLACED`) can be added from the UI with zero engine code changes
- **Provider abstraction** — WhatsApp Cloud API, Postmark (Email), OneSignal
  (Web Push) sit behind clean interfaces; swapping/adding providers never
  touches business logic
- **Safe template variables** (`{{user_name}}`, `{{login_time}}`, ...) with a
  controlled, non-`eval` renderer
- **Per-channel isolation** — one provider failing never blocks another, or
  the login/logout request itself
- **Full audit trail** via `NotificationLog`, with a filterable admin UI
- **JWT authentication**, staff-only admin endpoints
- **31 backend tests**, all external providers mocked (no real API calls in CI)
- Render + Vercel deployment configs included

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | Next.js (App Router), TypeScript, Tailwind CSS |
| Backend | Python, Django, Django REST Framework |
| Auth | JWT (`djangorestframework-simplejwt`) |
| Database | PostgreSQL (production), SQLite (local dev) |
| WhatsApp | Meta WhatsApp Cloud API (sandbox) |
| Email | Postmark (behind a swappable provider interface) |
| Web Push | OneSignal (browser only) |
| Deployment | Render (backend), Vercel (frontend) |

## Folder structure

```
notification-system/
├── backend/            Django + DRF API, notification engine, provider adapters
│   ├── apps/           accounts, notifications, core
│   ├── services/       whatsapp/, email/, webpush/, notification_engine/
│   └── tests/          31 tests covering auth, engine, permissions, providers
├── frontend/           Next.js admin dashboard
│   ├── app/            login, dashboard (notifications matrix, logs, users, settings)
│   ├── components/     design-system components (Button, Drawer, Badge, ...)
│   ├── hooks/          useAuth, useToast
│   └── lib/            API client, Web Push helper
├── docs/               SETUP, ENVIRONMENT_VARIABLES, CREDENTIAL_SETUP,
│                       API_DOCUMENTATION, ARCHITECTURE, TESTING, DEPLOYMENT
├── render.yaml         Render blueprint
└── .gitignore
```

## Quick start

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver

# Frontend (new terminal)
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open `http://localhost:3000`, log in with `admin@notifyhub.local` /
`DemoPass123!`.

Full details: [`docs/SETUP.md`](docs/SETUP.md).

## Notification flow

```
User logs in
   → Django authenticates, issues JWT
   → NotificationEngine.fire("LOGIN", user, context)
   → Loads enabled LOGIN templates (WhatsApp / Email / Web Push)
   → Renders {{variables}} safely
   → Each channel's provider adapter sends independently
   → Each attempt logged to NotificationLog, success or failure
   → Login response returns regardless of notification outcome
```

## Available triggers (out of the box)

- `LOGIN` — fires on successful authentication
- `LOGOUT` — fires on logout

Architected so `NOT_LOGGED_IN_1_DAY`, `NOT_LOGGED_IN_1_WEEK`,
`PASSWORD_RESET`, `ORDER_PLACED`, or any custom trigger can be added from the
**Notification Settings → Add trigger** button with no code changes — see
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for exactly how.

## Provider setup

The app runs out of the box with zero credentials (Email defaults to a safe
console mock; WhatsApp/Web Push cleanly report "not configured" in the logs).
To wire up real sandbox credentials:

1. [`docs/CREDENTIAL_SETUP.md`](docs/CREDENTIAL_SETUP.md) — step-by-step
   checklist for Meta WhatsApp, Postmark, and OneSignal.
2. [`docs/ENVIRONMENT_VARIABLES.md`](docs/ENVIRONMENT_VARIABLES.md) — exactly
   which file/dashboard each variable goes in.

## Deployment

- Backend → Render: [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)
- Frontend → Vercel: [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md)

## Admin login

After `seed_demo_data`:
- Admin: `admin@notifyhub.local` / `DemoPass123!`
- Normal user: `user@notifyhub.local` / `DemoPass123!`

Or create your own:
```bash
python manage.py create_demo_admin --email you@example.com --password yourpassword
```

## Testing

```bash
cd backend && python manage.py test tests
```

31 tests covering the engine, auth, permissions, and channel isolation — see
[`docs/TESTING.md`](docs/TESTING.md).

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| Frontend shows "Admin access required" | Logged in user has `is_staff=False`; use the demo admin or promote your user via `create_demo_admin`. |
| Test send returns "not configured" | Expected until you add real credentials — see `docs/CREDENTIAL_SETUP.md`. |
| CORS errors in browser console | `CORS_ALLOWED_ORIGINS` in `backend/.env` doesn't match your frontend's exact origin. |
| Web Push subscribe button does nothing | `NEXT_PUBLIC_ONESIGNAL_APP_ID` is empty, or the browser denied the permission prompt. |
| 401 immediately after login | Access tokens are short-lived (default 30 min); the frontend auto-refreshes using the refresh token — if that's also expired (default 7 days), log in again. |

## Architecture

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full breakdown of
the provider abstraction, the trigger/template data model, and why each
design decision was made.
