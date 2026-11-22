"""Agent tools that read the database.

PRIVACY: the customer's identity comes from the session state set by the API after login
(tool_context.state["customer_id"]). It is never taken from anything the model or the customer types.
"""
from google.adk.tools import ToolContext

from . import db


def get_order_status(order_id: str, tool_context: ToolContext) -> dict:
    """Look up the signed-in customer's own order by its order ID (like PL-1001).

    Args:
        order_id: The order ID the customer gave, e.g. "PL-1001".

    Returns:
        The order's status, items, total, payment method and dates, or an error message.
        Only orders belonging to the signed-in customer can be found.
    """
    customer_id = tool_context.state.get("customer_id")
    if not customer_id:
        return {"error": "not_signed_in",
                "message": "The customer is not signed in, so orders cannot be looked up. Ask them to sign in."}
    order = db.get_order_for_customer(order_id, customer_id)
    if not order:
        # Same answer whether the order does not exist or belongs to someone else: no information leaks.
        return {"error": "not_found",
                "message": "No order with that ID was found on this customer's account."}
    return order


def list_my_orders(tool_context: ToolContext) -> dict:
    """List the signed-in customer's own orders (ID, status, total, date), newest first."""
    customer_id = tool_context.state.get("customer_id")
    if not customer_id:
        return {"error": "not_signed_in",
                "message": "The customer is not signed in. Ask them to sign in."}
    return {"orders": db.list_orders_for_customer(customer_id)}


def search_books(query: str = "", genre: str = "", max_price: int = 0) -> dict:
    """Search PaperLeaf's in-stock books, e.g. to suggest a gift.

    Args:
        query: Words to match in the title, author or genre (optional).
        genre: A genre such as Fiction, Fantasy, Children, Science, History, Self-help (optional).
        max_price: Maximum price in rupees; 0 means no limit (optional).

    Returns:
        Up to 5 matching books with title, author, genre, price in rupees, condition and stock.
    """
    return {"books": db.search_books(query, genre, max_price)}
