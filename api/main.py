"""FastAPI backend that wraps the same ADK agent (Paige) for the Next.js frontend.

Run from the project root:  uvicorn api.main:app --reload --port 8100
"""
import os
import re
import secrets
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

BASE = Path(__file__).resolve().parent.parent
load_dotenv(BASE / "paperleaf_agent" / ".env")

from google.adk.runners import Runner  # noqa: E402
from google.adk.sessions import InMemorySessionService  # noqa: E402
from google.genai import types  # noqa: E402

from api import guards  # noqa: E402
from paperleaf_agent import db  # noqa: E402
from paperleaf_agent.agent import root_agent  # noqa: E402

APP_NAME = "paperleaf_api"
GREETING = "Hello, I'm Paige from PaperLeaf Books. How can I help you today?"
FALLBACK_MODEL = os.environ.get("FALLBACK_MODEL", "gemini-3.5-flash")
ALLOWED_ORIGINS = [
    o.strip() for o in os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",") if o.strip()
]
BUSY_MARKERS = ("429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE")


@asynccontextmanager
async def lifespan(app: FastAPI):
    guards.check_production_settings()
    db.get_engine()  # create tables and seed on first start, and fail early if the database is unreachable
    sessions = InMemorySessionService()
    app.state.sessions = sessions
    app.state.runner = Runner(app_name=APP_NAME, agent=root_agent, session_service=sessions)
    # Same agent on a backup model, used once if the main model is overloaded.
    app.state.fallback_runner = Runner(
        app_name=APP_NAME, agent=root_agent.model_copy(update={"model": FALLBACK_MODEL}), session_service=sessions
    )
    yield


app = FastAPI(title="PaperLeaf Books API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- basics ----------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/greeting")
def greeting():
    return {"greeting": GREETING}


# ---------- customer sign-in ----------
class LoginRequest(BaseModel):
    email: str = Field(max_length=200)
    password: str = Field(max_length=200)


def customer_id_from(authorization: str | None) -> int | None:
    sub = guards.read_token(authorization, "customer")
    return int(sub) if sub and sub.isdigit() else None


@app.post("/login")
def login(req: LoginRequest, request: Request):
    guards.rate_limit(request, "login", limit=10)
    customer = db.authenticate(req.email, req.password)
    if not customer:
        raise HTTPException(401, "Wrong email or password")
    return {"token": guards.make_token("customer", str(customer["id"]), hours=12), "name": customer["name"]}


@app.get("/me/orders")
def my_orders(authorization: str | None = Header(default=None)):
    customer_id = customer_id_from(authorization)
    if not customer_id:
        raise HTTPException(401, "Please sign in")
    return db.list_orders_for_customer(customer_id)


# ---------- buying books ----------
class CartLine(BaseModel):
    book_id: int
    qty: int = Field(ge=1, le=10)


class OrderRequest(BaseModel):
    items: list[CartLine] = Field(min_length=1, max_length=30)
    payment_method: str


@app.post("/orders", status_code=201)
def place_order(req: OrderRequest, request: Request, authorization: str | None = Header(default=None)):
    customer_id = customer_id_from(authorization)
    if not customer_id:
        raise HTTPException(401, "Please sign in to place an order")
    guards.rate_limit(request, "order", limit=10)
    try:
        return db.create_order(customer_id, [(i.book_id, i.qty) for i in req.items], req.payment_method)
    except db.OrderError as e:
        raise HTTPException(400, str(e))


@app.post("/orders/quote")
def quote(req: OrderRequest):
    """Price a cart (delivery and cash-on-delivery rules) without placing it."""
    subtotal = 0
    for i in req.items:
        book = db.get_book(i.book_id)
        if not book:
            raise HTTPException(400, "A book in your cart no longer exists")
        subtotal += book["price"] * i.qty
    try:
        return db.price_order(subtotal, req.payment_method)
    except db.OrderError as e:
        raise HTTPException(400, str(e))


# ---------- chat with Paige ----------
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    session_id: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    ticket_id: str | None = None


