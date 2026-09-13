"use client";

import { api } from "@/lib/api";

declare global {
  interface Window {
    OneSignalDeferred?: unknown[];
  }
}

const ONESIGNAL_APP_ID = process.env.NEXT_PUBLIC_ONESIGNAL_APP_ID || "";

/**
 * Loads the OneSignal SDK and initializes it with the public app id
 * only. The REST API key never appears in frontend code - all actual
 * sending happens server-side through the Django backend.
 */
export function loadOneSignal(): Promise<void> {
  return new Promise((resolve) => {
    if (!ONESIGNAL_APP_ID) {
      resolve();
      return;
    }
    if (document.getElementById("onesignal-sdk")) {
      resolve();
      return;
    }
    const script = document.createElement("script");
    script.id = "onesignal-sdk";
    script.src = "https://cdn.onesignal.com/sdks/web/v16/OneSignalSDK.page.js";
    script.defer = true;
    script.onload = () => resolve();
    document.head.appendChild(script);

    window.OneSignalDeferred = window.OneSignalDeferred || [];
    window.OneSignalDeferred.push(async (OneSignal: any) => {
      await OneSignal.init({ appId: ONESIGNAL_APP_ID, allowLocalhostAsSecureOrigin: true });
    });
  });
}

/**
 * Requests browser permission, then registers the resulting
 * subscription id with the Django backend against the current user.
 */
export async function subscribeBrowserToWebPush(): Promise<string | null> {
  if (!ONESIGNAL_APP_ID) {
    throw new Error("Web Push is not configured (NEXT_PUBLIC_ONESIGNAL_APP_ID missing).");
  }
  await loadOneSignal();

  return new Promise((resolve, reject) => {
    window.OneSignalDeferred = window.OneSignalDeferred || [];
    window.OneSignalDeferred.push(async (OneSignal: any) => {
      try {
        await OneSignal.Notifications.requestPermission();
        const subscriptionId: string | undefined = OneSignal.User?.PushSubscription?.id;
        if (!subscriptionId) {
          resolve(null);
          return;
        }
        await api.post("/api/webpush/subscribe/", {
          external_subscription_id: subscriptionId,
          browser: navigator.userAgent,
        });
        resolve(subscriptionId);
      } catch (err) {
        reject(err);
      }
    });
  });
}
