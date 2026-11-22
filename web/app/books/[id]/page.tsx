import { Suspense } from "react";
import BookDetail from "@/components/BookDetail";

export default function BookPage() {
  return (
    <Suspense fallback={<p className="text-stone-500">Loading…</p>}>
      <BookDetail />
    </Suspense>
  );
}
