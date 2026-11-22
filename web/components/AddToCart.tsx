"use client";

import Link from "next/link";
import { useState } from "react";
import type { Book } from "@/lib/api";
import { useCart } from "@/lib/cart";

export default function AddToCart({ book, large = false }: { book: Book; large?: boolean }) {
  const { add, lines } = useCart();
  const [justAdded, setJustAdded] = useState(false);
  const inCart = lines.find((l) => l.bookId === book.id)?.qty ?? 0;
  const size = large ? "px-5 py-3 text-base" : "px-3 py-1.5 text-sm";

  if (book.stock <= 0) {
    return <span className={`rounded bg-stone-200 font-medium text-stone-700 ${size}`}>Out of stock</span>;
  }

  return (
    <div className="flex items-center gap-3">
      <button
        onClick={() => {
          add(book);
          setJustAdded(true);
          setTimeout(() => setJustAdded(false), 1500);
        }}
        disabled={inCart >= Math.min(10, book.stock)}
        className={`rounded bg-emerald-700 font-medium text-white hover:bg-emerald-800 disabled:cursor-not-allowed disabled:opacity-60 ${size}`}
      >
        {justAdded ? "Added ✓" : "Add to cart"}
      </button>
      {inCart > 0 && (
        <Link href="/cart" className="text-sm text-emerald-800 underline">
          {inCart} in cart · View cart
        </Link>
      )}
    </div>
  );
}
