"""Secure opaque tokens (store only hashes)."""

import hashlib
import secrets
from datetime import datetime, timedelta, timezone


def generate_token(nbytes: int = 32) -> str:
    return secrets.token_urlsafe(nbytes)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def expires_at(hours: float = 24) -> datetime:
    return utc_now_naive() + timedelta(hours=hours)
