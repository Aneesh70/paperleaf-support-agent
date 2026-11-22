"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { getBook, type Book } from "@/lib/api";
import AddToCart from "@/components/AddToCart";

export default function BookDetail() {
  const { id } = useParams<{ id: string }>();
  const [book, setBook] = useState<Book | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getBook(id)
      .then(setBook)
      .catch((e) => setError(e.message));
  }, [id]);

  if (error) {
    return (
      <div>
        <p className="mb-3 text-stone-600">Sorry, we couldn&apos;t find that book ({error}).</p>
        <Link href="/books" className="text-emerald-700 underline">
          Back to all books
        </Link>
      </div>
    );
  }
  if (!book) return <p className="text-stone-600">Loading…</p>;

  return (
    <div>
      <Link href="/books" className="text-sm text-emerald-700 hover:underline">
        ← All books
      </Link>
      <div className="mt-4 grid gap-8 rounded-xl border border-stone-200 bg-white p-6 shadow-sm sm:grid-cols-[14rem_1fr]">
        <div className="flex h-56 items-center justify-center rounded bg-gradient-to-br from-emerald-50 to-amber-50 text-7xl">📖</div>
        <div>
          <h1 className="text-2xl font-bold">{book.title}</h1>
          <p className="text-stone-600">by {book.author}</p>
          <div className="mt-3 flex flex-wrap gap-2 text-xs">
            <span className="rounded-full bg-stone-100 px-2 py-1">{book.genre}</span>
            <span className="rounded-full bg-emerald-100 px-2 py-1 text-emerald-800">{book.condition}</span>
          </div>
          <p className="mt-5 text-3xl font-semibold text-emerald-800">₹{book.price}</p>
          <p className="mt-1 text-sm text-stone-600">
            {book.stock > 0 ? `${book.stock} in stock` : "Out of stock"} · Free delivery above ₹499, else ₹49 · Gift wrap ₹49
          </p>
          <div className="mt-6">
            <AddToCart book={book} large />
          </div>
          <p className="mt-4 text-sm text-stone-700">
            Questions about delivery, returns or gift wrapping? Ask Paige in the chat corner.
          </p>
        </div>
      </div>
    </div>
  );
}
