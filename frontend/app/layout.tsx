import type { Metadata } from "next";
import "./globals.css";

import { AuthProvider } from "@/hooks/useAuth";
import { ToastProvider } from "@/hooks/useToast";

export const metadata: Metadata = {
  title: "NotifyHub — Notification Management",
  description: "Manage WhatsApp, Email, and Web Push notifications from one screen.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        <ToastProvider>
          <AuthProvider>{children}</AuthProvider>
        </ToastProvider>
      </body>
    </html>
  );
}