async def run_once(runner: Runner, session_id: str, message: str) -> tuple[str, str | None]:
    reply, ticket_id = "", None
    async for event in runner.run_async(
        user_id="web",
        session_id=session_id,
        new_message=types.Content(role="user", parts=[types.Part(text=message)]),
    ):
        # Pick up the ticket ID straight from the tool result (made by the database, never by the model).
        for fr in event.get_function_responses() or []:
            if fr.name == "create_ticket":
                resp = fr.response or {}
                ticket_id = resp.get("result") if isinstance(resp, dict) else str(resp)
        if event.content and event.content.parts:
            reply += "".join(p.text or "" for p in event.content.parts if p.text)
    return reply.strip(), ticket_id


TICKET_PATTERN = re.compile(r"TKT-\d+", re.I)
RETRY_NUDGE = (
    "(Automatic check: your last reply mentioned a ticket ID that create_ticket never returned. "
    "If a person is needed, call create_ticket now and share only the ID it returns. Otherwise answer without any ticket ID.)"
)


def invented_ticket(reply: str, real_id: str | None) -> bool:
    """True if the reply names a ticket ID that the ticket tool did not actually return."""
    return any(m.upper() != (real_id or "").upper() for m in TICKET_PATTERN.findall(reply))


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request, authorization: str | None = Header(default=None)):
    guards.rate_limit(request, "chat", limit=20)
    sessions: InMemorySessionService = app.state.sessions
    customer_id = customer_id_from(authorization)  # None = guest
    existing = (
        await sessions.get_session(app_name=APP_NAME, user_id="web", session_id=req.session_id)
        if req.session_id else None
    )
    # A session is tied to who opened it: if the sign-in changed, start a fresh one.
    if not existing or existing.state.get("customer_id") != customer_id:
        existing = await sessions.create_session(app_name=APP_NAME, user_id="web", state={"customer_id": customer_id})
    session_id = existing.id

    try:
        try:
            reply, ticket_id = await run_once(app.state.runner, session_id, req.message)
        except Exception as e:
            if not any(k in str(e) for k in BUSY_MARKERS):
                raise
            reply, ticket_id = await run_once(app.state.fallback_runner, session_id, req.message)  # one retry
        if invented_ticket(reply, ticket_id):  # the model wrote a ticket ID without really creating one
            reply, ticket_id = await run_once(app.state.runner, session_id, RETRY_NUDGE)
            if invented_ticket(reply, ticket_id):
                reply, ticket_id = (
                    "Sorry, I couldn't raise that ticket just now. Please try again in a moment.", None
                )
    except Exception as e:
        if any(k in str(e) for k in BUSY_MARKERS):
            raise HTTPException(503, "Paige is busy right now. Please try again in a minute.")
        raise HTTPException(500, "Something went wrong on our side.")
    return ChatResponse(session_id=session_id, reply=reply, ticket_id=ticket_id)


# ---------- staff dashboard (passcode-protected) ----------
class AdminLogin(BaseModel):
    passcode: str = Field(max_length=200)


class StatusUpdate(BaseModel):
    status: str


def require_admin(authorization: str | None = Header(default=None)) -> None:
    if guards.read_token(authorization, "admin") is None:
        raise HTTPException(401, "Staff sign-in required")


@app.post("/admin/login")
def admin_login(req: AdminLogin, request: Request):
    guards.rate_limit(request, "admin-login", limit=5)
    if not secrets.compare_digest(req.passcode.encode(), guards.ADMIN_PASSCODE.encode()):
        raise HTTPException(401, "Wrong passcode")
    return {"token": guards.make_token("admin", "staff", hours=8)}


@app.get("/admin/tickets", dependencies=[Depends(require_admin)])
def admin_tickets(status: str | None = None):
    return db.list_tickets(status)


@app.patch("/admin/tickets/{ticket_id}", dependencies=[Depends(require_admin)])
def admin_update_ticket(ticket_id: str, body: StatusUpdate):
    if body.status not in db.TICKET_STATUSES:
        raise HTTPException(422, f"status must be one of {db.TICKET_STATUSES}")
    updated = db.update_ticket_status(ticket_id, body.status)
    if not updated:
        raise HTTPException(404, "Ticket not found")
    return updated


@app.get("/admin/stats", dependencies=[Depends(require_admin)])
def admin_stats():
    return db.ticket_stats()


# ---------- books (public) ----------
@app.get("/books")
def books(q: str = "", genre: str = "", condition: str = ""):
    return db.list_books(q, genre, condition)


@app.get("/books/{book_id}")
def book(book_id: int):
    row = db.get_book(book_id)
    if not row:
        raise HTTPException(404, "Book not found")
    return row
