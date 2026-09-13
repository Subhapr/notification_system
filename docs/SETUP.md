# Setup Guide (Local Development)

## Prerequisites
- Python 3.12+
- Node.js 18+
- (Optional) PostgreSQL — SQLite is used automatically if `DATABASE_URL` is empty.

## 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env             # then edit .env as needed (see docs/ENVIRONMENT_VARIABLES.md)

python manage.py migrate
python manage.py seed_demo_data  # creates demo admin/user, LOGIN/LOGOUT triggers, sample templates
python manage.py runserver
```

Backend now runs at `http://localhost:8000`. Verify with:

```bash
curl http://localhost:8000/health/
# {"status": "ok"}
```

Demo credentials created by `seed_demo_data`:
- Admin: `admin@notifyhub.local` / `DemoPass123!`
- Normal user: `user@notifyhub.local` / `DemoPass123!`

To create your own admin instead:

```bash
python manage.py create_demo_admin --email you@example.com --password yourpassword
```

## 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env.local       # edit if your backend runs elsewhere
npm run dev
```

Frontend now runs at `http://localhost:3000`.

## 3. Database

- **Local development**: leave `DATABASE_URL` empty in `backend/.env` — Django
  automatically uses a local `db.sqlite3` file.
- **PostgreSQL** (optional locally, required in production): install Postgres,
  create a database, and set:
  ```
  DATABASE_URL=postgres://user:password@localhost:5432/notification_system
  ```
  Then re-run `python manage.py migrate`.

## 4. Migrations

```bash
python manage.py makemigrations   # after changing models
python manage.py migrate
```

## 5. Running tests

```bash
cd backend
python manage.py test tests
```

See [`TESTING.md`](./TESTING.md) for details on what's covered and how
external providers are mocked.

## 6. Provider credentials

The app runs with zero credentials configured — WhatsApp/Web Push simply log
a clear "not configured" failure, and Email defaults to a console mock mode.
To wire up real providers, follow [`CREDENTIAL_SETUP.md`](./CREDENTIAL_SETUP.md).

## 7. Everyday demo flow

1. Open `http://localhost:3000`, log in as the demo admin.
2. Go to **Notification Settings**, edit the LOGIN → Email template, turn it on.
3. Log out, then log back in as the demo admin (or open a private window and
   log in as the demo user) — check **Notification Logs** for the result.
