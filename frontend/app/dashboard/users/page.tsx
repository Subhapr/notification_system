"use client";

import { useEffect, useState } from "react";

import { Badge } from "@/components/Form";
import { EmptyState, LoadingState } from "@/components/Feedback";
import { api } from "@/lib/api";
import type { Paginated, User } from "@/types";

export default function UsersPage() {
  const [users, setUsers] = useState<User[] | null>(null);

  useEffect(() => {
    api.get<Paginated<User>>("/api/auth/users/").then((d) => setUsers(d.results));
  }, []);

  return (
    <div className="mx-auto max-w-6xl px-5 py-8">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-ink">Users</h1>
        <p className="mt-1 text-sm text-muted">
          Everyone who can sign in. Only staff accounts can manage notifications.
        </p>
      </div>

      {!users ? (
        <LoadingState />
      ) : users.length === 0 ? (
        <EmptyState title="No users yet" />
      ) : (
        <div className="overflow-hidden rounded-2xl border border-border">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="border-b border-border bg-surface text-left text-xs font-medium uppercase tracking-wide text-muted">
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Email</th>
                <th className="px-4 py-3">Phone</th>
                <th className="px-4 py-3">Role</th>
                <th className="px-4 py-3">Joined</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-b border-border last:border-0 hover:bg-white/[0.02]">
                  <td className="px-4 py-3 text-ink">{u.full_name || "—"}</td>
                  <td className="px-4 py-3 text-muted">{u.email}</td>
                  <td className="px-4 py-3 text-muted">{u.phone_number || "—"}</td>
                  <td className="px-4 py-3">
                    <Badge tone={u.is_staff ? "accent" : "muted"}>{u.is_staff ? "Admin" : "User"}</Badge>
                  </td>
                  <td className="px-4 py-3 text-muted">{new Date(u.date_joined).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
