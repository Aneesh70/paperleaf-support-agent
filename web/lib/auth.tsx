"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { login as apiLogin } from "./api";

type Auth = {
  token: string | null;
  name: string | null;
  ready: boolean;
  signIn: (email: string) => Promise<void>;
  signOut: () => void;
};

const AuthContext = createContext<Auth | null>(null);
const KEY = "paperleaf_auth";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [name, setName] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    // Read the saved sign-in once after the first render (localStorage is not available on the server).
    try {
      const saved = JSON.parse(localStorage.getItem(KEY) ?? "null");
      if (saved?.token) {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setToken(saved.token);
        setName(saved.name);
      }
    } catch {}
    setReady(true);
  }, []);

  const signIn = useCallback(async (email: string) => {
    const res = await apiLogin(email);
    setToken(res.token);
    setName(res.name);
    localStorage.setItem(KEY, JSON.stringify(res));
  }, []);

  const signOut = useCallback(() => {
    setToken(null);
    setName(null);
    localStorage.removeItem(KEY);
  }, []);

  return <AuthContext.Provider value={{ token, name, ready, signIn, signOut }}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
