"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { api, clearTokens, getAccessToken, getRefreshToken, setTokens } from "@/lib/api";
import type { User } from "@/types";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  const loadUser = useCallback(async () => {
    if (!getAccessToken()) {
      setLoading(false);
      return;
    }
    try {
      const currentUser = await api.get<User>("/api/auth/me/");
      setUser(currentUser);
    } catch {
      clearTokens();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const login = useCallback(async (email: string, password: string) => {
    const data = await api.post<{ user: User; tokens: { access: string; refresh: string } }>(
      "/api/auth/login/",
      { email, password },
      false
    );
    setTokens(data.tokens.access, data.tokens.refresh);
    setUser(data.user);
  }, []);

  const logout = useCallback(async () => {
    const refresh = getRefreshToken();
    try {
      if (refresh) {
        await api.post("/api/auth/logout/", { refresh });
      }
    } catch {
      // Even if the backend call fails, always clear local session state.
    }
    clearTokens();
    setUser(null);
    router.push("/login");
  }, [router]);

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
