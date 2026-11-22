"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { useAuth } from "@/lib/auth";

const DEMO = [
  "aarav.mehta@example.com",
  "diya.nair@example.com",
  "rohan.iyer@example.com",
];

export default function LoginPage() {
  const { signIn } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await signIn(email, password);
      router.push("/orders");
    } catch {
      setError("Wrong email or password.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-sm">
      <h1 className="mb-4 text-2xl font-bold">Sign in</h1>
      <form onSubmit={submit} className="space-y-3 rounded-xl border border-stone-200 bg-white p-5 shadow-sm">
        <label className="block text-sm font-medium">
          Email
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full rounded border border-stone-300 px-3 py-2 outline-none focus:border-emerald-600"
          />
        </label>
        <label className="block text-sm font-medium">
          Password
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full rounded border border-stone-300 px-3 py-2 outline-none focus:border-emerald-600"
          />
        </label>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button disabled={busy} className="w-full rounded bg-emerald-700 py-2 text-white hover:bg-emerald-800 disabled:opacity-60">
          {busy ? "Signing in…" : "Sign in"}
        </button>
      </form>
      <div className="mt-4 rounded-lg bg-amber-50 p-4 text-sm text-amber-900">
        <p className="mb-2 font-medium">Demo accounts (made-up customers). Password for all: paperleaf123</p>
        <ul className="space-y-1">
          {DEMO.map((d) => (
            <li key={d}>
              <button type="button" onClick={() => {
                  setEmail(d);
                  setPassword("paperleaf123");
                }} className="underline">
                {d}
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
