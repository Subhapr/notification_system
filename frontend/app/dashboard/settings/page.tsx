"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/Button";
import { ChannelIcon, CHANNEL_LABELS } from "@/components/ChannelIcon";
import { LoadingState } from "@/components/Feedback";
import { Badge } from "@/components/Form";
import { useToast } from "@/hooks/useToast";
import { api, ApiError } from "@/lib/api";
import { subscribeBrowserToWebPush } from "@/lib/webpush";
import type { Channel } from "@/types";

type ConfigStatus = Record<Channel, boolean>;

export default function SettingsPage() {
  const { showToast } = useToast();
  const [status, setStatus] = useState<ConfigStatus | null>(null);
  const [subscribing, setSubscribing] = useState(false);

  useEffect(() => {
    api.get<ConfigStatus>("/api/config-status/").then(setStatus);
  }, []);

  async function handleSubscribe() {
    setSubscribing(true);
    try {
      const id = await subscribeBrowserToWebPush();
      if (id) {
        showToast("This browser is now subscribed to Web Push.", "success");
      } else {
        showToast("Permission was not granted.", "error");
      }
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Unable to subscribe.", "error");
    } finally {
      setSubscribing(false);
    }
  }

  return (
    <div className="mx-auto max-w-3xl px-5 py-8">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-ink">Settings</h1>
        <p className="mt-1 text-sm text-muted">
          Provider configuration status and this browser&apos;s Web Push subscription.
        </p>
      </div>

      <div className="mb-6 rounded-2xl border border-border bg-surface p-5">
        <h2 className="mb-4 text-sm font-semibold text-ink">Provider status</h2>
        {!status ? (
          <LoadingState />
        ) : (
          <div className="space-y-3">
            {(Object.keys(status) as Channel[]).map((channel) => (
              <div
                key={channel}
                className="flex items-center justify-between rounded-xl border border-border bg-surfaceRaised px-4 py-3"
              >
                <span className="inline-flex items-center gap-2 text-sm text-ink">
                  <ChannelIcon channel={channel} className="h-4 w-4 text-accent" />
                  {CHANNEL_LABELS[channel]}
                </span>
                <Badge tone={status[channel] ? "success" : "warning"}>
                  {status[channel] ? "Configured" : "Missing credentials"}
                </Badge>
              </div>
            ))}
          </div>
        )}
        <p className="mt-4 text-xs text-muted">
          Paste real credentials into <code className="font-mono">backend/.env</code> — see
          docs/ENVIRONMENT_VARIABLES.md for exactly where each value goes.
        </p>
      </div>

      <div className="rounded-2xl border border-border bg-surface p-5">
        <h2 className="mb-2 text-sm font-semibold text-ink">Web Push subscription</h2>
        <p className="mb-4 text-xs text-muted">
          Subscribe this browser to receive Web Push test notifications sent from the Notification
          Settings page.
        </p>
        <Button variant="secondary" onClick={handleSubscribe} loading={subscribing}>
          Subscribe this browser
        </Button>
      </div>
    </div>
  );
}
