# Credential Setup Checklist

Follow this checklist in order. Each step tells you what to click and where the
resulting value goes. Full details on each variable are in
[`ENVIRONMENT_VARIABLES.md`](./ENVIRONMENT_VARIABLES.md).

The app works with **zero credentials** out of the box: WhatsApp and Web Push
templates simply log a "not configured" failure in Notification Logs, and
Email defaults to a safe console mock mode. Add credentials one provider at a
time and re-test after each.

## 1. Meta Developer account
1. Go to https://developers.facebook.com and log in / sign up.
2. Click **My Apps → Create App → Other → Business**.

## 2. WhatsApp app
1. In your new app's dashboard, click **Add Product** and set up **WhatsApp**.
2. This creates a test WhatsApp Business Account with a sandbox number.

## 3. WhatsApp test phone
1. Under **WhatsApp → API Setup**, note the sandbox "From" phone number.
2. This is what your account will send messages from — no purchase needed.

## 4. WhatsApp recipient
1. Under the same API Setup screen, add your own WhatsApp number as a test
   recipient and confirm it via the code Meta sends you.
2. You can only message verified test recipients until the app goes live.

## 5. WhatsApp access token
1. Copy the "Temporary access token" shown on the API Setup screen (valid
   ~24h; generate a permanent one later via System Users for production).
2. Paste it into `backend/.env` → `WHATSAPP_ACCESS_TOKEN=`.

## 6. Phone number ID
1. Copy "Phone number ID" from the same screen.
2. Paste into `backend/.env` → `WHATSAPP_PHONE_NUMBER_ID=`.

## 7. Postmark account
1. Sign up at https://postmarkapp.com (free tier available).
2. Create a **Server** inside a Project.

## 8. Verified sender
1. Go to **Sender Signatures** and verify an email address you own (Postmark
   emails you a confirmation link).
2. This becomes `POSTMARK_FROM_EMAIL`.

## 9. Postmark server token
1. Inside your Server, go to **API Tokens** and copy the **Server API token**.
2. Paste into `backend/.env` → `POSTMARK_SERVER_TOKEN=`.
3. Also set `EMAIL_PROVIDER=postmark` (it defaults to `console`, a safe mock).

## 10. OneSignal account
1. Sign up at https://onesignal.com.
2. Click **New App/Website**, choose **Web Push**, and follow the setup
   wizard (site name, site URL — use `http://localhost:3000` for local dev).

## 11. OneSignal app
1. Complete the wizard. Note the **App ID** shown in Settings → Keys & IDs.
2. Paste it into **both**:
   - `backend/.env` → `ONESIGNAL_APP_ID=`
   - `frontend/.env.local` → `NEXT_PUBLIC_ONESIGNAL_APP_ID=`

## 12. OneSignal REST API key
1. Same Keys & IDs screen → copy the **REST API Key**.
2. Paste into `backend/.env` → `ONESIGNAL_REST_API_KEY=` only. Never put this
   in the frontend.

## 13. Browser subscription
1. Start both servers (see `docs/SETUP.md`).
2. Log in to the frontend, go to **Settings**, and click **Subscribe this
   browser**.
3. Accept the browser's notification permission prompt.
4. Go to **Notification Settings → Login → Web Push → Test** to confirm
   delivery.

---

Once all three providers are configured, turn each channel ON from
**Notification Settings** and fire a real Login/Logout to see all three
channels dispatch independently.
