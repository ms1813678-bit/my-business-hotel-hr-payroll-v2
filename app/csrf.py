import secrets
from typing import Optional

from fastapi import Request, HTTPException


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def set_csrf_token(request: Request) -> str:
    token = generate_csrf_token()
    request.session["csrf_token"] = token
    return token


def validate_csrf_token(request: Request, token: Optional[str]) -> None:
    expected = request.session.get("csrf_token")
    if not expected or not token or not secrets.compare_digest(expected, token):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")
