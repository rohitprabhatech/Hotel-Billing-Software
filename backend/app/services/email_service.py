"""SMTP email delivery — provider configured via environment only."""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage
from pathlib import Path

from flask import current_app, render_template_string

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates" / "emails"

# In-memory outbox for tests / suppressed send
_outbox: list[dict] = []


class EmailService:
    @staticmethod
    def clear_outbox():
        _outbox.clear()

    @staticmethod
    def get_outbox() -> list[dict]:
        return list(_outbox)

    @staticmethod
    def send_email(*, to: str, subject: str, html_body: str, text_body: str | None = None):
        sender = current_app.config.get("MAIL_DEFAULT_SENDER") or "noreply@localhost"
        message = {
            "to": to,
            "subject": subject,
            "html": html_body,
            "text": text_body or "",
            "from": sender,
        }
        _outbox.append(message)

        if current_app.config.get("MAIL_SUPPRESS_SEND"):
            logger.info("MAIL_SUPPRESS_SEND: skipped email to %s (%s)", to, subject)
            return

        if not current_app.config.get("MAIL_SERVER"):
            logger.warning("MAIL_SERVER not configured; email to %s logged only", to)
            return

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = to
        msg.set_content(text_body or subject)
        msg.add_alternative(html_body, subtype="html")

        host = current_app.config["MAIL_SERVER"]
        port = int(current_app.config.get("MAIL_PORT") or 587)
        username = current_app.config.get("MAIL_USERNAME")
        password = current_app.config.get("MAIL_PASSWORD")
        use_tls = bool(current_app.config.get("MAIL_USE_TLS", True))
        use_ssl = bool(current_app.config.get("MAIL_USE_SSL", False))

        if use_ssl:
            with smtplib.SMTP_SSL(host, port, timeout=30) as smtp:
                if username:
                    smtp.login(username, password or "")
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(host, port, timeout=30) as smtp:
                if use_tls:
                    smtp.starttls()
                if username:
                    smtp.login(username, password or "")
                smtp.send_message(msg)

    @staticmethod
    def _render(template_name: str, **context) -> str:
        path = TEMPLATE_DIR / template_name
        raw = path.read_text(encoding="utf-8")
        return render_template_string(raw, **context)

    @staticmethod
    def send_verification_email(*, to: str, name: str, verify_url: str):
        html = EmailService._render(
            "verify_email.html",
            name=name,
            verify_url=verify_url,
            app_name="Hotel Billing Software",
        )
        EmailService.send_email(
            to=to,
            subject="Verify your hotel account",
            html_body=html,
            text_body=f"Hello {name},\n\nVerify your account: {verify_url}\n",
        )

    @staticmethod
    def send_password_reset_email(*, to: str, name: str, reset_url: str):
        html = EmailService._render(
            "reset_password.html",
            name=name,
            reset_url=reset_url,
            app_name="Hotel Billing Software",
        )
        EmailService.send_email(
            to=to,
            subject="Reset your password",
            html_body=html,
            text_body=f"Hello {name},\n\nReset your password: {reset_url}\n",
        )

    @staticmethod
    def send_password_changed_email(*, to: str, name: str):
        html = EmailService._render(
            "password_changed.html",
            name=name,
            app_name="Hotel Billing Software",
        )
        EmailService.send_email(
            to=to,
            subject="Your password was changed",
            html_body=html,
            text_body=f"Hello {name},\n\nYour password was changed successfully.\n",
        )

    @staticmethod
    def send_login_notification(*, to: str, name: str, ip_address: str | None):
        html = EmailService._render(
            "login_notification.html",
            name=name,
            ip_address=ip_address or "unknown",
            app_name="Hotel Billing Software",
        )
        EmailService.send_email(
            to=to,
            subject="New login to your account",
            html_body=html,
            text_body=f"Hello {name},\n\nNew login detected from {ip_address or 'unknown'}.\n",
        )
