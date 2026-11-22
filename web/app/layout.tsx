import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth";
import { CartProvider } from "@/lib/cart";
import Header from "@/components/Header";
import ChatWidget from "@/components/ChatWidget";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "PaperLeaf Books",
  description: "New and pre-loved printed books across India, with Paige, your bookish support assistant.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${geistSans.variable} h-full antialiased`}>
      <body className="flex min-h-full flex-col bg-stone-50 text-stone-900">
        <AuthProvider>
          <CartProvider>
          <Header />
          <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-8">{children}</main>
          <footer className="border-t border-stone-200 py-4 text-center text-xs text-stone-600">
            PaperLeaf Books is a made-up store. All data is for practice.
          </footer>
          <ChatWidget />
          </CartProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
