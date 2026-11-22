import jwt
import pytest

from api import guards
from tests.conftest import admin_token, customer_token


def test_health_and_books(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert len(client.get("/books").json()) == 30
    assert client.get("/books?genre=Fantasy").json()
    assert client.get("/books/1").status_code == 200
    assert client.get("/books/9999").status_code == 404


def test_customer_login_and_orders(client):
    assert client.post("/login", json={"email": "aarav.mehta@example.com", "password": "bad"}).status_code == 401
    assert client.post("/login", json={"email": "nobody@example.com", "password": "x"}).status_code == 401
    tok = customer_token(client)
    r = client.get("/me/orders", headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 200 and {o["id"] for o in r.json()} == {"PL-1001", "PL-1002"}
    assert client.get("/me/orders").status_code == 401


def test_tampered_or_wrong_role_tokens_rejected(client):
    tok = customer_token(client)
    assert client.get("/me/orders", headers={"Authorization": f"Bearer {tok}x"}).status_code == 401
    forged = jwt.encode({"role": "customer", "sub": "2", "exp": 9999999999}, "wrong-secret-wrong-secret-wrong", "HS256")
    assert client.get("/me/orders", headers={"Authorization": f"Bearer {forged}"}).status_code == 401
    # a customer token must not open the staff dashboard
    assert client.get("/admin/tickets", headers={"Authorization": f"Bearer {tok}"}).status_code == 401
    # a staff token must not act as a customer
    assert client.get("/me/orders", headers={"Authorization": f"Bearer {admin_token(client)}"}).status_code == 401


def test_expired_token_rejected(client):
    old = jwt.encode({"role": "admin", "sub": "staff", "exp": 1}, guards.JWT_SECRET, "HS256")
    assert client.get("/admin/stats", headers={"Authorization": f"Bearer {old}"}).status_code == 401


def test_admin_flow(client):
    assert client.post("/admin/login", json={"passcode": "nope"}).status_code == 401
    assert client.get("/admin/tickets").status_code == 401
    assert client.get("/tickets").status_code == 404  # the old public endpoint is gone
    h = {"Authorization": f"Bearer {admin_token(client)}"}
    from paperleaf_agent import db

    tid = db.insert_ticket("api test", "angry customer", "high")
    assert any(t["ticket_id"] == tid for t in client.get("/admin/tickets", headers=h).json())
    assert client.patch(f"/admin/tickets/{tid}", json={"status": "in_progress"}, headers=h).json()["status"] == "in_progress"
    assert client.patch(f"/admin/tickets/{tid}", json={"status": "bad"}, headers=h).status_code == 422
    assert client.patch("/admin/tickets/TKT-999999", json={"status": "open"}, headers=h).status_code == 404
    assert client.get("/admin/stats", headers=h).json()["total"] >= 1


def test_rate_limit_on_login(client):
    codes = [client.post("/login", json={"email": "a@b.c", "password": "x"}).status_code for _ in range(12)]
    assert codes[:10] == [401] * 10
    assert 429 in codes[10:]
    r = client.post("/login", json={"email": "a@b.c", "password": "x"})
    assert r.status_code == 429 and "Retry-After" in r.headers


def test_admin_login_rate_limited(client):
    codes = [client.post("/admin/login", json={"passcode": "guess"}).status_code for _ in range(7)]
    assert codes[:5] == [401] * 5 and 429 in codes[5:]


def test_chat_validation(client):
    assert client.post("/chat", json={"message": ""}).status_code == 422
    assert client.post("/chat", json={"message": "x" * 1001}).status_code == 422


def test_cors_only_allows_configured_origins(client):
    ok = client.options("/chat", headers={"Origin": "http://localhost:3001", "Access-Control-Request-Method": "POST"})
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:3001"
    bad = client.options("/chat", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"})
    assert "access-control-allow-origin" not in bad.headers


def test_production_refuses_weak_settings(monkeypatch):
    monkeypatch.setattr(guards, "IS_PROD", True)
    monkeypatch.setattr(guards, "ADMIN_PASSCODE", "admin-demo")
    monkeypatch.delenv("JWT_SECRET", raising=False)
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
    with pytest.raises(RuntimeError, match="JWT_SECRET"):
        guards.check_production_settings()


def test_invented_ticket_ids_are_detected():
    from api.main import invented_ticket

    assert invented_ticket("Your ticket ID is TKT-4521.", None)  # no ticket was created
    assert invented_ticket("Your ticket ID is TKT-4521.", "TKT-1001")  # wrong ID
    assert not invented_ticket("Your ticket ID is TKT-1001.", "TKT-1001")
    assert not invented_ticket("It is free above 499 (Source: Delivery).", None)
