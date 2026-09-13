# Deployment

## Backend → Render

### Option A: Blueprint (fastest)
1. Push this repo to GitHub.
2. In Render, click **New → Blueprint**, point it at your repo. It will read
   `render.yaml` at the repo root and provision a web service + PostgreSQL
   database.
3. Fill in the remaining secret environment variables (WhatsApp, Postmark,
   OneSignal — see `docs/ENVIRONMENT_VARIABLES.md`) in the service's
   Environment tab, since these aren't in the blueprint for safety.

### Option B: Manual
1. **New → PostgreSQL** — create a database, copy its Internal Database URL.
2. **New → Web Service** — connect your repo, set:
   - **Root Directory**: `backend`
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
3. Add environment variables (Dashboard → your service → Environment):
   - `DJANGO_SECRET_KEY` (generate one)
   - `DEBUG=False`
   - `ALLOWED_HOSTS=your-app.onrender.com`
   - `CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app`
   - `DATABASE_URL` = the Postgres Internal Database URL from step 1
   - WhatsApp / Postmark / OneSignal variables per `docs/ENVIRONMENT_VARIABLES.md`
4. Deploy. Render runs `build.sh` (installs deps, collects static files,
   migrates), then starts gunicorn.
5. Verify: `curl https://your-app.onrender.com/health/` → `{"status": "ok"}`
6. Create your admin user via Render's shell tab:
   ```bash
   python manage.py create_demo_admin --email you@example.com --password yourpassword
   ```

## Frontend → Vercel

1. Push this repo to GitHub (if not already).
2. In Vercel, **Add New → Project**, import the repo, set **Root Directory**
   to `frontend`.
3. Vercel auto-detects Next.js; leave build settings as default (or use the
   included `vercel.json`).
4. Add environment variables (Project → Settings → Environment Variables):
   - `NEXT_PUBLIC_API_BASE_URL=https://your-app.onrender.com`
   - `NEXT_PUBLIC_ONESIGNAL_APP_ID=<your OneSignal App ID>`
5. Deploy. Vercel gives you a `https://your-frontend.vercel.app` URL.
6. Go back to Render and update `CORS_ALLOWED_ORIGINS` to that exact URL,
   then redeploy the backend (env var changes require a redeploy).

## Switching between local and deployed backends

The frontend never hardcodes an API URL — it only reads
`NEXT_PUBLIC_API_BASE_URL`. Point it at `http://localhost:8000` for local
development or your Render URL for production; no code changes needed.

## Health checks

Render can be configured to poll `GET /health/` for zero-downtime deploys
(Render dashboard → your service → Settings → Health Check Path → `/health/`).

## Static files

`whitenoise` serves Django's own static files (mainly the Django admin) in
production — no separate static file host is required.
