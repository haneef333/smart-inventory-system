"""
Owner login for the inventory app.

Set OWNER_PASSWORD to turn it on. Without it the app stays open, as before,
which is handy on your own computer but should never be the case once deployed.

Tokens are signed with HMAC (standard library only, no extra packages) and last
7 days. Changing OWNER_PASSWORD logs everyone out, because the signing key is
derived from it.
"""

import base64
import hashlib
import hmac
import json
import os
import time
from collections import defaultdict, deque

from fastapi import APIRouter, HTTPException, Request

from schemas import OwnerLogin

OWNER_PASSWORD = os.getenv("OWNER_PASSWORD", "")
TOKEN_DAYS = 7
_SIGNING_KEY = (
    os.getenv("OWNER_TOKEN_SECRET")
    or hashlib.sha256(f"owner:{OWNER_PASSWORD}:{os.getenv('INTEGRATION_SECRET', '')}".encode()).hexdigest()
).encode()

if not OWNER_PASSWORD:
    print("[auth] OWNER_PASSWORD is not set: the inventory app is open to anyone with its link.")

router = APIRouter(prefix="/api/auth", tags=["auth"])


def auth_enabled() -> bool:
    return bool(OWNER_PASSWORD)


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def _sign(payload: str) -> str:
    return _b64(hmac.new(_SIGNING_KEY, payload.encode(), hashlib.sha256).digest())


def create_token() -> tuple[str, int]:
    expires_at = int(time.time()) + TOKEN_DAYS * 86400
    payload = _b64(json.dumps({"exp": expires_at, "role": "owner"}).encode())
    return f"{payload}.{_sign(payload)}", expires_at


def verify_token(token: str | None) -> bool:
    if not token or "." not in token:
        return False
    payload, signature = token.rsplit(".", 1)
    if not hmac.compare_digest(signature, _sign(payload)):
        return False
    try:
        data = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    except ValueError:
        return False
    return data.get("exp", 0) > time.time()


def token_from_header(authorization: str | None) -> str | None:
    if authorization and authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return None


# Slow down password guessing: at most 5 attempts per minute per address
_attempts: dict[str, deque] = defaultdict(deque)


def _check_rate_limit(ip: str):
    now = time.time()
    window = _attempts[ip]
    while window and now - window[0] > 60:
        window.popleft()
    if len(window) >= 5:
        raise HTTPException(status_code=429, detail="Too many attempts. Wait a minute and try again.")
    window.append(now)


@router.get("/status")
def auth_status():
    return {"auth_required": auth_enabled()}


@router.post("/login")
def login(body: OwnerLogin, request: Request):
    if not auth_enabled():
        token, expires_at = create_token()
        return {"token": token, "expires_at": expires_at}
    _check_rate_limit(request.client.host if request.client else "unknown")
    if not hmac.compare_digest(body.password.encode(), OWNER_PASSWORD.encode()):
        raise HTTPException(status_code=401, detail="That password is not right.")
    token, expires_at = create_token()
    return {"token": token, "expires_at": expires_at}
