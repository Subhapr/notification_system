# Environment Variables

Every credential in this project is read from environment variables. Nothing is
hardcoded. This document tells you **exactly** where to paste each value.

Legend used below:
- **File (local)**: the file to edit on your machine.
- **Render**: where to set it for the deployed backend.
- **Vercel**: where to set it for the deployed frontend.
- **Secret?**: whether it must be kept private.
- **Restart required?**: whether you need to restart/redeploy after changing it.

---

## Backend variables (`backend/.env`)

### DJANGO_SECRET_KEY
- **Purpose**: Cryptographic signing key for sessions, tokens, etc.
- **Where to obtain**: Generate one, e.g. `python -c "import secrets; print(secrets.token_urlsafe(50))"`.
- **File (local)**: `backend/.env` → `DJANGO_SECRET_KEY=`
- **Render**: Dashboard → your service → Environment → Add Environment Variable → `DJANGO_SECRET_KEY`
- **Secret?**: YES
- **Frontend?**: NO
- **Restart required?**: YES

### DEBUG
- **Purpose**: Enables Django debug mode (verbose errors). Must be `False` in production.
- **File (local)**: `backend/.env` → `DEBUG=True` (local) / `DEBUG=False` (production)
- **Render**: Environment variable `DEBUG=False`
- **Secret?**: NO
- **Restart required?**: YES

### ALLOWED_HOSTS
- **Purpose**: Comma-separated list of hostnames Django will serve.
- **File (local)**: `backend/.env` → `ALLOWED_HOSTS=localhost,127.0.0.1`
- **Render**: `ALLOWED_HOSTS=your-app.onrender.com` (Render also auto-adds `RENDER_EXTERNAL_HOSTNAME`)
- **Secret?**: NO
- **Restart required?**: YES

### CORS_ALLOWED_ORIGINS
- **Purpose**: Which frontend origins may call the API from the browser.
- **File (local)**: `backend/.env` → `CORS_ALLOWED_ORIGINS=http://localhost:3000`
- **Render**: `CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app`
- **Secret?**: NO
- **Restart required?**: YES

### DATABASE_URL
- **Purpose**: PostgreSQL connection string. Leave empty locally to use SQLite automatically.
- **Where to obtain**: Render → PostgreSQL instance → "Internal Database URL" (or External, if connecting from outside Render).
- **File (local)**: `backend/.env` → `DATABASE_URL=` (leave empty for SQLite)
- **Render**: Automatically provided if you attach a Render Postgres database, or paste manually.
- **Secret?**: YES
- **Restart required?**: YES

### JWT_ACCESS_TOKEN_LIFETIME_MINUTES / JWT_REFRESH_TOKEN_LIFETIME_DAYS
- **Purpose**: How long access/refresh tokens remain valid.
- **File (local)**: `backend/.env`
- **Secret?**: NO
- **Restart required?**: YES

---

### WhatsApp Cloud API (Meta sandbox)

