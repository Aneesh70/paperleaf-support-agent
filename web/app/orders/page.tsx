"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getMyOrders, type OrderSummary } from "@/lib/api";
import { useAuth } from "@/lib/auth";

const statusStyle: Record<OrderSummary["status"], string> = {
  Placed: "bg-stone-100 text-stone-700",
  Shipped: "bg-sky-100 text-sky-800",
  Delivered: "bg-emerald-100 text-emerald-800",
  Cancelled: "bg-red-100 text-red-700",
  Returned: "bg-amber-100 text-amber-800",
};

export default function OrdersPage() {
  const { token, name, ready } = useAuth();
  const [orders, setOrders] = useState<OrderSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    getMyOrders(token)
      .then(setOrders)
      .catch((e) => setError(e.message));
  }, [token]);

  if (!ready) return null;
  if (!token) {
    return (
      <p>
        Please{" "}
        <Link href="/login" className="text-emerald-700 underline">
          sign in
        </Link>{" "}
        to see your orders.
      </p>
    );
  }

  return (
    <div>
      <h1 className="mb-1 text-2xl font-bold">My orders</h1>
      <p className="mb-5 text-sm text-stone-500">Signed in as {name}. Ask Paige &ldquo;Where is my order PL-…?&rdquo; to check one.</p>
      {error && <p className="text-sm text-red-600">{error}</p>}
      {!orders && !error && <p className="text-stone-500">Loading…</p>}
      <div className="space-y-3">
        {orders?.map((o) => (
          <div key={o.id} className="flex items-center justify-between rounded-lg border border-stone-200 bg-white p-4">
            <div>
              <div className="font-semibold">{o.id}</div>
              <div className="text-sm text-stone-500">Placed {o.placed_at}</div>
            </div>
            <div className="text-right">
              <div className="font-semibold text-emerald-800">₹{o.total}</div>
              <span className={`rounded-full px-2 py-0.5 text-xs ${statusStyle[o.status]}`}>{o.status}</span>
            </div>
          </div>
        ))}
        {orders?.length === 0 && <p className="text-stone-500">No orders yet.</p>}
      </div>
    </div>
  );
}
