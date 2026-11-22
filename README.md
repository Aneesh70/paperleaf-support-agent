# PaperLeaf Books: AI support agent, shop and staff dashboard

A made-up online bookstore with **Paige**, an AI support agent built on Google ADK and Gemini. All data is made up for practice.

## What it does
- **Paige** answers from the store's FAQ sheet, shows the source category, looks up the signed-in customer's own orders, suggests books, and hands off to a person by raising a **ticket** (ID made by the database, never by the model).
- **Guardrails:** stays on topic, never shares another customer's details, never promises refunds, discounts or free items, never asks for card numbers, OTPs or passwords, and ignores requests to break these rules.
- **Shop (Next.js):** catalogue, book pages, customer sign-in, "My orders", and a chat widget with Paige.
- **Staff dashboard (`/admin`):** passcode-protected ticket table with status updates, stat tiles and charts.

## Architecture

```
 Browser ──► Next.js shop (Vercel)  ──HTTPS──►  FastAPI (Render)  ──►  Postgres (SQLite locally)
              /books /orders /admin               /chat /login /admin/*       books, customers, orders, tickets
                                                       │
                                                       └──► Paige: Google ADK agent + Gemini
                                                            tools: create_ticket, get_order_status,
                                                                   list_my_orders, search_books
                                                            knowledge: FAQ Google Sheet (loaded at start)
```

Privacy by design: the customer's identity comes from a signed login token held in the chat session. The model never supplies it, so an order that belongs to someone else looks exactly like an order that does not exist.

## Run it locally
```
python -m venv .venv
.venv\Scripts\pip install -r api\requirements.txt
copy .env.example paperleaf_agent\.env        # then put your Gemini key in it
.venv\Scripts\uvicorn api.main:app --port 8100

cd web
copy .env.example .env.local
npm install
npm run dev -- --port 3001
```
Open http://localhost:3001. Demo customers sign in with their email and the password `paperleaf123` (for example `aarav.mehta@example.com`). The staff dashboard is at `/admin` (local passcode `admin-demo`).

## Tests
```
.venv\Scripts\python -m pytest tests -q            # fast unit and API tests, no model calls
.venv\Scripts\python tests\live_guardrails.py      # 27 tricky messages against the real model
```

## Security notes
- Passwords are hashed (scrypt). Login and chat are rate limited per IP. Tokens are signed and expire.
- With `APP_ENV=production` the API refuses to start unless `JWT_SECRET`, `ADMIN_PASSCODE` and `ALLOWED_ORIGINS` are set properly.
- Secrets live in environment variables only (see `.env.example`). Real `.env` files are git-ignored.
- If the main Gemini model is busy, the API retries once on a backup model (`FALLBACK_MODEL`).

## Project history
`main` holds the original Streamlit version (steps 1 to 4 of the course brief). The full-stack version lives on the feature branches.
