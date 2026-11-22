"""FastAPI backend that wraps the same ADK agent (Paige) for the Next.js frontend.

Run from the project root:  uvicorn api.main:app --reload --port 8100
"""
import os
import secrets
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

BASE = Path(__file__).resolve().parent.parent
load_dotenv(BASE / "paperleaf_agent" / ".env")

from google.adk.runners import InMemoryRunner  # noqa: E402
from google.genai import types  # noqa: E402

from paperleaf_agent.agent import root_agent  # noqa: E402
from paperleaf_agent import db  # noqa: E402

APP_NAME = "paperleaf_api"
GREETING = "Hello, I'm Paige from PaperLeaf Books. How can I help you today?"
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.runner = InMemoryRunner(agent=root_agent, app_name=APP_NAME)
    yield


app = FastAPI(title="PaperLeaf Books API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Demo sign-in: made-up customers, email only, token kept in memory. (Real auth is a later stage.)
TOKENS: dict[str, int] = {}


class LoginRequest(BaseModel):
    email: str


def customer_from_token(authorization: str | None) -> int | None:
    if authorization and authorization.lower().startswith("bearer "):
        return TOKENS.get(authorization[7:].strip())
    return None


@app.post("/login")
def login(req: LoginRequest):
    customer = db.get_customer_by_email(req.email)
    if not customer:
        raise HTTPException(401, "Unknown email")
    token = secrets.token_urlsafe(24)
    TOKENS[token] = customer["id"]
    return {"token": token, "name": customer["name"]}


@app.get("/me/orders")
def my_orders(authorization: str | None = Header(default=None)):
    customer_id = customer_from_token(authorization)
    if not customer_id:
        raise HTTPException(401, "Please sign in")
    return db.list_orders_for_customer(customer_id)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    session_id: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    ticket_id: str | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/greeting")
def greeting():
    return {"greeting": GREETING}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, authorization: str | None = Header(default=None)):
    runner: InMemoryRunner = app.state.runner
    customer_id = customer_from_token(authorization)  # None = guest
    session_id = req.session_id
    existing = (
        await runner.session_service.get_session(app_name=APP_NAME, user_id="web", session_id=session_id)
        if session_id else None
    )
    # A session is tied to who opened it: if the sign-in changed, start a fresh one.
    if not existing or existing.state.get("customer_id") != customer_id:
        session = await runner.session_service.create_session(
            app_name=APP_NAME, user_id="web", state={"customer_id": customer_id}
        )
        session_id = session.id

    reply, ticket_id = "", None
    try:
        async for event in runner.run_async(
            user_id="web",
            session_id=session_id,
            new_message=types.Content(role="user", parts=[types.Part(text=req.message)]),
        ):
            # Pick up the ticket ID straight from the tool result (code-made, never from the model).
            for fr in event.get_function_responses() or []:
                if fr.name == "create_ticket":
                    resp = fr.response or {}
                    ticket_id = resp.get("result") if isinstance(resp, dict) else str(resp)
            if event.content and event.content.parts:
                reply += "".join(p.text or "" for p in event.content.parts if p.text)
    except Exception as e:
        msg = str(e)
        if any(k in msg for k in ("429", "RESOURCE_EXHAUSTED", "503", "UNAVAILABLE")):
            raise HTTPException(503, "Paige is busy right now. Please try again in a minute.")
        raise HTTPException(500, "Something went wrong on our side.")
    return ChatResponse(session_id=session_id, reply=reply.strip(), ticket_id=ticket_id)


@app.get("/tickets")
def tickets(status: str | None = None):
    return db.list_tickets(status)


@app.get("/books")
def books(q: str | None = None, genre: str | None = None, condition: str | None = None):
    sql, args = "SELECT * FROM books WHERE 1=1", []
    if q:
        sql += " AND (title LIKE ? OR author LIKE ?)"
        args += [f"%{q}%", f"%{q}%"]
    if genre:
        sql += " AND genre = ?"
        args.append(genre)
    if condition:
        sql += " AND condition = ?"
        args.append(condition)
    conn = db.get_conn()
    try:
        return [dict(r) for r in conn.execute(sql + " ORDER BY title", args).fetchall()]
    finally:
        conn.close()


@app.get("/books/{book_id}")
def book(book_id: int):
    conn = db.get_conn()
    try:
        row = conn.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    finally:
        conn.close()
    if not row:
        raise HTTPException(404, "Book not found")
    return dict(row)
