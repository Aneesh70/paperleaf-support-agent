"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getBooks, type Book } from "@/lib/api";
import BookCard from "@/components/BookCard";

export default function Home() {
  const [featured, setFeatured] = useState<Book[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getBooks()
      .then((b) => setFeatured(b.filter((x) => x.condition === "New").slice(0, 4)))
      .catch((e) => setError(e.message));
  }, []);

  return (
    <div className="space-y-10">
      <section className="rounded-2xl bg-gradient-to-br from-emerald-700 to-emerald-900 p-8 text-white sm:p-12">
        <h1 className="text-3xl font-bold sm:text-4xl">Books you&apos;ll love, new and pre-loved.</h1>
        <p className="mt-3 max-w-xl text-emerald-100">
          Free delivery above ₹499 across India. Every pre-loved book is checked and marked Good or Like New.
        </p>
        <Link href="/books" className="mt-6 inline-block rounded bg-white px-5 py-2 font-medium text-emerald-800 hover:bg-emerald-50">
          Browse the shelves
        </Link>
      </section>

      <section>
        <h2 className="mb-4 text-xl font-semibold">Featured books</h2>
        {error ? (
          <p className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">
            Couldn&apos;t reach the store backend ({error}). Is the API running on port 8100?
          </p>
        ) : (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            {featured.map((b) => (
              <BookCard key={b.id} book={b} />
            ))}
          </div>
        )}
      </section>

      <section className="rounded-lg border border-emerald-200 bg-emerald-50 p-5 text-sm text-emerald-900">
        💬 Questions about delivery, returns or your order? Tap <strong>Chat with Paige</strong> in the corner.
      </section>
    </div>
  );
}