#### WHATSAPP_ACCESS_TOKEN
- **Purpose**: Bearer token authorizing calls to the WhatsApp Cloud API.
- **Where to obtain**: [Meta for Developers](https://developers.facebook.com/apps) → your app → WhatsApp → API Setup → "Temporary access token" (or a permanent System User token for production).
- **File (local)**: `backend/.env` → `WHATSAPP_ACCESS_TOKEN=`
- **Render**: Environment variable `WHATSAPP_ACCESS_TOKEN`
- **Secret?**: YES
- **Frontend?**: NO — never sent to the browser.
- **Restart required?**: YES

#### WHATSAPP_PHONE_NUMBER_ID
- **Purpose**: Identifies which sandbox/business phone number sends the message.
- **Where to obtain**: Same WhatsApp → API Setup screen, "Phone number ID".
- **File (local)**: `backend/.env` → `WHATSAPP_PHONE_NUMBER_ID=`
- **Secret?**: Treat as sensitive (not a bearer token, but avoid publishing it).
- **Restart required?**: YES

#### WHATSAPP_API_VERSION
- **Purpose**: Graph API version to call, e.g. `v20.0`.
- **File (local)**: `backend/.env` → `WHATSAPP_API_VERSION=v20.0`
- **Secret?**: NO

---

### Email (Postmark)

#### EMAIL_PROVIDER
- **Purpose**: Selects which email adapter the engine uses: `postmark` (real) or `console` (safe dev mock — logs only, never sends).
- **File (local)**: `backend/.env` → `EMAIL_PROVIDER=console` for local dev, `EMAIL_PROVIDER=postmark` once you have credentials.
- **Secret?**: NO

#### POSTMARK_SERVER_TOKEN
- **Purpose**: Authenticates requests to the Postmark API.
- **Where to obtain**: [Postmark](https://postmarkapp.com) → Servers → your server → API Tokens → "Server API token".
- **File (local)**: `backend/.env` → `POSTMARK_SERVER_TOKEN=`
- **Secret?**: YES
- **Frontend?**: NO
- **Restart required?**: YES

#### POSTMARK_FROM_EMAIL
- **Purpose**: The verified "From" address Postmark will send as.
- **Where to obtain**: Postmark → Sender Signatures (must be verified before sending).
- **File (local)**: `backend/.env` → `POSTMARK_FROM_EMAIL=`
- **Secret?**: NO (but must be a verified sender)
- **Restart required?**: YES

---

### Web Push (OneSignal)

#### ONESIGNAL_APP_ID
- **Purpose**: Identifies your OneSignal app.
- **Where to obtain**: [OneSignal](https://onesignal.com) → your app → Settings → Keys & IDs → "OneSignal App ID".
- **File (local, backend)**: `backend/.env` → `ONESIGNAL_APP_ID=`
- **File (local, frontend)**: `frontend/.env.local` → `NEXT_PUBLIC_ONESIGNAL_APP_ID=` (same value — this one IS safe to expose to the browser)
- **Render**: `ONESIGNAL_APP_ID`
- **Vercel**: `NEXT_PUBLIC_ONESIGNAL_APP_ID`
- **Secret?**: NO (public identifier)
- **Restart required?**: YES

#### ONESIGNAL_REST_API_KEY
- **Purpose**: Server-side key used to actually send push notifications via the REST API.
- **Where to obtain**: OneSignal → Settings → Keys & IDs → "REST API Key".
- **File (local)**: `backend/.env` → `ONESIGNAL_REST_API_KEY=`
- **Secret?**: YES
- **Frontend?**: NEVER — this key must only exist in the backend.
- **Restart required?**: YES

---

### Misc

#### SITE_NAME
- **Purpose**: Used in the `{{site_name}}` template variable.
- **File (local)**: `backend/.env` → `SITE_NAME=NotifyHub`
- **Secret?**: NO

---

## Frontend variables (`frontend/.env.local`)

### NEXT_PUBLIC_API_BASE_URL
- **Purpose**: Base URL the frontend uses to call the Django API (no trailing slash).
- **File (local)**: `frontend/.env.local` → `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`
- **Vercel**: Project → Settings → Environment Variables → `NEXT_PUBLIC_API_BASE_URL=https://your-backend.onrender.com`
- **Secret?**: NO (all `NEXT_PUBLIC_*` variables are bundled into client JS)
- **Restart required?**: YES (rebuild/redeploy)

### NEXT_PUBLIC_ONESIGNAL_APP_ID
- See "Web Push (OneSignal)" above.

---

## Quick reference table

| Variable | Backend/Frontend | Secret | Local file |
|---|---|---|---|
| DJANGO_SECRET_KEY | Backend | Yes | backend/.env |
| DEBUG | Backend | No | backend/.env |
| ALLOWED_HOSTS | Backend | No | backend/.env |
| CORS_ALLOWED_ORIGINS | Backend | No | backend/.env |
| DATABASE_URL | Backend | Yes | backend/.env |
| WHATSAPP_ACCESS_TOKEN | Backend | Yes | backend/.env |
| WHATSAPP_PHONE_NUMBER_ID | Backend | Yes | backend/.env |
| WHATSAPP_API_VERSION | Backend | No | backend/.env |
| EMAIL_PROVIDER | Backend | No | backend/.env |
| POSTMARK_SERVER_TOKEN | Backend | Yes | backend/.env |
| POSTMARK_FROM_EMAIL | Backend | No | backend/.env |
| ONESIGNAL_APP_ID | Backend | No | backend/.env |
| ONESIGNAL_REST_API_KEY | Backend | Yes | backend/.env |
| SITE_NAME | Backend | No | backend/.env |
| NEXT_PUBLIC_API_BASE_URL | Frontend | No | frontend/.env.local |
| NEXT_PUBLIC_ONESIGNAL_APP_ID | Frontend | No | frontend/.env.local |
