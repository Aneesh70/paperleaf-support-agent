export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8100";

export type Book = {
  id: number;
  title: string;
  author: string;
  genre: string;
  price: number;
  condition: "New" | "Like New" | "Good";
  stock: number;
};

export type OrderSummary = {
  id: string;
  status: "Placed" | "Shipped" | "Delivered" | "Cancelled" | "Returned";
  total: number;
  placed_at: string;
};

export type ChatReply = {
  session_id: string;
  reply: string;
  ticket_id: string | null;
};

async function request<T>(path: string, init?: RequestInit, token?: string | null): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await fetch(`${API_URL}${path}`, { ...init, headers: { ...headers, ...init?.headers } });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      detail = (await res.json()).detail ?? detail;
    } catch {}
    throw new Error(detail);
  }
  return res.json();
}

export const getBooks = (params: { q?: string; genre?: string; condition?: string } = {}) => {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => v && qs.set(k, v));
  return request<Book[]>(`/books${qs.size ? `?${qs}` : ""}`);
};

export const getBook = (id: string | number) => request<Book>(`/books/${id}`);

export const login = (email: string, password: string) =>
  request<{ token: string; name: string }>("/login", { method: "POST", body: JSON.stringify({ email, password }) });

export const getMyOrders = (token: string) => request<OrderSummary[]>("/me/orders", undefined, token);

export const sendChat = (message: string, sessionId: string | null, token: string | null) =>
  request<ChatReply>(
    "/chat",
    { method: "POST", body: JSON.stringify({ message, session_id: sessionId }) },
    token,
  );

export const getGreeting = () => request<{ greeting: string }>("/greeting");

// ---------- staff dashboard ----------
export type TicketStatus = "open" | "in_progress" | "closed";

export type Ticket = {
  ticket_id: string;
  time: string;
  customer_message: string;
  reason: string;
  priority: "normal" | "high";
  status: TicketStatus;
  customer_id: number | null;
};

export type Stats = {
  total: number;
  by_status: Record<TicketStatus, number>;
  open_by_priority: { high: number; normal: number };
  by_reason: { reason: string; count: number }[];
  per_day: { date: string; count: number }[];
};

export const adminLogin = (passcode: string) =>
  request<{ token: string }>("/admin/login", { method: "POST", body: JSON.stringify({ passcode }) });

export const adminTickets = (token: string) => request<Ticket[]>("/admin/tickets", undefined, token);

export const adminStats = (token: string) => request<Stats>("/admin/stats", undefined, token);

export const adminSetStatus = (token: string, ticketId: string, status: TicketStatus) =>
  request<Ticket>(`/admin/tickets/${ticketId}`, { method: "PATCH", body: JSON.stringify({ status }) }, token);
