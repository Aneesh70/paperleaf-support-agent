"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { PAYMENT_METHODS, placeOrder, quoteOrder, type PlacedOrder, type Pricing } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import BookCover from "@/components/BookCover";
import { useCart } from "@/lib/cart";

export default function CartPage() {
  const { lines, subtotal, setQty, remove, clear } = useCart();
  const { token, name, ready } = useAuth();
  const [payment, setPayment] = useState<string>(PAYMENT_METHODS[0]);
  const [pricing, setPricing] = useState<Pricing | null>(null);
  const [problem, setProblem] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [placed, setPlaced] = useState<PlacedOrder | null>(null);

  // Ask the API for the exact price (delivery and cash-on-delivery rules) whenever the cart or payment changes.
  const itemsKey = lines.map((l) => `${l.bookId}x${l.qty}`).join(",");
  useEffect(() => {
    if (lines.length === 0) return;
    let cancelled = false;
    quoteOrder(lines.map((l) => ({ book_id: l.bookId, qty: l.qty })), payment)
      .then((p) => {
        if (cancelled) return;
        setPricing(p);
        setProblem(null);
      })
      .catch((e: Error) => {
        if (cancelled) return;
        setPricing(null);
        setProblem(e.message);
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [itemsKey, payment]);

  async function checkout() {
    if (!token) return;
    setBusy(true);
    setProblem(null);
    try {
      const order = await placeOrder(lines.map((l) => ({ book_id: l.bookId, qty: l.qty })), payment, token);
      setPlaced(order);
      clear();
    } catch (e) {
      setProblem(e instanceof Error ? e.message : "Could not place the order. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  if (placed) {
    return (
      <div className="mx-auto max-w-lg rounded-xl border border-emerald-200 bg-white p-6 shadow-sm">
        <h1 className="text-2xl font-bold text-emerald-900">Order placed 🎉</h1>
        <p className="mt-2 text-stone-800">
          Thank you{name ? `, ${name.split(" ")[0]}` : ""}! Your order number is <strong>{placed.order_id}</strong>.
        </p>
        <ul className="mt-4 divide-y divide-stone-200 text-sm text-stone-800">
          {placed.items.map((i) => (
            <li key={i.book_id} className="flex justify-between py-2">
              <span>
                {i.title} × {i.qty}
              </span>
              <span>₹{i.price * i.qty}</span>
            </li>
          ))}
        </ul>
        <div className="mt-3 space-y-1 text-sm text-stone-800">
          <Row label="Delivery" value={placed.delivery_fee === 0 ? "Free" : `₹${placed.delivery_fee}`} />
          {placed.cod_fee > 0 && <Row label="Cash on delivery fee" value={`₹${placed.cod_fee}`} />}
          <Row label={`Total (${placed.payment_method})`} value={`₹${placed.total}`} bold />
        </div>
        <p className="mt-4 text-sm text-stone-700">
          This is a demo store, so no real payment was taken. You can ask Paige &ldquo;Where is my order {placed.order_id}?&rdquo;
        </p>
        <div className="mt-5 flex gap-3">
          <Link href="/orders" className="rounded bg-emerald-700 px-4 py-2 text-white hover:bg-emerald-800">
            View my orders
          </Link>
          <Link href="/books" className="rounded border border-stone-300 px-4 py-2 text-stone-800 hover:bg-stone-100">
            Keep shopping
          </Link>
        </div>
      </div>
    );
  }

  if (lines.length === 0) {
    return (
      <div>
        <h1 className="mb-3 text-2xl font-bold">Your cart</h1>
        <p className="mb-4 text-stone-700">Your cart is empty.</p>
        <Link href="/books" className="rounded bg-emerald-700 px-4 py-2 text-white hover:bg-emerald-800">
          Browse books
        </Link>
      </div>
    );
  }

  return (
    <div className="grid gap-8 md:grid-cols-[1fr_20rem]">
      <section>
        <h1 className="mb-4 text-2xl font-bold">Your cart</h1>
        <ul className="space-y-3">
          {lines.map((l) => (
            <li key={l.bookId} className="flex items-center justify-between gap-3 rounded-lg border border-stone-200 bg-white p-4">
              <BookCover id={l.bookId} title={l.title} author={l.author} coverUrl={l.coverUrl} size="thumb" />
              <div className="min-w-0 flex-1">
                <Link href={`/books/${l.bookId}`} className="block truncate font-semibold text-stone-900 hover:underline">
                  {l.title}
                </Link>
                <div className="text-sm text-stone-700">
                  {l.author} · ₹{l.price}
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex items-center rounded border border-stone-300 text-stone-900">
                  <button aria-label="Fewer" onClick={() => setQty(l.bookId, l.qty - 1)} disabled={l.qty <= 1} className="px-2 py-1 hover:bg-stone-100 disabled:opacity-40">
                    −
                  </button>
                  <span className="min-w-8 text-center text-sm">{l.qty}</span>
                  <button aria-label="More" onClick={() => setQty(l.bookId, l.qty + 1)} disabled={l.qty >= Math.min(10, l.stock)} className="px-2 py-1 hover:bg-stone-100 disabled:opacity-40">
                    +
                  </button>
                </div>
                <div className="w-16 text-right font-semibold text-emerald-900">₹{l.price * l.qty}</div>
                <button onClick={() => remove(l.bookId)} className="text-sm text-red-700 underline">
                  Remove
                </button>
              </div>
            </li>
          ))}
        </ul>
      </section>

      <aside className="h-fit rounded-xl border border-stone-200 bg-white p-5 shadow-sm">
        <h2 className="mb-3 font-semibold">Order summary</h2>
        <label className="mb-3 block text-sm font-medium text-stone-800">
          Payment method
          <select value={payment} onChange={(e) => setPayment(e.target.value)} className="mt-1 w-full rounded border border-stone-300 px-2 py-2 text-sm">
            {PAYMENT_METHODS.map((m) => (
              <option key={m}>{m}</option>
            ))}
          </select>
        </label>
        <div className="space-y-1 text-sm text-stone-800">
          <Row label="Subtotal" value={`₹${subtotal}`} />
          {pricing && (
            <>
              <Row label="Delivery" value={pricing.delivery_fee === 0 ? "Free" : `₹${pricing.delivery_fee}`} />
              {pricing.cod_fee > 0 && <Row label="Cash on delivery fee" value={`₹${pricing.cod_fee}`} />}
              <div className="my-2 border-t border-stone-200" />
              <Row label="Total" value={`₹${pricing.total}`} bold />
            </>
          )}
        </div>
        <p className="mt-2 text-xs text-stone-700">Free delivery above ₹499, otherwise ₹49. Cash on delivery up to ₹3,000 (₹30 fee).</p>
        {problem && <p className="mt-3 rounded bg-red-50 p-2 text-sm text-red-800">{problem}</p>}

        {ready && !token ? (
          <div className="mt-4 rounded bg-amber-50 p-3 text-sm text-amber-900">
            Please{" "}
            <Link href="/login" className="font-medium underline">
              sign in
            </Link>{" "}
            to place your order. Your cart will be kept.
          </div>
        ) : (
          <button
            onClick={checkout}
            disabled={busy || !pricing || !token}
            className="mt-4 w-full rounded bg-emerald-700 py-2.5 font-medium text-white hover:bg-emerald-800 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {busy ? "Placing order…" : "Place order (demo)"}
          </button>
        )}
      </aside>
    </div>
  );
}

function Row({ label, value, bold = false }: { label: string; value: string; bold?: boolean }) {
  return (
    <div className={`flex justify-between ${bold ? "text-base font-semibold text-stone-900" : ""}`}>
      <span>{label}</span>
      <span>{value}</span>
    </div>
  );
}
