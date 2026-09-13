"use client";

import clsx from "clsx";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { useAuth } from "@/hooks/useAuth";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard", icon: GridIcon },
  { href: "/dashboard/notifications", label: "Notification Settings", icon: BellIcon },
  { href: "/dashboard/notifications/logs", label: "Notification Logs", icon: ListIcon },
  { href: "/dashboard/users", label: "Users", icon: UsersIcon },
  { href: "/dashboard/settings", label: "Settings", icon: GearIcon },
];

export function DashboardShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <div className="flex min-h-screen bg-canvas">
      <aside className="hidden w-64 shrink-0 flex-col border-r border-border bg-surface md:flex">
        <div className="flex items-center gap-2 px-5 py-5">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-accent text-sm font-bold text-white">
            N
          </div>
          <span className="text-sm font-semibold tracking-tight text-ink">NotifyHub</span>
        </div>
        <nav className="flex-1 space-y-1 px-3">
          {NAV_ITEMS.map((item) => {
            const active =
              item.href === "/dashboard" ? pathname === item.href : pathname.startsWith(item.href);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={clsx(
                  "focus-ring flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition-colors",
                  active
                    ? "bg-accent/12 text-accent"
                    : "text-muted hover:bg-white/5 hover:text-ink"
                )}
              >
                <Icon className="h-4 w-4 shrink-0" />
                {item.label}
              </Link>
            );
          })}
        </nav>
        <div className="border-t border-border px-4 py-4">
          <div className="mb-2 flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-surfaceRaised text-xs font-medium text-ink">
              {user?.email?.[0]?.toUpperCase() ?? "?"}
            </div>
            <div className="min-w-0">
              <p className="truncate text-xs font-medium text-ink">{user?.full_name || user?.email}</p>
              <p className="truncate text-[11px] text-muted">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={logout}
            className="focus-ring w-full rounded-lg px-3 py-1.5 text-left text-xs text-muted hover:bg-white/5 hover:text-ink"
          >
            Sign out
          </button>
        </div>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-border bg-surface/60 px-5 py-3.5 backdrop-blur md:hidden">
          <span className="text-sm font-semibold text-ink">NotifyHub</span>
          <button onClick={logout} className="text-xs text-muted">
            Sign out
          </button>
        </header>
        <main className="flex-1 overflow-y-auto">{children}</main>
      </div>
    </div>
  );
}

function GridIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" fill="none" {...props}>
      <rect x="3" y="3" width="8" height="8" rx="1.5" stroke="currentColor" strokeWidth="1.6" />
      <rect x="13" y="3" width="8" height="8" rx="1.5" stroke="currentColor" strokeWidth="1.6" />
      <rect x="3" y="13" width="8" height="8" rx="1.5" stroke="currentColor" strokeWidth="1.6" />
      <rect x="13" y="13" width="8" height="8" rx="1.5" stroke="currentColor" strokeWidth="1.6" />
    </svg>
  );
}
function BellIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" fill="none" {...props}>
      <path
        d="M6 8a6 6 0 1112 0c0 4 1.5 5.5 1.5 5.5h-15S6 12 6 8z"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
      <path d="M9.5 17a2.5 2.5 0 005 0" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}
function ListIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" fill="none" {...props}>
      <path d="M8 6h13M8 12h13M8 18h13" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <circle cx="3.5" cy="6" r="1.3" fill="currentColor" />
      <circle cx="3.5" cy="12" r="1.3" fill="currentColor" />
      <circle cx="3.5" cy="18" r="1.3" fill="currentColor" />
    </svg>
  );
}
function UsersIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" fill="none" {...props}>
      <circle cx="9" cy="8" r="3" stroke="currentColor" strokeWidth="1.6" />
      <path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <path d="M16 8a3 3 0 010 6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
      <path d="M15 14c2.8.3 5 2.7 5 6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    </svg>
  );
}
function GearIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 24 24" fill="none" {...props}>
      <circle cx="12" cy="12" r="3" stroke="currentColor" strokeWidth="1.6" />
      <path
        d="M19 12a7 7 0 00-.1-1.2l2-1.5-2-3.4-2.3.9a7 7 0 00-2-1.2L14.2 3H9.8l-.4 2.6a7 7 0 00-2 1.2l-2.3-.9-2 3.4 2 1.5A7 7 0 005 12c0 .4 0 .8.1 1.2l-2 1.5 2 3.4 2.3-.9c.6.5 1.3.9 2 1.2l.4 2.6h4.4l.4-2.6a7 7 0 002-1.2l2.3.9 2-3.4-2-1.5c.1-.4.1-.8.1-1.2z"
        stroke="currentColor"
        strokeWidth="1.3"
        strokeLinejoin="round"
      />
    </svg>
  );
}
