"use client";

import { useEffect, useMemo, useState } from "react";

import { ChannelIcon, CHANNEL_LABELS, StatusBadge } from "@/components/ChannelIcon";
import { EmptyState, LoadingState } from "@/components/Feedback";
import { Badge, Select } from "@/components/Form";
import { api } from "@/lib/api";
import type { Channel, NotificationLog, NotificationStatus, Paginated } from "@/types";

const CHANNEL_OPTIONS: (Channel | "")[] = ["", "WHATSAPP", "EMAIL", "WEB_PUSH"];
const STATUS_OPTIONS: (NotificationStatus | "")[] = ["", "SENT", "FAILED", "PENDING", "SKIPPED"];

export default function NotificationLogsPage() {
  const [logs, setLogs] = useState<NotificationLog[] | null>(null);
  const [channel, setChannel] = useState<Channel | "">("");
  const [status, setStatus] = useState<NotificationStatus | "">("");
  const [triggerCode, setTriggerCode] = useState("");
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams();
    if (channel) params.set("channel", channel);
    if (status) params.set("status", status);
    if (triggerCode) params.set("trigger", triggerCode);
    api
      .get<Paginated<NotificationLog>>(`/api/notifications/logs/?${params.toString()}`)
      .then((d) => setLogs(d.results));
  }, [channel, status, triggerCode]);

  const triggerCodes = useMemo(() => {
    const set = new Set<string>();
    logs?.forEach((l) => l.trigger_code && set.add(l.trigger_code));
    return Array.from(set);
  }, [logs]);

  return (
    <div className="mx-auto max-w-6xl px-5 py-8">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-ink">Notification Logs</h1>
        <p className="mt-1 text-sm text-muted">
          Inspect every notification attempt across every channel and trigger.
        </p>
      </div>

      <div className="mb-5 flex flex-wrap gap-3">
        <Select value={channel} onChange={(e) => setChannel(e.target.value as Channel | "")} className="w-40">
          {CHANNEL_OPTIONS.map((c) => (
            <option key={c} value={c}>
              {c ? CHANNEL_LABELS[c] : "All channels"}
            </option>
          ))}
        </Select>
        <Select value={status} onChange={(e) => setStatus(e.target.value as NotificationStatus | "")} className="w-40">
          {STATUS_OPTIONS.map((s) => (
            <option key={s} value={s}>
              {s || "All statuses"}
            </option>
          ))}
        </Select>
        <Select value={triggerCode} onChange={(e) => setTriggerCode(e.target.value)} className="w-40">
          <option value="">All triggers</option>
          {triggerCodes.map((code) => (
            <option key={code} value={code}>
              {code}
            </option>
          ))}
        </Select>
      </div>

      {!logs ? (
        <LoadingState />
      ) : logs.length === 0 ? (
        <EmptyState title="No notifications logged yet" description="Fire a trigger or send a test to see activity here." />
      ) : (
        <div className="overflow-hidden rounded-2xl border border-border">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="border-b border-border bg-surface text-left text-xs font-medium uppercase tracking-wide text-muted">
                <th className="px-4 py-3">Date</th>
                <th className="px-4 py-3">User</th>
                <th className="px-4 py-3">Trigger</th>
                <th className="px-4 py-3">Channel</th>
                <th className="px-4 py-3">Recipient</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <FragmentRow
                  key={log.id}
                  log={log}
                  expanded={expanded === log.id}
                  onToggle={() => setExpanded((prev) => (prev === log.id ? null : log.id))}
                />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function FragmentRow({
  log,
  expanded,
  onToggle,
}: {
  log: NotificationLog;
  expanded: boolean;
  onToggle: () => void;
}) {
  return (
    <>
      <tr
        onClick={onToggle}
        className="cursor-pointer border-b border-border last:border-0 hover:bg-white/[0.02]"
      >
        <td className="px-4 py-3 text-xs text-muted">{new Date(log.created_at).toLocaleString()}</td>
        <td className="px-4 py-3 text-xs text-ink">{log.user_email || "—"}</td>
        <td className="px-4 py-3">
          <span className="font-mono text-xs text-ink">{log.trigger_code || "—"}</span>
          {log.is_test && (
            <Badge tone="accent" className="ml-2">
              Test
            </Badge>
          )}
        </td>
        <td className="px-4 py-3">
          <span className="inline-flex items-center gap-1.5 text-xs text-ink">
            <ChannelIcon channel={log.channel} className="h-3.5 w-3.5 text-accent" />
            {CHANNEL_LABELS[log.channel]}
          </span>
        </td>
        <td className="px-4 py-3 text-xs text-muted">{log.recipient || "—"}</td>
        <td className="px-4 py-3">
          <StatusBadge status={log.status} />
        </td>
      </tr>
      {expanded && (
        <tr className="border-b border-border bg-surface/50">
          <td colSpan={6} className="px-4 py-4">
            <div className="grid grid-cols-1 gap-3 text-xs sm:grid-cols-2">
              <DetailRow label="Provider message ID" value={log.provider_message_id || "—"} mono />
              <DetailRow label="Subject" value={log.rendered_subject || "—"} />
              {log.error_message && (
                <div className="sm:col-span-2">
                  <p className="mb-1 text-muted">Error</p>
                  <p className="rounded-lg bg-danger/10 px-3 py-2 text-danger">{log.error_message}</p>
                </div>
              )}
            </div>
          </td>
        </tr>
      )}
    </>
  );
}

function DetailRow({ label, value, mono }: { label: string; value: string; mono?: boolean }) {
  return (
    <div>
      <p className="mb-1 text-muted">{label}</p>
      <p className={mono ? "font-mono text-ink" : "text-ink"}>{value}</p>
    </div>
  );
}
