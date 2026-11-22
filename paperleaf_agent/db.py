"""SQLite database for PaperLeaf Books (all data is made up for practice).

Tables: books, customers, orders, order_items, tickets.
The database file is created and seeded automatically on first use.
"""
import sqlite3
import threading
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "paperleaf.db"
_init_lock = threading.Lock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    genre TEXT NOT NULL,
    price INTEGER NOT NULL,            -- rupees
    condition TEXT NOT NULL CHECK (condition IN ('New','Like New','Good')),
    stock INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    city TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS orders (
    id TEXT PRIMARY KEY,               -- like PL-1001
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    status TEXT NOT NULL CHECK (status IN ('Placed','Shipped','Delivered','Cancelled','Returned')),
    total INTEGER NOT NULL,
    payment_method TEXT NOT NULL,
    placed_at TEXT NOT NULL,
    delivered_at TEXT
);
CREATE TABLE IF NOT EXISTS order_items (
    order_id TEXT NOT NULL REFERENCES orders(id),
    book_id INTEGER NOT NULL REFERENCES books(id),
    qty INTEGER NOT NULL,
    price INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,   -- never reused; ticket ID = TKT-<id>
    time TEXT NOT NULL,
    customer_message TEXT NOT NULL,
    reason TEXT NOT NULL,
    priority TEXT NOT NULL CHECK (priority IN ('normal','high')),
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','in_progress','closed')),
    customer_id INTEGER REFERENCES customers(id)
);
"""

BOOKS = [
    ("The Midnight Library", "Matt Haig", "Fiction", 399, "New", 12),
    ("Atomic Habits", "James Clear", "Self-help", 449, "New", 20),
    ("The Alchemist", "Paulo Coelho", "Fiction", 299, "New", 25),
    ("Sapiens", "Yuval Noah Harari", "Non-fiction", 599, "New", 8),
    ("The God of Small Things", "Arundhati Roy", "Fiction", 349, "New", 10),
    ("Wings of Fire", "A. P. J. Abdul Kalam", "Biography", 250, "New", 15),
    ("Malgudi Days", "R. K. Narayan", "Fiction", 220, "New", 18),
    ("The White Tiger", "Aravind Adiga", "Fiction", 320, "New", 9),
    ("Train to Pakistan", "Khushwant Singh", "Fiction", 275, "New", 7),
    ("Rich Dad Poor Dad", "Robert Kiyosaki", "Finance", 350, "New", 14),
    ("Ikigai", "Hector Garcia", "Self-help", 299, "New", 16),
    ("Harry Potter and the Philosopher's Stone", "J. K. Rowling", "Children", 499, "New", 11),
    ("The Hobbit", "J. R. R. Tolkien", "Fantasy", 450, "New", 9),
    ("A Brief History of Time", "Stephen Hawking", "Science", 399, "New", 6),
    ("NCERT Mathematics Class 10", "NCERT", "Textbook", 150, "New", 40),
    ("Concepts of Physics Vol 1", "H. C. Verma", "Textbook", 520, "New", 13),
    ("Python Crash Course", "Eric Matthes", "Technology", 1999, "New", 5),
    ("The Pragmatic Programmer", "Hunt & Thomas", "Technology", 2499, "New", 4),
    ("Gitanjali", "Rabindranath Tagore", "Poetry", 199, "New", 12),
    ("Chanakya's Chant", "Ashwin Sanghi", "Fiction", 299, "Like New", 3),
    ("The Palace of Illusions", "Chitra Banerjee Divakaruni", "Fiction", 260, "Like New", 2),
    ("Godan", "Munshi Premchand", "Fiction", 150, "Good", 4),
    ("Discovery of India", "Jawaharlal Nehru", "History", 280, "Good", 2),
    ("The Immortals of Meluha", "Amish Tripathi", "Fantasy", 230, "Like New", 5),
    ("India After Gandhi", "Ramachandra Guha", "History", 650, "New", 6),
    ("Panchatantra Stories", "Vishnu Sharma", "Children", 180, "New", 20),
    ("The Monk Who Sold His Ferrari", "Robin Sharma", "Self-help", 240, "Good", 3),
    ("Thinking, Fast and Slow", "Daniel Kahneman", "Non-fiction", 420, "Like New", 4),
    ("Cosmos", "Carl Sagan", "Science", 480, "New", 5),
    ("Sherlock Holmes: Complete Stories", "Arthur Conan Doyle", "Mystery", 550, "New", 7),
]

CUSTOMERS = [
    ("Aarav Mehta", "aarav.mehta@example.com", "Mumbai"),
    ("Diya Nair", "diya.nair@example.com", "Kochi"),
    ("Rohan Iyer", "rohan.iyer@example.com", "Bengaluru"),
    ("Sneha Kulkarni", "sneha.kulkarni@example.com", "Pune"),
    ("Kabir Singh", "kabir.singh@example.com", "Delhi"),
    ("Ananya Das", "ananya.das@example.com", "Kolkata"),
]

# (order_id, customer_id, status, payment, placed_at, delivered_at, [(book_id, qty)])
ORDERS = [
    ("PL-1001", 1, "Delivered", "UPI", "2026-11-02 10:15", "2026-11-05 16:40", [(1, 1), (2, 1)]),
    ("PL-1002", 1, "Shipped", "Credit card", "2026-11-18 09:05", None, [(4, 1)]),
    ("PL-1003", 2, "Delivered", "Cash on delivery", "2026-11-04 18:30", "2026-11-09 12:10", [(3, 2)]),
    ("PL-1004", 2, "Placed", "UPI", "2026-11-21 20:45", None, [(12, 1), (26, 1)]),
    ("PL-1005", 3, "Delivered", "Net banking", "2026-10-28 11:00", "2026-11-01 15:20", [(17, 1), (18, 1)]),
    ("PL-1006", 3, "Returned", "UPI", "2026-10-20 13:25", "2026-10-24 10:00", [(16, 1)]),
    ("PL-1007", 4, "Shipped", "Debit card", "2026-11-19 08:50", None, [(8, 1), (9, 1), (10, 1)]),
    ("PL-1008", 4, "Cancelled", "UPI", "2026-11-12 17:10", None, [(13, 1)]),
    ("PL-1009", 5, "Delivered", "Cash on delivery", "2026-11-08 12:00", "2026-11-12 14:30", [(15, 3)]),
    ("PL-1010", 5, "Placed", "UPI", "2026-11-22 09:30", None, [(21, 1), (22, 1)]),
    ("PL-1011", 6, "Delivered", "Credit card", "2026-11-06 19:20", "2026-11-10 11:45", [(25, 1), (29, 1)]),
    ("PL-1012", 6, "Shipped", "UPI", "2026-11-20 14:15", None, [(5, 1)]),
]


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_conn() -> sqlite3.Connection:
    ensure_db()
    return _connect()


def ensure_db() -> None:
    """Create and seed the database on first use."""
    if DB_PATH.exists():
        return
    with _init_lock:
        if DB_PATH.exists():
            return
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = DB_PATH.with_suffix(".tmp")
        tmp.unlink(missing_ok=True)
        conn = sqlite3.connect(tmp)
        conn.executescript(SCHEMA)
        conn.executemany(
            "INSERT INTO books (title, author, genre, price, condition, stock) VALUES (?,?,?,?,?,?)", BOOKS
        )
        conn.executemany("INSERT INTO customers (name, email, city) VALUES (?,?,?)", CUSTOMERS)
        prices = {i + 1: b[3] for i, b in enumerate(BOOKS)}
        for oid, cid, status, pay, placed, delivered, items in ORDERS:
            total = sum(prices[b] * q for b, q in items)
            total += 0 if total > 499 else 49  # delivery fee rule from the FAQ
            conn.execute("INSERT INTO orders VALUES (?,?,?,?,?,?,?)", (oid, cid, status, total, pay, placed, delivered))
            conn.executemany(
                "INSERT INTO order_items VALUES (?,?,?,?)", [(oid, b, q, prices[b]) for b, q in items]
            )
        # First ticket will be TKT-1001
        conn.execute("INSERT INTO sqlite_sequence (name, seq) VALUES ('tickets', 1000)")
        conn.commit()
        conn.close()
        tmp.replace(DB_PATH)


# ---------- tickets ----------
def insert_ticket(message: str, reason: str, priority: str, customer_id: int | None = None) -> str:
    conn = get_conn()
    try:
        with conn:
            cur = conn.execute(
                "INSERT INTO tickets (time, customer_message, reason, priority, status, customer_id) "
                "VALUES (?,?,?,?, 'open', ?)",
                (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message, reason, priority, customer_id),
            )
            return f"TKT-{cur.lastrowid}"
    finally:
        conn.close()


def list_tickets(status: str | None = None) -> list[dict]:
    q = "SELECT id, time, customer_message, reason, priority, status, customer_id FROM tickets"
    args: tuple = ()
    if status:
        q += " WHERE status = ?"
        args = (status,)
    q += " ORDER BY id DESC"
    conn = get_conn()
    try:
        rows = conn.execute(q, args).fetchall()
    finally:
        conn.close()
    return [
        {"ticket_id": f"TKT-{r['id']}", **{k: r[k] for k in r.keys() if k != "id"}} for r in rows
    ]


# ---------- customers, orders, books ----------
def get_customer_by_email(email: str) -> dict | None:
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT id, name, email, city FROM customers WHERE lower(email) = lower(?)", (email.strip(),)
        ).fetchone()
    finally:
        conn.close()
    return dict(row) if row else None


def get_order_for_customer(order_id: str, customer_id: int) -> dict | None:
    """Return the order ONLY if it belongs to this customer (otherwise None, same as 'not found')."""
    conn = get_conn()
    try:
        o = conn.execute(
            "SELECT id, status, total, payment_method, placed_at, delivered_at FROM orders "
            "WHERE upper(id) = upper(?) AND customer_id = ?",
            (order_id.strip(), customer_id),
        ).fetchone()
        if not o:
            return None
        items = conn.execute(
            "SELECT b.title, i.qty, i.price FROM order_items i JOIN books b ON b.id = i.book_id "
            "WHERE i.order_id = ?",
            (o["id"],),
        ).fetchall()
    finally:
        conn.close()
    return {**dict(o), "items": [dict(i) for i in items]}


def list_orders_for_customer(customer_id: int) -> list[dict]:
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT id, status, total, placed_at FROM orders WHERE customer_id = ? ORDER BY placed_at DESC",
            (customer_id,),
        ).fetchall()
    finally:
        conn.close()
    return [dict(r) for r in rows]


def search_books(query: str = "", genre: str = "", max_price: int = 0, limit: int = 5) -> list[dict]:
    sql, args = "SELECT title, author, genre, price, condition, stock FROM books WHERE stock > 0", []
    if query:
        sql += " AND (title LIKE ? OR author LIKE ? OR genre LIKE ?)"
        args += [f"%{query}%"] * 3
    if genre:
        sql += " AND genre LIKE ?"
        args.append(f"%{genre}%")
    if max_price and max_price > 0:
        sql += " AND price <= ?"
        args.append(max_price)
    sql += " ORDER BY title LIMIT ?"
    args.append(limit)
    conn = get_conn()
    try:
        return [dict(r) for r in conn.execute(sql, args).fetchall()]
    finally:
        conn.close()
