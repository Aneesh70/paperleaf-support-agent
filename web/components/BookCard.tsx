import Link from "next/link";
import type { Book } from "@/lib/api";
import AddToCart from "./AddToCart";

const conditionStyle: Record<Book["condition"], string> = {
  New: "bg-emerald-100 text-emerald-900",
  "Like New": "bg-sky-100 text-sky-900",
  Good: "bg-amber-100 text-amber-900",
};

export default function BookCard({ book }: { book: Book }) {
  return (
    <div className="flex flex-col justify-between rounded-lg border border-stone-200 bg-white p-4 shadow-sm transition hover:shadow-md">
      <Link href={`/books/${book.id}`} className="block">
        <div className="mb-3 flex h-28 items-center justify-center rounded bg-gradient-to-br from-emerald-50 to-amber-50 text-4xl">
          📖
        </div>
        <h3 className="font-semibold leading-snug text-stone-900">{book.title}</h3>
        <p className="text-sm text-stone-700">{book.author}</p>
      </Link>
      <div className="mt-3 space-y-3">
        <div className="flex items-center justify-between">
          <span className="font-semibold text-emerald-900">₹{book.price}</span>
          <span className={`rounded-full px-2 py-0.5 text-xs ${conditionStyle[book.condition]}`}>{book.condition}</span>
        </div>
        <AddToCart book={book} />
      </div>
    </div>
  );
}
