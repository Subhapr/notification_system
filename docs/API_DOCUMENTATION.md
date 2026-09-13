# API Documentation

Base URL (local): `http://localhost:8000`

## Response envelope

Every endpoint returns the same shape:

```json
{ "success": true, "message": "...", "data": { ... } }
```

Errors:

```json
{ "success": false, "message": "Unable to send notification.", "errors": { "field": ["..."] } }
```

Paginated list endpoints nest pagination info inside `data`:

```json
{
  "success": true,
  "message": "",
  "data": { "count": 12, "next": "http://.../?page=2", "previous": null, "results": [ ... ] }
}
```

## Authentication

All endpoints except `/health/` and `/api/auth/login/` require a JWT access
token: `Authorization: Bearer <token>`.

### POST /api/auth/login/
- **Auth**: None
- **Body**: `{ "email": "admin@notifyhub.local", "password": "DemoPass123!" }`
- **Response 200**: `{ user: {...}, tokens: { access, refresh } }`
- **Errors**: 400 invalid credentials.
- Side effect: fires the `LOGIN` trigger for the authenticated user.

### POST /api/auth/logout/
- **Auth**: Required
- **Body**: `{ "refresh": "<refresh token>" }`
- **Response 200**: blacklists the refresh token.
- **Errors**: 400 invalid/expired token, 401 unauthenticated.
- Side effect: fires the `LOGOUT` trigger.

### POST /api/auth/refresh/
- **Auth**: None
- **Body**: `{ "refresh": "<refresh token>" }`
- **Response 200**: `{ access: "<new access token>" }`
- **Errors**: 401 invalid/expired/blacklisted token.

### GET /api/auth/me/
- **Auth**: Required
- **Response 200**: current user object.

### GET /api/auth/users/
- **Auth**: Staff only
- **Response 200**: paginated list of all users.

## Triggers

### GET /api/triggers/
- **Auth**: Staff only
- **Response 200**: paginated list of triggers, each including
  `available_variables` for its code.

### POST /api/triggers/
- **Auth**: Staff only
- **Body**: `{ "name": "Password Reset", "code": "PASSWORD_RESET", "description": "...", "is_active": true }`
- **Response 201**: created trigger.

### GET/PATCH/DELETE /api/triggers/{id}/
- **Auth**: Staff only
- Standard retrieve/update/delete.

## Notification Templates

### GET /api/notification-templates/
- **Auth**: Staff only
- **Query params**: `?trigger=LOGIN` filters by trigger code.
- **Response 200**: paginated list. Each item includes `is_provider_configured`
  (whether the channel's provider has credentials set, without exposing them).

### POST /api/notification-templates/
- **Auth**: Staff only
- **Body**:
  ```json
  {
    "trigger": 1,
    "channel": "EMAIL",
    "name": "Login email",
    "subject": "Welcome back to {{site_name}}",
    "body": "Hi {{user_name}}, you logged in at {{login_time}}.",
    "enabled": true
  }
  ```
- **Response 201**: created template.
- **Errors**: 400 if `subject` missing for an EMAIL template, or if a
  template for this (trigger, channel) pair already exists.

### GET/PATCH/DELETE /api/notification-templates/{id}/
- **Auth**: Staff only.

### POST /api/notification-templates/{id}/toggle/
- **Auth**: Staff only
- Flips `enabled` and returns the updated template.

### POST /api/notification-templates/{id}/test/
- **Auth**: Staff only
- **Body**: `{ "test_recipient": "+15551234567" }` (omit for Web Push — uses
  the current admin's active subscription).
- **Response 200**: `{ channel, status: "SENT", message }`
- **Response 422**: `{ channel, status: "FAILED"|"SKIPPED", message }` — e.g.
  provider not configured, or no Web Push subscription registered.

## Notification Logs

### GET /api/notifications/logs/
- **Auth**: Staff only
- **Query params**: `trigger`, `channel`, `status`, `date_from`, `date_to`
  (ISO 8601 datetimes).
- **Response 200**: paginated list of `NotificationLog` entries, most recent
  first.

## Web Push

### POST /api/webpush/subscribe/
- **Auth**: Any authenticated user (registers *their own* browser)
- **Body**: `{ "external_subscription_id": "...", "browser": "Chrome/125...", "device_metadata": {} }`
- **Response 200**: confirms subscription.

### POST /api/webpush/unsubscribe/
- **Auth**: Any authenticated user
- **Body**: `{ "external_subscription_id": "..." }`
- **Response 200**: marks the subscription inactive.

## Provider configuration status

### GET /api/config-status/
- **Auth**: Staff only
- **Response 200**: `{ "WHATSAPP": false, "EMAIL": true, "WEB_PUSH": false }`
  — never returns the credentials themselves, only whether each is set.

## Health

### GET /health/
- **Auth**: None
- **Response 200**: `{ "status": "ok" }` — used by Render for health checks.
