# Testing

## Backend

```bash
cd backend
python manage.py test tests
```

31 tests, all using Django's `TestCase` (transactional, isolated database per
test). **No real WhatsApp/Postmark/OneSignal API calls are ever made** —
external providers are mocked with `unittest.mock.patch`, and providers are
simply unconfigured in the test environment (no `.env` secrets), which
exercises the real "provider not configured" failure path.

### What's covered (`backend/tests/`)

- **`test_auth.py`** — login success/failure, that login fires only enabled
  `LOGIN` templates (not `LOGOUT`), that disabled templates are skipped, JWT
  refresh, logout blacklisting the refresh token, `/api/auth/me/`.
- **`test_notification_engine.py`** — the safe variable renderer (including
  that it does **not** evaluate arbitrary Python), channel isolation (one
  provider failing doesn't block another), inactive triggers being skipped
  entirely, disabled channels not sending, missing recipients producing
  `SKIPPED` (not `FAILED`), and Web Push resolving the user's active
  subscription.
- **`test_templates_api.py`** — permission boundaries (normal users get 403
  on template endpoints, unauthenticated requests get 401), template CRUD,
  the `toggle` action, the `test` (send-test) action succeeding with a mocked
  provider and failing cleanly when a provider is unconfigured, and Web Push
  subscribe/unsubscribe.
- **`test_admin_endpoints.py`** — the admin-only users directory and
  provider config-status endpoint.

### Mocking pattern

```python
@patch("services.notification_engine.provider_registry.get_email_provider")
def test_send_test_success(self, mock_email_factory):
    mock_provider = mock_email_factory.return_value
    mock_provider.is_configured.return_value = True
    mock_provider.send.return_value = ProviderResult(success=True, provider_message_id="msg-1")
    ...
```

Patching happens at the `provider_registry` factory function, so the engine's
real dispatch/logging logic still runs end-to-end — only the outbound HTTP
call is replaced.

## Frontend

The frontend is verified via a full production build (`npm run build`),
which runs the TypeScript compiler in strict mode across every page and
component. For interactive verification, run both servers per
`docs/SETUP.md` and walk through the demo flow.

## Manual end-to-end smoke test

1. `python manage.py seed_demo_data`
2. Start backend + frontend.
3. Log in as `admin@notifyhub.local`.
4. Enable the LOGIN → Email template (Email defaults to a safe console mock
   provider, so this works with zero credentials).
5. Log out and back in; confirm a `SENT` row appears in Notification Logs.
6. Add real WhatsApp/OneSignal credentials per `docs/CREDENTIAL_SETUP.md` and
   repeat with the WhatsApp/Web Push channels.
