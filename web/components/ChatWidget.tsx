"use client";

import { useEffect, useRef, useState } from "react";
import { getGreeting, sendChat } from "@/lib/api";
import { useAuth } from "@/lib/auth";

type Msg = { role: "user" | "paige"; text: string; ticket?: string | null };

const FALLBACK_GREETING = "Hello, I'm Paige from PaperLeaf Books. How can I help you today?";
const SUGGESTIONS = ["How much does delivery cost?", "What is your return policy?", "Suggest a gift book under ₹300"];

export default function ChatWidget() {
  const { token, name, ready } = useAuth();
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const bottom = useRef<HTMLDivElement>(null);

  // Greeting when the chat first opens
  useEffect(() => {
    if (open && messages.length === 0) {
      getGreeting()
        .then((g) => setMessages([{ role: "paige", text: g.greeting }]))
        .catch(() => setMessages([{ role: "paige", text: FALLBACK_GREETING }]));
    }
  }, [open, messages.length]);

  // A different sign-in means a different conversation
  useEffect(() => {
    if (!ready) return;
    setMessages([]);
    setSessionId(null);
  }, [token, ready]);

  useEffect(() => {
    bottom.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  async function send(text: string) {
    const msg = text.trim();
    if (!msg || busy) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", text: msg }]);
    setBusy(true);
    try {
      const res = await sendChat(msg, sessionId, token);
      setSessionId(res.session_id);
      setMessages((m) => [...m, { role: "paige", text: res.reply || "Sorry, could you rephrase that?", ticket: res.ticket_id }]);
    } catch (e) {
      setMessages((m) => [
        ...m,
        { role: "paige", text: e instanceof Error ? e.message : "Sorry, something went wrong. Please try again." },
      ]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      {!open && (
        <button
          onClick={() => setOpen(true)}
          className="fixed bottom-5 right-5 z-20 rounded-full bg-emerald-700 px-5 py-3 text-white shadow-lg hover:bg-emerald-800"
        >
          💬 Chat with Paige
        </button>
      )}
      {open && (
        <div className="fixed bottom-5 right-5 z-20 flex h-[32rem] w-[22rem] max-w-[calc(100vw-2rem)] flex-col overflow-hidden rounded-xl border border-stone-200 bg-white shadow-2xl">
          <div className="flex items-center justify-between bg-emerald-700 px-4 py-3 text-white">
            <div>
              <div className="font-semibold">Paige · PaperLeaf Books</div>
              <div className="text-xs text-emerald-100">{name ? `Signed in as ${name}` : "Guest (sign in to ask about orders)"}</div>
            </div>
            <button onClick={() => setOpen(false)} aria-label="Close chat" className="text-xl leading-none">
              ×
            </button>
          </div>

          <div className="flex-1 space-y-3 overflow-y-auto bg-stone-50 p-3">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                <div
                  className={`max-w-[85%] whitespace-pre-wrap rounded-2xl px-3 py-2 text-sm ${
                    m.role === "user" ? "bg-emerald-700 text-white" : "border border-stone-200 bg-white text-stone-800"
                  }`}
                >
                  {m.text}
                  {m.ticket && (
                    <div className="mt-2 rounded bg-amber-100 px-2 py-1 text-xs font-medium text-amber-900">
                      🎫 Ticket {m.ticket}
                    </div>
                  )}
                </div>
              </div>
            ))}
            {busy && <div className="text-sm text-stone-600">Paige is typing…</div>}
            {messages.length === 1 && !busy && (
              <div className="flex flex-wrap gap-2 pt-1">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => send(s)}
                    className="rounded-full border border-emerald-300 bg-white px-3 py-1 text-xs text-emerald-800 hover:bg-emerald-50"
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}
            <div ref={bottom} />
          </div>

          <form
            onSubmit={(e) => {
              e.preventDefault();
              send(input);
            }}
            className="flex gap-2 border-t border-stone-200 p-3"
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about orders, delivery, returns…"
              maxLength={1000}
              className="flex-1 rounded border border-stone-300 px-3 py-2 text-sm outline-none focus:border-emerald-600"
            />
            <button
              disabled={busy || !input.trim()}
              className="rounded bg-emerald-700 px-3 py-2 text-sm text-white hover:bg-emerald-800 disabled:opacity-50"
            >
              Send
            </button>
          </form>
        </div>
      )}
    </>
  );
}
