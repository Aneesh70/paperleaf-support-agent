import csv
import threading
from datetime import datetime
from pathlib import Path

# tickets.csv lives in the project folder (next to the paperleaf_agent folder)
TICKETS_FILE = Path(__file__).resolve().parent.parent / "tickets.csv"
FIELDS = ["ticket_id", "time", "customer_message", "reason", "priority", "status"]
_lock = threading.Lock()


def _next_number() -> int:
    """Next ticket number: one more than the highest already in the file (starts at 1001)."""
    highest = 1000
    if TICKETS_FILE.exists():
        with open(TICKETS_FILE, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                try:
                    highest = max(highest, int(row["ticket_id"].split("-")[1]))
                except (KeyError, ValueError, IndexError):
                    pass
    return highest + 1


def create_ticket(message: str, reason: str, priority: str) -> str:
    """Raise a support ticket so a person from PaperLeaf Books can follow up.

    Args:
        message: The customer's message that needs a person's help (short, no card numbers, OTPs or passwords).
        reason: Why a person is needed, e.g. "damaged item", "refund above Rs 2000",
            "answer not in FAQ", "angry customer", "customer asked for a person".
        priority: "high" for angry customers, damaged/wrong items and refunds above Rs 2000; otherwise "normal".

    Returns:
        The ticket ID, like TKT-1001. Share this ID with the customer.
    """
    priority = "high" if str(priority).strip().lower() == "high" else "normal"
    with _lock:
        ticket_id = f"TKT-{_next_number()}"
        is_new = not TICKETS_FILE.exists() or TICKETS_FILE.stat().st_size == 0
        with open(TICKETS_FILE, "a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if is_new:
                w.writerow(FIELDS)
            w.writerow([ticket_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        message, reason, priority, "open"])
    return ticket_id
