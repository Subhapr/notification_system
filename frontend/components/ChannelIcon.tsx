import type { Channel, NotificationStatus } from "@/types";
import { Badge } from "@/components/Form";

export const CHANNEL_LABELS: Record<Channel, string> = {
  WHATSAPP: "WhatsApp",
  EMAIL: "Email",
  WEB_PUSH: "Web Push",
};

export function ChannelIcon({ channel, className }: { channel: Channel; className?: string }) {
  if (channel === "WHATSAPP") {
    return (
      <svg viewBox="0 0 24 24" fill="none" className={className}>
        <path
          d="M6.5 17.5L4 20l2.6-2.4A8 8 0 1112 20a8 8 0 01-5.5-2.5z"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinejoin="round"
        />
        <path
          d="M9 9.5c.3 2.5 2 4.2 4.5 4.5.5 0 1-.2 1.2-.7l.3-.7-2-1-.5.6c-1-.4-1.7-1.1-2.1-2l.6-.5-1-2-.7.3c-.5.2-.7.8-.6 1.3z"
          fill="currentColor"
        />
      </svg>
    );
  }
  if (channel === "EMAIL") {
    return (
      <svg viewBox="0 0 24 24" fill="none" className={className}>
        <rect x="3.5" y="5.5" width="17" height="13" rx="2" stroke="currentColor" strokeWidth="1.5" />
        <path d="M4.5 7l7.5 6 7.5-6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    );
  }
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className}>
      <path
        d="M6 8a6 6 0 1112 0c0 4 1.5 5.5 1.5 5.5h-15S6 12 6 8z"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinejoin="round"
      />
      <path d="M9.5 17a2.5 2.5 0 005 0" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}

export function StatusBadge({ status }: { status: NotificationStatus }) {
  const map: Record<NotificationStatus, { tone: "success" | "danger" | "warning" | "muted"; label: string }> = {
    SENT: { tone: "success", label: "Sent" },
    FAILED: { tone: "danger", label: "Failed" },
    PENDING: { tone: "warning", label: "Pending" },
    SKIPPED: { tone: "muted", label: "Skipped" },
  };
  const { tone, label } = map[status];
  return <Badge tone={tone}>{label}</Badge>;
}
