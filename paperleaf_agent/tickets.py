from . import db


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
    # Safety net in code: these reasons are always high priority, whatever the model chose.
    if any(k in str(reason).lower() for k in ("refund above", "damaged", "wrong item", "angry", "upset")):
        priority = "high"
    # The ID is made by the database (auto-increment, never reused), not by the model.
    return db.insert_ticket(message, reason, priority)
