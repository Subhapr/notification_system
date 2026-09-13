export type Channel = "WHATSAPP" | "EMAIL" | "WEB_PUSH";

export type NotificationStatus = "PENDING" | "SENT" | "FAILED" | "SKIPPED";

export interface User {
  id: number;
  email: string;
  full_name: string;
  phone_number: string;
  is_staff: boolean;
  is_active: boolean;
  date_joined: string;
}

export interface Trigger {
  id: number;
  name: string;
  code: string;
  description: string;
  is_active: boolean;
  available_variables: string[];
  created_at: string;
  updated_at: string;
}

export interface NotificationTemplate {
  id: number;
  trigger: number;
  trigger_code: string;
  trigger_name: string;
  channel: Channel;
  name: string;
  subject: string;
  title: string;
  body: string;
  enabled: boolean;
  variable_mapping: string[];
  is_provider_configured: boolean;
  created_at: string;
  updated_at: string;
}

export interface NotificationLog {
  id: string;
  user: number | null;
  user_email: string;
  trigger: number | null;
  trigger_code: string;
  channel: Channel;
  template: number | null;
  status: NotificationStatus;
  recipient: string;
  rendered_subject: string;
  provider_message_id: string;
  provider_response: Record<string, unknown>;
  error_message: string;
  is_test: boolean;
  created_at: string;
}

export interface ApiEnvelope<T> {
  success: boolean;
  message: string;
  data?: T;
  errors?: Record<string, unknown>;
  meta?: Record<string, unknown>;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
