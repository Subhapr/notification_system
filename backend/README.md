# Backend — Django REST API

See the [root README](../README.md) and [`docs/`](../docs) for full project
documentation. This file covers backend-specific commands only.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver
```

## Useful commands

```bash
python manage.py test tests                 # run the test suite (31 tests)
python manage.py makemigrations              # after changing models
python manage.py create_demo_admin --email you@example.com --password yourpassword
python manage.py seed_demo_data              # idempotent: safe to re-run
python manage.py createsuperuser             # standard Django admin superuser
```

## Layout

```
config/                 settings, urls, wsgi/asgi
apps/
  accounts/              custom User model, JWT auth views, users directory
  notifications/         Trigger / NotificationTemplate / NotificationLog / WebPushSubscription
  core/                  response envelope, exception handler, permissions, pagination, viewsets
services/
  notification_engine/   the engine itself, template renderer, variable registry, provider registry
  whatsapp/               WhatsApp Cloud API adapter
  email/                  Postmark (+ console mock, Brevo stub) adapters
  webpush/                OneSignal adapter
tests/                   auth, engine, template API, admin endpoint tests
```

Django admin is available at `/admin/` for direct database inspection (create
a superuser with `createsuperuser`), separate from the custom SaaS dashboard
the frontend provides.
