import type { ApiEnvelope } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

const ACCESS_TOKEN_KEY = "nh_access_token";
const REFRESH_TOKEN_KEY = "nh_refresh_token";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function setTokens(access: string, refresh?: string) {
  window.localStorage.setItem(ACCESS_TOKEN_KEY, access);
  if (refresh) window.localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
}

export function clearTokens() {
  window.localStorage.removeItem(ACCESS_TOKEN_KEY);
  window.localStorage.removeItem(REFRESH_TOKEN_KEY);
}

export class ApiError extends Error {
  status: number;
  errors?: Record<string, unknown>;

  constructor(message: string, status: number, errors?: Record<string, unknown>) {
    super(message);
    this.status = status;
    this.errors = errors;
  }
}

async function refreshAccessToken(): Promise<string | null> {
  const refresh = getRefreshToken();
  if (!refresh) return null;

  const response = await fetch(`${API_BASE_URL}/api/auth/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  });

  if (!response.ok) {
    clearTokens();
    return null;
  }

  const body: ApiEnvelope<{ access: string }> = await response.json();
  const access = body.data?.access;
  if (access) {
    setTokens(access);
    return access;
  }
  return null;
}

interface RequestOptions {
  method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  body?: unknown;
  auth?: boolean;
}

export async function apiRequest<T>(
  path: string,
  { method = "GET", body, auth = true }: RequestOptions = {}
): Promise<T> {
  const doFetch = async (accessToken: string | null) => {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    if (auth && accessToken) headers.Authorization = `Bearer ${accessToken}`;

    return fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  };

  let response = await doFetch(getAccessToken());

  if (response.status === 401 && auth) {
    const newAccess = await refreshAccessToken();
    if (newAccess) {
      response = await doFetch(newAccess);
    }
  }

  let payload: ApiEnvelope<T> | undefined;
  try {
    payload = await response.json();
  } catch {
    payload = undefined;
  }

  if (!response.ok || !payload?.success) {
    throw new ApiError(
      payload?.message || "Request failed.",
      response.status,
      payload?.errors
    );
  }

  return payload.data as T;
}

export const api = {
  get: <T>(path: string) => apiRequest<T>(path),
  post: <T>(path: string, body?: unknown, auth = true) =>
    apiRequest<T>(path, { method: "POST", body, auth }),
  patch: <T>(path: string, body?: unknown) => apiRequest<T>(path, { method: "PATCH", body }),
  put: <T>(path: string, body?: unknown) => apiRequest<T>(path, { method: "PUT", body }),
  delete: <T>(path: string) => apiRequest<T>(path, { method: "DELETE" }),
};
