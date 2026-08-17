"""Email helpers for customer bill delivery."""

from __future__ import annotations

import re

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_email(value: str | None) -> str:
    email = (value or "").strip().lower()
    if not email or not _EMAIL_RE.match(email) or len(email) > 255:
        raise ValueError("Enter a valid email address.")
    return email


def mask_email(value: str | None) -> str | None:
    if not value:
        return None
    email = str(value).strip()
    if "@" not in email:
        return "***"
    local, _, domain = email.partition("@")
    if not local:
        return f"***@{domain}"
    if len(local) == 1:
        masked_local = "*"
    else:
        masked_local = local[0] + ("*" * min(len(local) - 1, 6))
    return f"{masked_local}@{domain}"
