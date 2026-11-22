"use client";

import { useCallback, useEffect, useState } from "react";
import {
  adminLogin,
  adminSetStatus,
  adminStats,
  adminTickets,
  type Stats,
  type Ticket,
  type TicketStatus,
} from "@/lib/api";
import StatTile from "@/components/charts/StatTile";
import BarList from "@/components/charts/BarList";
import DailyColumns from "@/components/charts/DailyColumns";

const KEY = "paperleaf_admin_token";
const STATUS_LABEL: Record<TicketStatus, string> = { open: "Open", in_progress: "In progress", closed: "Closed" };
const FILTERS: ("all" | TicketStatus)[] = ["all", "open", "in_progress", "closed"];

export default function AdminPage() {
  const [token, setToken] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    // Read the saved staff sign-in once after the first render (sessionStorage is not available on the server).
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setToken(sessionStorage.getItem(KEY));
    setReady(true);
  }, []);

  if (!ready) return null;
  if (!token) {
    return (
      <PasscodeForm
        onDone={(t) => {
          sessionStorage.setItem(KEY, t);
          setToken(t);
        }}
      />
    );
  }
  return (
    <Dashboard
      token={token}
      onSignOut={() => {
        sessionStorage.removeItem(KEY);
        setToken(null);
      }}
    />
  );
}

function PasscodeForm({ onDone }: { onDone: (token: string) => void }) {
  const [passcode, setPasscode] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      onDone((await adminLogin(passcode)).token);
    } catch {
      setError("Wrong passcode.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-sm">
      <h1 className="mb-4 text-2xl font-bold">Staff dashboard</h1>
      <form onSubmit={submit} className="space-y-3 rounded-xl border border-stone-200 bg-white p-5 shadow-sm">
        <label className="block text-sm font-medium">
          Staff passcode
          <input
            type="password"
            required
            value={passcode}
            onChange={(e) => setPasscode(e.target.value)}
            className="mt-1 w-full rounded border border-stone-300 px-3 py-2 outline-none focus:border-emerald-600"
          />
        </label>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button disabled={busy} className="w-full rounded bg-emerald-700 py-2 text-white hover:bg-emerald-800 disabled:opacity-60">
          {busy ? "Checking…" : "Open dashboard"}
        </button>
      </form>
    </div>
  );
}

function Dashboard({ token, onSignOut }: { token: string; onSignOut: () => void }) {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [filter, setFilter] = useState<"all" | TicketStatus>("all");
  const [error, setError] = useState<string | null>(null);
  const [loaded, setLoaded] = useState(false);

  const load = useCallback(() => {
    Promise.all([adminTickets(token), adminStats(token)])
      .then(([t, s]) => {
        setTickets(t);
        setStats(s);
        setError(null);
        setLoaded(true);
      })
      .catch((e: Error) => {
        if (/sign-in required/i.test(e.message)) onSignOut();
        else setError(e.message);
      });
  }, [token, onSignOut]);

  useEffect(() => {
    load();
    const id = setInterval(load, 10000); // pick up new tickets raised by Paige
    return () => clearInterval(id);
  }, [load]);

  async function changeStatus(t: Ticket, status: TicketStatus) {
    setTickets((all) => all.map((x) => (x.ticket_id === t.ticket_id ? { ...x, status } : x))); // optimistic
    try {
      await adminSetStatus(token, t.ticket_id, status);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not update the ticket.");
    }
    load();
  }

  const shown = tickets.filter((t) => filter === "all" || t.status === filter);

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Staff dashboard</h1>
          <p className="text-sm text-stone-500">Tickets raised by Paige. Refreshes every 10 seconds.</p>
        </div>
        <button onClick={onSignOut} className="rounded border border-stone-300 bg-white px-3 py-1 text-sm hover:bg-stone-100">
          Sign out
        </button>
      </div>

      {error && <p className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">{error}</p>}

      {stats && (
        <>
          <section className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <StatTile label="Open tickets" value={stats.by_status.open} />
            <StatTile label="In progress" value={stats.by_status.in_progress} />
            <StatTile
              label="High priority, not closed"
              value={stats.open_by_priority.high}
              note={stats.open_by_priority.high > 0 ? "▲ Needs attention first" : "None waiting"}
            />
            <StatTile label="All tickets" value={stats.total} note={`${stats.by_status.closed} closed`} />
          </section>

          <section className="grid gap-6 md:grid-cols-2">
            <div className="rounded-lg border border-stone-200 bg-white p-4">
              <h2 className="mb-3 font-semibold">Tickets by reason</h2>
              <BarList
                rows={stats.by_reason.map((r) => ({ label: r.reason, value: r.count }))}
                emptyText="No tickets yet. Chat with Paige to raise one."
              />
            </div>
            <div className="rounded-lg border border-stone-200 bg-white p-4">
              <h2 className="mb-3 font-semibold">Tickets per day (last 7 days)</h2>
              <DailyColumns data={stats.per_day} />
            </div>
          </section>
        </>
      )}

      <section>
        <div className="mb-3 flex flex-wrap items-center gap-2">
          <h2 className="mr-2 font-semibold">All tickets</h2>
          {FILTERS.map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`rounded-full border px-3 py-1 text-xs ${
                filter === f ? "border-emerald-700 bg-emerald-700 text-white" : "border-stone-300 bg-white text-stone-700 hover:bg-stone-100"
              }`}
            >
              {f === "all" ? "All" : STATUS_LABEL[f]}
            </button>
          ))}
        </div>

        <div className="overflow-x-auto rounded-lg border border-stone-200 bg-white">
          <table className="w-full text-left text-sm">
            <thead className="bg-stone-50 text-xs uppercase text-stone-500">
              <tr>
                <th className="px-3 py-2">Ticket</th>
                <th className="px-3 py-2">Priority</th>
                <th className="px-3 py-2">Customer message</th>
                <th className="px-3 py-2">Reason</th>
                <th className="px-3 py-2">Raised</th>
                <th className="px-3 py-2">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100">
              {shown.map((t) => (
                <tr key={t.ticket_id} className="align-top">
                  <td className="px-3 py-2 font-medium">{t.ticket_id}</td>
                  <td className="px-3 py-2">
                    {t.priority === "high" ? (
                      <span className="rounded bg-red-50 px-2 py-0.5 text-xs font-medium text-red-700">▲ High</span>
                    ) : (
                      <span className="rounded bg-stone-100 px-2 py-0.5 text-xs text-stone-700">Normal</span>
                    )}
                  </td>
                  <td className="max-w-xs px-3 py-2 text-stone-700">{t.customer_message}</td>
                  <td className="px-3 py-2 text-stone-600">{t.reason}</td>
                  <td className="whitespace-nowrap px-3 py-2 text-stone-500">{t.time}</td>
                  <td className="px-3 py-2">
                    <select
                      value={t.status}
                      onChange={(e) => changeStatus(t, e.target.value as TicketStatus)}
                      aria-label={`Status of ${t.ticket_id}`}
                      className="rounded border border-stone-300 bg-white px-2 py-1 text-xs"
                    >
                      {(Object.keys(STATUS_LABEL) as TicketStatus[]).map((s) => (
                        <option key={s} value={s}>
                          {STATUS_LABEL[s]}
                        </option>
                      ))}
                    </select>
                  </td>
                </tr>
              ))}
              {loaded && shown.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-3 py-6 text-center text-stone-500">
                    No tickets here.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
