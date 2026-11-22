"use client";

import { useEffect, useMemo, useState } from "react";
import { getBooks, type Book } from "@/lib/api";
import BookCard from "@/components/BookCard";

export default function BooksPage() {
  const [all, setAll] = useState<Book[]>([]);
  const [q, setQ] = useState("");
  const [genre, setGenre] = useState("");
  const [condition, setCondition] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getBooks()
      .then(setAll)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const genres = useMemo(() => [...new Set(all.map((b) => b.genre))].sort(), [all]);
  const shown = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return all.filter(
      (b) =>
        (!needle || b.title.toLowerCase().includes(needle) || b.author.toLowerCase().includes(needle)) &&
        (!genre || b.genre === genre) &&
        (!condition || b.condition === condition),
    );
  }, [all, q, genre, condition]);

  return (
    <div>
      <h1 className="mb-4 text-2xl font-bold">All books</h1>
      <div className="mb-6 flex flex-wrap gap-3">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search title or author"
          className="min-w-[14rem] flex-1 rounded border border-stone-300 bg-white px-3 py-2 text-sm outline-none focus:border-emerald-600"
        />
        <select value={genre} onChange={(e) => setGenre(e.target.value)} className="rounded border border-stone-300 bg-white px-3 py-2 text-sm">
          <option value="">All genres</option>
          {genres.map((g) => (
            <option key={g}>{g}</option>
          ))}
        </select>
        <select value={condition} onChange={(e) => setCondition(e.target.value)} className="rounded border border-stone-300 bg-white px-3 py-2 text-sm">
          <option value="">New &amp; pre-loved</option>
          <option>New</option>
          <option>Like New</option>
          <option>Good</option>
        </select>
      </div>

      {error && <p className="rounded border border-red-200 bg-red-50 p-3 text-sm text-red-700">Couldn&apos;t load books: {error}</p>}
      {loading && !error && <p className="text-stone-600">Loading…</p>}
      {!loading && !error && shown.length === 0 && <p className="text-stone-600">No books match your search.</p>}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4">
        {shown.map((b) => (
          <BookCard key={b.id} book={b} />
        ))}
      </div>
    </div>
  );
}
