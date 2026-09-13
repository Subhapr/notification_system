"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/hooks/useAuth";
import { LoadingState } from "@/components/Feedback";

export default function RootPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (loading) return;
    router.replace(user ? "/dashboard" : "/login");
  }, [loading, user, router]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-canvas">
      <LoadingState label="Loading NotifyHub…" />
    </div>
  );
}
