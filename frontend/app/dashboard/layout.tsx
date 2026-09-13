"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { DashboardShell } from "@/components/DashboardShell";
import { LoadingState } from "@/components/Feedback";
import { useAuth } from "@/hooks/useAuth";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [loading, user, router]);

  if (loading || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-canvas">
        <LoadingState label="Checking your session…" />
      </div>
    );
  }

  if (!user.is_staff) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-canvas px-4">
        <div className="max-w-sm rounded-2xl border border-border bg-surface p-6 text-center shadow-card">
          <p className="text-sm font-medium text-ink">Admin access required</p>
          <p className="mt-1 text-xs text-muted">
            Your account doesn&apos;t have permission to manage notifications.
          </p>
        </div>
      </div>
    );
  }

  return <DashboardShell>{children}</DashboardShell>;
}
