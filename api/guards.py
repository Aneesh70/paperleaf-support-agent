"""Settings, signed tokens and rate limiting for the API."""
import os
import secrets
import threading
import time
from collections import defaultdict, deque

import jwt
from fastapi import HTTPException, Request

IS_PROD = os.environ.get("APP_ENV", "development").lower() == "production"
_DEV_ADMIN = "admin-demo"
ADMIN_PASSCODE = os.environ.get("ADMIN_PASSCODE", _DEV_ADMIN)
JWT_SECRET = os.environ.get("JWT_SECRET") or secrets.token_urlsafe(32)  # random per start in dev only
JWT_ALGO = "HS256"


def check_production_settings() -> None:
    """In production, refuse to start with weak or missing secrets."""
    if not IS_PROD:
        return
    problems = []
    if not os.environ.get("JWT_SECRET") or len(os.environ["JWT_SECRET"]) < 32:
        problems.append("JWT_SECRET must be set (at least 32 characters)")
    if ADMIN_PASSCODE == _DEV_ADMIN or len(ADMIN_PASSCODE) < 8:
        problems.append("ADMIN_PASSCODE must be set to something other than the demo value (8+ characters)")
    if not os.environ.get("ALLOWED_ORIGINS"):
        problems.append("ALLOWED_ORIGINS must be set to the shop's URL")
    if problems:
        raise RuntimeError("Unsafe production settings: " + "; ".join(problems))


# ---------- signed tokens (survive restarts, work across instances) ----------
def make_token(role: str, subject: str, hours: int) -> str:
    now = int(time.time())
    return jwt.encode({"role": role, "sub": subject, "iat": now, "exp": now + hours * 3600}, JWT_SECRET, JWT_ALGO)


def read_token(authorization: str | None, role: str) -> str | None:
    """Return the token's subject if it is a valid, unexpired token for this role, else None."""
    if not (authorization and authorization.lower().startswith("bearer ")):
        return None
    try:
        data = jwt.decode(authorization[7:].strip(), JWT_SECRET, algorithms=[JWT_ALGO])
    except jwt.PyJWTError:
        return None
    return data.get("sub") if data.get("role") == role else None


# ---------- rate limiting (per client IP, in memory) ----------
_hits: dict[str, deque] = defaultdict(deque)
_lock = threading.Lock()


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")  # set by Render's proxy
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limit(request: Request, bucket: str, limit: int, window_seconds: int = 60) -> None:
    key, now = f"{bucket}:{client_ip(request)}", time.monotonic()
    with _lock:
        q = _hits[key]
        while q and now - q[0] > window_seconds:
            q.popleft()
        if len(q) >= limit:
            retry = int(window_seconds - (now - q[0])) + 1
            raise HTTPException(429, f"Too many requests. Please wait {retry} seconds and try again.",
                                headers={"Retry-After": str(retry)})
        q.append(now)
        if len(_hits) > 5000:  # keep memory bounded
            for k in [k for k, v in _hits.items() if not v or now - v[-1] > window_seconds]:
                _hits.pop(k, None)
