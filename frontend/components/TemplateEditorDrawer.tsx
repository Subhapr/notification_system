"use client";

import { useEffect, useRef, useState } from "react";

import { Button } from "@/components/Button";
import { ChannelIcon, CHANNEL_LABELS } from "@/components/ChannelIcon";
import { Drawer } from "@/components/Drawer";
import { Badge, Input, Switch, Textarea } from "@/components/Form";
import { useToast } from "@/hooks/useToast";
import { api, ApiError } from "@/lib/api";
import type { Channel, NotificationTemplate, Trigger } from "@/types";

interface Props {
  open: boolean;
  onClose: () => void;
  trigger: Trigger;
  channel: Channel;
  existing: NotificationTemplate | null;
  onSaved: (template: NotificationTemplate) => void;
}

export function TemplateEditorDrawer({ open, onClose, trigger, channel, existing, onSaved }: Props) {
  const { showToast } = useToast();
  const [name, setName] = useState("");
  const [subject, setSubject] = useState("");
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [enabled, setEnabled] = useState(false);
  const [saving, setSaving] = useState(false);
  const [testRecipient, setTestRecipient] = useState("");
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ ok: boolean; message: string } | null>(null);
  const bodyRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (!open) return;
    setName(existing?.name || `${trigger.name} - ${CHANNEL_LABELS[channel]}`);
    setSubject(existing?.subject || "");
    setTitle(existing?.title || "");
    setBody(existing?.body || "");
    setEnabled(existing?.enabled ?? false);
    setTestResult(null);
    setTestRecipient("");
  }, [open, existing, trigger, channel]);

  function insertVariable(variable: string) {
    const textarea = bodyRef.current;
    const token = `{{${variable}}}`;
    if (!textarea) {
      setBody((prev) => prev + token);
      return;
    }
    const start = textarea.selectionStart ?? body.length;
    const end = textarea.selectionEnd ?? body.length;
    const next = body.slice(0, start) + token + body.slice(end);
    setBody(next);
    requestAnimationFrame(() => {
      textarea.focus();
      textarea.setSelectionRange(start + token.length, start + token.length);
    });
  }

  async function handleSave() {
    setSaving(true);
    try {
      const payload = {
        trigger: trigger.id,
        channel,
        name,
        subject: channel === "EMAIL" ? subject : "",
        title: channel === "WEB_PUSH" ? title : "",
        body,
        enabled,
      };
      const saved = existing
        ? await api.patch<NotificationTemplate>(`/api/notification-templates/${existing.id}/`, payload)
        : await api.post<NotificationTemplate>("/api/notification-templates/", payload);
      showToast("Template saved.", "success");
      onSaved(saved);
      onClose();
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : "Unable to save template.", "error");
    } finally {
      setSaving(false);
    }
  }

  async function handleTestSend() {
    if (!existing) {
      showToast("Save the template before sending a test.", "error");
      return;
    }
    setTesting(true);
    setTestResult(null);
    try {
      await api.post(`/api/notification-templates/${existing.id}/test/`, {
        test_recipient: testRecipient,
      });
      setTestResult({ ok: true, message: "Test notification sent successfully." });
    } catch (err) {
      setTestResult({
        ok: false,
        message: err instanceof ApiError ? err.message : "Test send failed.",
      });
    } finally {
      setTesting(false);
    }
  }

  return (
    <Drawer
      open={open}
      onClose={onClose}
      title={`${existing ? "Edit" : "Create"} template`}
      subtitle={`${trigger.name} · ${CHANNEL_LABELS[channel]}`}
      footer={
        <div className="flex items-center justify-between">
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleSave} loading={saving}>
            Save template
          </Button>
        </div>
      }
    >
      <div className="space-y-5">
        <div className="flex items-center justify-between rounded-xl border border-border bg-surfaceRaised px-4 py-3">
          <div className="flex items-center gap-2">
            <ChannelIcon channel={channel} className="h-4 w-4 text-accent" />
            <span className="text-sm text-ink">Enabled</span>
          </div>
          <Switch checked={enabled} onChange={() => setEnabled((v) => !v)} label="Enable template" />
        </div>

        <Field label="Template name">
          <Input value={name} onChange={(e) => setName(e.target.value)} />
        </Field>

        {channel === "EMAIL" && (
          <Field label="Subject">
            <Input value={subject} onChange={(e) => setSubject(e.target.value)} placeholder="Welcome back to {{site_name}}" />
          </Field>
        )}

        {channel === "WEB_PUSH" && (
          <Field label="Notification title">
            <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Welcome back!" />
          </Field>
        )}

        <Field label="Message body">
          <Textarea
            ref={bodyRef}
            rows={6}
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="Hi {{user_name}}, ..."
          />
        </Field>

        <div>
          <p className="mb-2 text-xs font-medium text-muted">Available variables · click to insert</p>
          <div className="flex flex-wrap gap-1.5">
            {trigger.available_variables.map((variable) => (
              <button
                key={variable}
                type="button"
                onClick={() => insertVariable(variable)}
                className="focus-ring rounded-full border border-borderLight bg-surfaceRaised px-2.5 py-1 font-mono text-[11px] text-accent hover:bg-accent/10"
              >
                {`{{${variable}}}`}
              </button>
            ))}
          </div>
        </div>

        <div className="rounded-xl border border-border bg-surfaceRaised p-4">
          <p className="mb-2 text-xs font-medium text-muted">Send test</p>
          <div className="flex gap-2">
            <Input
              value={testRecipient}
              onChange={(e) => setTestRecipient(e.target.value)}
              placeholder={
                channel === "WHATSAPP"
                  ? "+15551234567"
                  : channel === "EMAIL"
                  ? "you@example.com"
                  : "Uses current browser subscription"
              }
              disabled={channel === "WEB_PUSH"}
            />
            <Button variant="secondary" onClick={handleTestSend} loading={testing}>
              Test
            </Button>
          </div>
          {testResult && (
            <p className={`mt-2 text-xs ${testResult.ok ? "text-success" : "text-danger"}`}>
              {testResult.message}
            </p>
          )}
          {!existing && (
            <p className="mt-2 text-[11px] text-muted">Save the template first to enable test sending.</p>
          )}
        </div>

        {existing && !existing.is_provider_configured && (
          <Badge tone="warning">Provider credentials not configured for this channel yet</Badge>
        )}
      </div>
    </Drawer>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="mb-1.5 block text-xs font-medium text-muted">{label}</label>
      {children}
    </div>
  );
}
