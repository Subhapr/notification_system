"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { LoadingState } from "@/components/Feedback";
import { api } from "@/lib/api";
import type { NotificationLog, NotificationTemplate, Paginated, Trigger } from "@/types";

export default function DashboardHomePage() {
  const [triggers, setTriggers] = useState<Trigger[] | null>(null);
  const [templates, setTemplates] = useState<NotificationTemplate[] | null>(null);
  const [recentLogs, setRecentLogs] = useState<NotificationLog[] | null>(null);

  useEffect(() => {
    api.get<Paginated<Trigger>>("/api/triggers/").then((d) => setTriggers(d.results));
    api
      .get<Paginated<NotificationTemplate>>("/api/notification-templates/")
      .then((d) => setTemplates(d.results));
    api
      .get<Paginated<NotificationLog>>("/api/notifications/logs/")
      .then((d) => setRecentLogs(d.results.slice(0, 6)));
  }, []);

  if (!triggers || !templates || !recentLogs) {
    return <LoadingState />;
  }

  const enabledCount = templates.filter((t) => t.enabled).length;
  const sentCount = recentLogs.filter((l) => l.status === "SENT").length;

  return (
    <div className="mx-auto max-w-6xl px-5 py-8">
      <div className="mb-8">
        <h1 className="text-xl font-semibold text-ink">Dashboard</h1>
        <p className="mt-1 text-sm text-muted">
          An overview of your notification configuration and recent activity.
        </p>
      </div>

      <div className="mb-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatCard label="Active triggers" value={triggers.filter((t) => t.is_active).length.toString()} />
        <StatCard label="Enabled templates" value={`${enabledCount} / ${templates.length}`} />
        <StatCard label="Recent sends" value={sentCount.toString()} hint="of last 6 logged" />
      </div>

      <div className="rounded-2xl border border-border bg-surface p-5">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-ink">Getting started</h2>
        </div>
        <ol className="space-y-3 text-sm text-muted">
          <li>
            1. Open{" "}
            <Link href="/dashboard/notifications" className="text-accent hover:underline">
              Notification Settings
            </Link>{" "}
            to configure templates for Login and Logout.
          </li>
          <li>2. Paste your WhatsApp, Postmark, and OneSignal credentials into backend/.env.</li>
          <li>3. Turn channels on and send a test notification.</li>
          <li>
            4. Review results in{" "}
            <Link href="/dashboard/notifications/logs" className="text-accent hover:underline">
              Notification Logs
            </Link>
            .
          </li>
        </ol>
      </div>
    </div>
  );
}

function StatCard({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="rounded-2xl border border-border bg-surface p-5">
      <p className="text-xs text-muted">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-ink">{value}</p>
      {hint && <p className="mt-1 text-[11px] text-muted">{hint}</p>}
    </div>
  );
}
