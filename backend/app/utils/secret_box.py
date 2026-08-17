"""Encrypt/decrypt short secrets at rest (Fernet)."""

from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken
from flask import current_app

from app.utils.exceptions import ValidationError


def _fernet() -> Fernet:
    raw = (
        current_app.config.get("WHATSAPP_TOKEN_ENCRYPTION_KEY")
        or current_app.config.get("SECRET_KEY")
        or ""
    )
    # Derive a stable 32-byte url-safe key from configured secret
    digest = hashlib.sha256(raw.encode("utf-8")).digest()
    key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def encrypt_secret(plaintext: str) -> str:
    if not plaintext:
        raise ValidationError("Access token is required.")
    return _fernet().encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_secret(ciphertext: str) -> str:
    if not ciphertext:
        raise ValidationError("WhatsApp access token is not configured.")
    try:
        return _fernet().decrypt(ciphertext.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise ValidationError(
            "WhatsApp credentials could not be decrypted. Re-save the access token."
        ) from exc
