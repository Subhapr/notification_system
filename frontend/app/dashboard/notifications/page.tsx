"use client";

import { useEffect, useMemo, useState } from "react";

import { AddTriggerModal } from "@/components/AddTriggerModal";
import { Button } from "@/components/Button";
import { ChannelIcon, CHANNEL_LABELS } from "@/components/ChannelIcon";
import { EmptyState, LoadingState } from "@/components/Feedback";
import { Badge, Input, Switch } from "@/components/Form";
import { TemplateEditorDrawer } from "@/components/TemplateEditorDrawer";
import { useToast } from "@/hooks/useToast";
import { api, ApiError } from "@/lib/api";
import type { Channel, NotificationTemplate, Paginated, Trigger } from "@/types";

const CHANNELS: Channel[] = ["WHATSAPP", "EMAIL", "WEB_PUSH"];

export default function NotificationSettingsPage() {
  const { showToast } = useToast();
  const [triggers, setTriggers] = useState<Trigger[] | null>(null);
  const [templates, setTemplates] = useState<NotificationTemplate[] | null>(null);
  const [search, setSearch] = useState("");
  const [addTriggerOpen, setAddTriggerOpen] = useState(false);
  const [editorState, setEditorState] = useState<{
    trigger: Trigger;
    channel: Channel;
    existing: NotificationTemplate | null;
  } | null>(null);

  async function loadAll() {
    const [triggerData, templateData] = await Promise.all([
      api.get<Paginated<Trigger>>("/api/triggers/"),
      api.get<Paginated<NotificationTemplate>>("/api/notification-templates/"),
    ]);
    setTriggers(triggerData.results);
    setTemplates(templateData.results);
  }

  useEffect(() => {
    loadAll();
  }, []);

  const templateMap = useMemo(() => {
    const map = new Map<string, NotificationTemplate>();
    templates?.forEach((t) => map.set(`${t.trigger}:${t.channel}`, t));
    return map;
  }, [templates]);

  const filteredTriggers = useMemo(() => {
    if (!triggers) return [];
    const q = search.trim().toLowerCase();
    if (!q) return triggers;
    return triggers.filter(
      (t) => t.name.toLowerCase().includes(q) || t.code.toLowerCase().includes(q)
    );
  }, [triggers, search]);

  function getTemplate(triggerId: number, channel: Channel) {
    return templateMap.get(`${triggerId}:${channel}`) || null;
  }

  function openEditor(trigger: Trigger, channel: Channel) {
    setEditorState({ trigger, channel, existing: getTemplate(trigger.id, channel) });
  }

  function handleTemplateSaved(saved: NotificationTemplate) {
    setTemplates((prev) => {
      if (!prev) return prev;
      const exists = prev.some((t) => t.id === saved.id);
      return exists ? prev.map((t) => (t.id === saved.id ? saved : t)) : [...prev, saved];
    });
  }

  async function handleToggle(template: NotificationTemplate | null, trigger: Trigger, channel: Channel) {
    if (!template) {
      openEditor(trigger, channel);
      return;
    }
    const optimistic = { ...template, enabled: !template.enabled };
    setTemplates((prev) => prev?.map((t) => (t.id === template.id ? optimistic : t)) ?? prev);
    try {
      const updated = await api.post<NotificationTemplate>(
        `/api/notification-templates/${template.id}/toggle/`
      );
      setTemplates((prev) => prev?.map((t) => (t.id === updated.id ? updated : t)) ?? prev);
    } catch (err) {
      setTemplates((prev) => prev?.map((t) => (t.id === template.id ? template : t)) ?? prev);
      showToast(err instanceof ApiError ? err.message : "Unable to toggle channel.", "error");
    }
  }

  if (!triggers || !templates) {
    return <LoadingState />;
  }

  return (
    <div className="mx-auto max-w-6xl px-5 py-8">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-xl font-semibold text-ink">Notification Settings</h1>
          <p className="mt-1 text-sm text-muted">
            Manage WhatsApp, Email, and Web Push templates for every trigger — no provider
            dashboards required.
          </p>
        </div>
        <div className="flex gap-2">
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search triggers…"
            className="w-48"
          />
          <Button onClick={() => setAddTriggerOpen(true)}>Add trigger</Button>
        </div>
      </div>

      {filteredTriggers.length === 0 ? (
        <EmptyState
          title="No triggers yet"
          description="Add your first trigger (e.g. Login) to start configuring notification templates."
          action={<Button onClick={() => setAddTriggerOpen(true)}>Add trigger</Button>}
        />
      ) : (
        <>
          {/* Desktop / tablet matrix */}
          <div className="hidden overflow-hidden rounded-2xl border border-border md:block">
            <table className="w-full border-collapse text-sm">
              <thead>
                <tr className="border-b border-border bg-surface">
                  <th className="w-48 px-5 py-3 text-left text-xs font-medium uppercase tracking-wide text-muted">
                    Trigger
                  </th>
                  {CHANNELS.map((channel) => (
                    <th key={channel} className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wide text-muted">
                      <span className="inline-flex items-center gap-1.5">
                        <ChannelIcon channel={channel} className="h-3.5 w-3.5" />
                        {CHANNEL_LABELS[channel]}
                      </span>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filteredTriggers.map((trigger) => (
                  <tr key={trigger.id} className="border-b border-border last:border-0 hover:bg-white/[0.02]">
                    <td className="px-5 py-4 align-top">
                      <p className="text-sm font-medium text-ink">{trigger.name}</p>
                      <p className="mt-0.5 font-mono text-[11px] text-muted">{trigger.code}</p>
                      {!trigger.is_active && (
                        <Badge tone="muted" className="mt-1.5">
                          Inactive
                        </Badge>
                      )}
                    </td>
                    {CHANNELS.map((channel) => {
                      const template = getTemplate(trigger.id, channel);
                      return (
                        <td key={channel} className="px-4 py-4 align-top">
                          <ChannelCell
                            template={template}
                            onEdit={() => openEditor(trigger, channel)}
                            onToggle={() => handleToggle(template, trigger, channel)}
                          />
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Mobile: accordion of channel cards per trigger */}
          <div className="space-y-4 md:hidden">
            {filteredTriggers.map((trigger) => (
              <div key={trigger.id} className="rounded-2xl border border-border bg-surface p-4">
                <div className="mb-3 flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-ink">{trigger.name}</p>
                    <p className="font-mono text-[11px] text-muted">{trigger.code}</p>
                  </div>
                  {!trigger.is_active && <Badge tone="muted">Inactive</Badge>}
                </div>
                <div className="space-y-2">
                  {CHANNELS.map((channel) => {
                    const template = getTemplate(trigger.id, channel);
                    return (
                      <div key={channel} className="rounded-xl border border-border bg-surfaceRaised p-3">
                        <ChannelCell
                          compact
                          template={template}
                          onEdit={() => openEditor(trigger, channel)}
                          onToggle={() => handleToggle(template, trigger, channel)}
                          channelFallback={channel}
                        />
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      <AddTriggerModal
        open={addTriggerOpen}
        onClose={() => setAddTriggerOpen(false)}
        onCreated={(trigger) => setTriggers((prev) => (prev ? [...prev, trigger] : [trigger]))}
      />

      {editorState && (
        <TemplateEditorDrawer
          open={!!editorState}
          onClose={() => setEditorState(null)}
          trigger={editorState.trigger}
          channel={editorState.channel}
          existing={editorState.existing}
          onSaved={handleTemplateSaved}
        />
      )}
    </div>
  );
}

function ChannelCell({
  template,
  onEdit,
  onToggle,
  compact,
  channelFallback,
}: {
  template: NotificationTemplate | null;
  onEdit: () => void;
  onToggle: () => void;
  compact?: boolean;
  channelFallback?: Channel;
}) {
  const channel = template?.channel ?? channelFallback;

  return (
    <div className={compact ? "" : "rounded-xl border border-border bg-surface p-3"}>
      <div className="mb-2 flex items-center justify-between">
        {compact && channel && (
          <span className="inline-flex items-center gap-1.5 text-xs font-medium text-ink">
            <ChannelIcon channel={channel} className="h-3.5 w-3.5 text-accent" />
            {CHANNEL_LABELS[channel]}
          </span>
        )}
        {template ? (
          <Badge tone={template.enabled ? "success" : "muted"}>
            {template.enabled ? "Configured · On" : "Configured · Off"}
          </Badge>
        ) : (
          <Badge tone="muted">Not set</Badge>
        )}
      </div>

      {template ? (
        <p className="mb-2 line-clamp-2 text-xs text-muted">
          {template.body || template.title || "(empty body)"}
        </p>
      ) : (
        <p className="mb-2 text-xs text-muted">No template configured for this channel yet.</p>
      )}

      {template && !template.is_provider_configured && (
        <p className="mb-2 text-[11px] text-warning">Provider not configured</p>
      )}

      <div className="flex items-center gap-2">
        <Button size="sm" variant="secondary" onClick={onEdit}>
          {template ? "Edit" : "Create"}
        </Button>
        {template && (
          <div className="ml-auto flex items-center gap-1.5">
            <span className="text-[11px] text-muted">{template.enabled ? "On" : "Off"}</span>
            <Switch checked={template.enabled} onChange={onToggle} label="Toggle channel" />
          </div>
        )}
      </div>
    </div>
  );
}
