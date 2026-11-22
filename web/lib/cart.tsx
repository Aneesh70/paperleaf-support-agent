"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { Book } from "./api";

export type CartLine = { bookId: number; title: string; author: string; price: number; stock: number; qty: number; coverUrl?: string | null };

type Cart = {
  lines: CartLine[];
  count: number;
  subtotal: number;
  add: (book: Book, qty?: number) => void;
  setQty: (bookId: number, qty: number) => void;
  remove: (bookId: number) => void;
  clear: () => void;
};

const CartContext = createContext<Cart | null>(null);
const KEY = "paperleaf_cart";
const MAX_PER_BOOK = 10;

export function CartProvider({ children }: { children: React.ReactNode }) {
  const [lines, setLines] = useState<CartLine[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    // Read the saved cart once after the first render (localStorage is not available on the server).
    try {
      const saved = JSON.parse(localStorage.getItem(KEY) ?? "[]");
      if (Array.isArray(saved)) {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setLines(saved);
      }
    } catch {}
    setLoaded(true);
  }, []);

  useEffect(() => {
    if (loaded) localStorage.setItem(KEY, JSON.stringify(lines));
  }, [lines, loaded]);

  const add = useCallback((book: Book, qty = 1) => {
    setLines((cur) => {
      const limit = Math.min(MAX_PER_BOOK, book.stock);
      const existing = cur.find((l) => l.bookId === book.id);
      if (existing) {
        return cur.map((l) => (l.bookId === book.id ? { ...l, stock: book.stock, coverUrl: book.cover_url, qty: Math.min(limit, l.qty + qty) } : l));
      }
      return [...cur, { bookId: book.id, title: book.title, author: book.author, price: book.price, stock: book.stock, coverUrl: book.cover_url, qty: Math.min(limit, qty) }];
    });
  }, []);

  const setQty = useCallback((bookId: number, qty: number) => {
    setLines((cur) =>
      cur.map((l) => (l.bookId === bookId ? { ...l, qty: Math.max(1, Math.min(MAX_PER_BOOK, l.stock, qty)) } : l)),
    );
  }, []);

  const remove = useCallback((bookId: number) => setLines((cur) => cur.filter((l) => l.bookId !== bookId)), []);
  const clear = useCallback(() => setLines([]), []);

  const value = useMemo<Cart>(
    () => ({
      lines,
      count: lines.reduce((n, l) => n + l.qty, 0),
      subtotal: lines.reduce((n, l) => n + l.qty * l.price, 0),
      add,
      setQty,
      remove,
      clear,
    }),
    [lines, add, setQty, remove, clear],
  );
  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}

export function useCart() {
  const ctx = useContext(CartContext);
  if (!ctx) throw new Error("useCart must be used inside CartProvider");
  return ctx;
}
