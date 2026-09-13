# Architecture

## Overview

```
Next.js Frontend (TypeScript, Tailwind)
        │  JWT over HTTPS
        ▼
Django REST API  (apps/accounts, apps/notifications)
        │
        ▼
NotificationEngine  (services/notification_engine)
        │  loads Trigger + enabled NotificationTemplates
        │  resolves {{variables}} via a safe renderer
        ▼
Provider Adapters   (services/whatsapp, services/email, services/webpush)
        │
        ▼
WhatsApp Cloud API · Postmark · OneSignal
```

Every attempt is written to `NotificationLog` regardless of outcome, giving a
full audit trail independent of whether the send succeeded.

## Why a provider abstraction?

The assignment requires the admin to manage everything from one screen and
requires that adding a new email provider (e.g. Brevo) shouldn't touch
business logic. This is solved with a small interface:

```python
class BaseNotificationProvider:
    def is_configured(self) -> bool: ...
    def send(self, *, recipient, subject, title, body) -> ProviderResult: ...
```

`NotificationEngine` only ever calls `provider.send(...)` and reads a
normalized `ProviderResult(success, provider_message_id, raw_response,
error_message)`. It never touches `requests`, HTTP status codes, or any
vendor-specific payload shape directly — that's isolated inside each
`services/<channel>/*_provider.py` file.

**Adding a new email provider** (e.g. Resend) means:
1. Create `services/email/providers.py::ResendEmailProvider(BaseEmailProvider)`.
2. Implement `is_configured()` and `send()`.
3. Register it in `get_email_provider()`'s `providers` dict.
4. Set `EMAIL_PROVIDER=resend` in `.env`.

No changes anywhere else — not in the engine, not in views, not in the
frontend.

## Why a Trigger/Template data model instead of hardcoded triggers?

`NotificationEngine.fire(trigger_code="LOGIN", user=..., context=...)` looks
the trigger up by `code` at runtime. **Adding a new trigger** (e.g.
`ORDER_PLACED`) means:
1. Add a row to `Trigger` (via the admin UI's "Add trigger" button, or the API).
2. Add an entry to `services/notification_engine/variables.py::TRIGGER_VARIABLES`
   describing which `{{variables}}` are available for it (optional — falls
   back to common variables).
3. Call `NotificationEngine.fire(trigger_code="ORDER_PLACED", user=user,
   context={"order_id": ..., "order_total": ...})` from wherever that event
   happens in your codebase (e.g. the order-creation view).

No changes to the engine, the provider adapters, the API, or the frontend
matrix — the new trigger just appears as a new row.

## Why per-channel isolation matters

`NotificationEngine._dispatch_one()` wraps each channel's send in its own
try/except and writes its own `NotificationLog` row. A WhatsApp timeout can
never prevent the Email or Web Push channel for the same event from being
attempted, and an unexpected exception in one provider never bubbles up to
break the login/logout HTTP response itself.

## Why a safe template renderer instead of Python templates/eval?

`services/notification_engine/template_renderer.py` uses a single regex
(`\{\{\s*([a-zA-Z0-9_]+)\s*\}\}`) and a plain dict lookup — no `eval`, no
Django template engine with arbitrary context, no format-string injection
surface. Unknown variables render as an empty string rather than raising, so
a typo in a template can never crash a live login/logout flow.

## Why NotificationLog uses UUID primary keys

Log rows are an audit trail, potentially exposed via API to admins across
paginated views; UUIDs avoid leaking sequential volume information and make
external references (e.g. from provider webhooks in a future iteration)
collision-safe.

## Frontend structure

- `hooks/useAuth.tsx` — JWT session state, `apiRequest` auto-refreshes an
  expired access token once via the refresh token before failing.
- `lib/api.ts` — single fetch wrapper enforcing the `{success, message,
  data}` envelope everywhere, including paginated list responses (see
  `apps/core/pagination.py::EnvelopePageNumberPagination` and
  `apps/core/viewsets.py::EnvelopeModelViewSet` on the backend, which wrap
  every DRF action consistently).
- `app/dashboard/notifications/page.tsx` — the matrix is a `trigger × channel`
  grid built client-side from two flat lists (`/api/triggers/`,
  `/api/notification-templates/`), so the UI never assumes a specific set of
  channels or triggers beyond the fixed three channels.

## Ready for background workers

`NotificationEngine.fire()` runs synchronously today (simplest correct
implementation for the assignment), but every provider call is a plain
function call with no shared mutable state, and every attempt is idempotent
at the (trigger, channel, template) level per call. Moving dispatch to Celery
means wrapping `NotificationEngine._dispatch_one` in a `@shared_task` and
calling `.delay(...)` from `.fire()` instead of calling it directly — no
model or provider changes required.
