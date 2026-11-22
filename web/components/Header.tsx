"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth";

export default function Header() {
  const { name, ready, signOut } = useAuth();
  return (
    <header className="border-b border-stone-200 bg-white/80 backdrop-blur sticky top-0 z-10">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <Link href="/" className="text-lg font-semibold text-emerald-800">
          📚 PaperLeaf Books
        </Link>
        <nav className="flex items-center gap-4 text-sm text-stone-700">
          <Link href="/books" className="hover:text-emerald-700">
            Books
          </Link>
          {ready && name ? (
            <>
              <Link href="/orders" className="hover:text-emerald-700">
                My orders
              </Link>
              <span className="hidden text-stone-500 sm:inline">Hi, {name.split(" ")[0]}</span>
              <button onClick={signOut} className="rounded border border-stone-300 px-2 py-1 hover:bg-stone-100">
                Sign out
              </button>
            </>
          ) : (
            ready && (
              <Link href="/login" className="rounded bg-emerald-700 px-3 py-1 text-white hover:bg-emerald-800">
                Sign in
              </Link>
            )
          )}
        </nav>
      </div>
    </header>
  );
}
