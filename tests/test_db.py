from paperleaf_agent import db
from paperleaf_agent.security import hash_password, verify_password


def test_seed_counts():
    assert len(db.list_books()) == 30
    assert db.get_book(1)["title"] == "The Midnight Library"
    assert db.get_book(9999) is None


def test_ticket_ids_start_at_1001_and_never_repeat():
    a = db.insert_ticket("one", "answer not in FAQ", "normal")
    b = db.insert_ticket("two", "angry customer", "high")
    assert int(a[4:]) >= 1001
    assert int(b[4:]) == int(a[4:]) + 1
    assert a != b


def test_ticket_status_update_and_validation():
    t = db.insert_ticket("x", "damaged item", "high")
    assert db.update_ticket_status(t, "closed")["status"] == "closed"
    assert db.update_ticket_status("TKT-999999", "open") is None
    assert db.update_ticket_status("not-a-ticket", "open") is None
    try:
        db.update_ticket_status(t, "bogus")
        raise AssertionError("bad status accepted")
    except ValueError:
        pass


def test_passwords_hashed_and_verified():
    h = hash_password("secret")
    assert h != "secret" and verify_password("secret", h) and not verify_password("nope", h)
    assert not verify_password("secret", "garbage")


def test_authenticate():
    assert db.authenticate("AARAV.MEHTA@example.com", db.DEMO_PASSWORD)["name"] == "Aarav Mehta"
    assert db.authenticate("aarav.mehta@example.com", "wrong") is None
    assert db.authenticate("nobody@example.com", "x") is None


def test_order_privacy():
    # PL-1001 belongs to customer 1, PL-1003 to customer 2
    assert db.get_order_for_customer("PL-1001", 1)["status"] == "Delivered"
    assert db.get_order_for_customer("pl-1001", 1) is not None  # case-insensitive
    assert db.get_order_for_customer("PL-1003", 1) is None  # someone else's order looks like "not found"
    assert db.get_order_for_customer("PL-9999", 1) is None
    assert {o["id"] for o in db.list_orders_for_customer(1)} == {"PL-1001", "PL-1002"}


def test_book_search():
    assert all(b["price"] <= 300 for b in db.search_books(genre="Fantasy", max_price=300))
    assert db.search_books("zzzz-no-such-book") == []


def test_stats_shape():
    s = db.ticket_stats()
    assert set(s) == {"total", "by_status", "open_by_priority", "by_reason", "per_day"}
    assert len(s["per_day"]) == 7
    assert db.reason_group("refund above Rs 2000").startswith("Refund")
    assert db.reason_group("something else") == "Other"


def test_order_pricing_rules_from_the_faq():
    assert db.price_order(300, "UPI") == {"subtotal": 300, "delivery_fee": 49, "cod_fee": 0, "total": 349}
    assert db.price_order(499, "UPI")["delivery_fee"] == 49  # free only ABOVE 499
    assert db.price_order(500, "UPI")["delivery_fee"] == 0
    assert db.price_order(1000, "Cash on delivery")["total"] == 1030  # free delivery + 30 COD fee
    assert db.price_order(3000, "Cash on delivery")["total"] == 3030
    for bad in (lambda: db.price_order(3001, "Cash on delivery"), lambda: db.price_order(100, "Bitcoin")):
        try:
            bad()
            raise AssertionError("rule not enforced")
        except db.OrderError:
            pass


def test_create_order_reduces_stock_and_links_customer():
    before = db.get_book(3)["stock"]
    order = db.create_order(1, [(3, 2)], "UPI")  # The Alchemist, Rs 299 each
    assert order["order_id"].startswith("PL-") and order["total"] == 598 + 0
    assert db.get_book(3)["stock"] == before - 2
    mine = db.get_order_for_customer(order["order_id"], 1)
    assert mine["status"] == "Placed" and mine["items"][0]["qty"] == 2
    assert db.get_order_for_customer(order["order_id"], 2) is None  # not visible to others


def test_create_order_rejects_bad_requests_and_keeps_stock():
    stock = db.get_book(4)["stock"]
    for items, pay in (([], "UPI"), ([(4, 0)], "UPI"), ([(4, stock + 1)], "UPI"), ([(9999, 1)], "UPI"), ([(4, 1)], "Bitcoin")):
        try:
            db.create_order(1, items, pay)
            raise AssertionError(f"accepted {items} {pay}")
        except db.OrderError:
            pass
    assert db.get_book(4)["stock"] == stock  # nothing was taken from stock
