import asyncio
import os
import threading
import uuid
from pathlib import Path

import streamlit as st

BASE = Path(__file__).parent
GREETING = "Hello, I'm Paige from PaperLeaf Books. How can I help you today?"

st.set_page_config(page_title="PaperLeaf Books Support", page_icon="📚")


# ---------- secrets: Streamlit secrets when deployed, .env on the laptop ----------
def get_secret(name: str):
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:  # no secrets.toml on this machine
        pass
    return None


if not os.environ.get("GOOGLE_API_KEY"):
    key = get_secret("GOOGLE_API_KEY")
    if key:
        os.environ["GOOGLE_API_KEY"] = key
    else:
        from dotenv import load_dotenv

        load_dotenv(BASE / "paperleaf_agent" / ".env")


# ---------- one background event loop for ADK (it is async, Streamlit is not) ----------
@st.cache_resource
def get_loop():
    loop = asyncio.new_event_loop()
    threading.Thread(target=loop.run_forever, daemon=True).start()
    return loop


def run_async(coro):
    return asyncio.run_coroutine_threadsafe(coro, get_loop()).result(timeout=120)


@st.cache_resource
def get_runner():
    from google.adk.runners import InMemoryRunner

    from paperleaf_agent.agent import root_agent  # same ADK agent as adk web

    return InMemoryRunner(agent=root_agent, app_name="paperleaf_web")


async def ask_paige(runner, session_id: str, text: str) -> str:
    from google.genai import types

    reply = ""
    async for event in runner.run_async(
        user_id="web_user",
        session_id=session_id,
        new_message=types.Content(role="user", parts=[types.Part(text=text)]),
    ):
        if event.content and event.content.parts:
            reply += "".join(p.text or "" for p in event.content.parts)
    return reply.strip()


def new_session(runner) -> str:
    session = run_async(
        runner.session_service.create_session(app_name="paperleaf_web", user_id="web_user")
    )
    return session.id


def open_tickets():
    from paperleaf_agent import db

    return db.list_tickets("open")[::-1]


# ---------- page ----------
st.title("📚 PaperLeaf Books Support")

# Passcode gate
if not st.session_state.get("unlocked"):
    expected = get_secret("APP_PASSCODE")
    if not expected:
        st.error("APP_PASSCODE is not set in Streamlit secrets.")
        st.stop()
    with st.form("passcode"):
        entered = st.text_input("Enter the passcode to open the chat", type="password")
        if st.form_submit_button("Open chat"):
            if entered == str(expected):
                st.session_state.unlocked = True
                st.rerun()
            else:
                st.error("Wrong passcode.")
    st.stop()

if not os.environ.get("GOOGLE_API_KEY"):
    st.error("GOOGLE_API_KEY is missing. Add it to Streamlit secrets (or .env on your laptop).")
    st.stop()

runner = get_runner()
if "session_id" not in st.session_state:
    st.session_state.session_id = new_session(runner)
    st.session_state.messages = [{"role": "assistant", "content": GREETING}]

# Chat bubbles
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Ask Paige about orders, delivery, payments, returns..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Paige is thinking..."):
            try:
                reply = run_async(ask_paige(runner, st.session_state.session_id, prompt))
            except Exception as e:
                msg = str(e)
                if "429" in msg or "RESOURCE_EXHAUSTED" in msg or "503" in msg or "UNAVAILABLE" in msg:
                    reply = "Sorry, I'm a little busy right now. Please try again in a minute."
                else:
                    reply = "Sorry, something went wrong on my side. Please try again."
        st.markdown(reply or "Sorry, I didn't catch that. Could you rephrase?")
    st.session_state.messages.append({"role": "assistant", "content": reply})

# Sidebar: open tickets (rendered after the reply so a new ticket shows straight away)
with st.sidebar:
    st.header("🎫 Open tickets")
    tickets = open_tickets()
    if not tickets:
        st.caption("No open tickets.")
    for t in reversed(tickets):
        st.markdown(f"**{t['ticket_id']}** · {t['priority']}  \n{t['reason']}  \n_{t['time']}_")
        st.divider()
