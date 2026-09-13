"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/Button";
import { Input, Textarea } from "@/components/Form";
import { useToast } from "@/hooks/useToast";
import { api, ApiError } from "@/lib/api";
import type { Trigger } from "@/types";

export function AddTriggerModal({
  open,
  onClose,
  onCreated,
}: {
  open: boolean;
  onClose: () => void;
  onCreated: (trigger: Trigger) => void;
}) {
  const { showToast } = useToast();
  const [name, setName] = useState("");
  const [code, setCode] = useState("");
  const [description, setDescription] = useState("");
  const [saving, setSaving] = useState(false);

  if (!open) return null;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      const trigger = await api.post<Trigger>("/api/triggers/", {
        name,
        code,
        description,
        is_active: true,
      });
      showToast("Trigger created.", "success");
      onCreated(trigger);
      setName("");
      setCode("");
      setDescription("");
      onClose();
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : "Unable to create trigger.", "error");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <form
        onSubmit={handleSubmit}
        className="relative w-full max-w-md rounded-2xl border border-border bg-surfaceRaised p-6 shadow-card animate-fade-in"
      >
        <h3 className="text-sm font-semibold text-ink">Add trigger</h3>
        <p className="mt-1 text-xs text-muted">
          New triggers become available to the notification engine immediately — no code changes required.
        </p>

        <div className="mt-5 space-y-4">
          <div>
            <label className="mb-1.5 block text-xs font-medium text-muted">Name</label>
            <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Password Reset" required />
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium text-muted">Code</label>
            <Input
              value={code}
              onChange={(e) => setCode(e.target.value.toUpperCase().replace(/\s+/g, "_"))}
              placeholder="PASSWORD_RESET"
              required
            />
          </div>
          <div>
            <label className="mb-1.5 block text-xs font-medium text-muted">Description</label>
            <Textarea
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Fires when a user requests a password reset."
            />
          </div>
        </div>

        <div className="mt-6 flex justify-end gap-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            Create trigger
          </Button>
        </div>
      </form>
    </div>
  );
}
