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


APP_DISPLAY_NAME = "Business Billing Software"


class EmailService:
    @staticmethod
    def clear_outbox():
        _outbox.clear()

    @staticmethod
    def get_outbox() -> list[dict]:
        return list(_outbox)

    @staticmethod
    def send_email(
        *,
        to: str,
        subject: str,
        html_body: str,
        text_body: str | None = None,
        attachments: list[dict] | None = None,
    ):
        sender = current_app.config.get("MAIL_DEFAULT_SENDER") or "noreply@localhost"
        message = {
            "to": to,
            "subject": subject,
            "html": html_body,
            "text": text_body or "",
            "from": sender,
            "attachments": [
                {
                    "filename": a.get("filename"),
                    "maintype": a.get("maintype", "application"),
                    "subtype": a.get("subtype", "octet-stream"),
                    "size": len(a.get("data") or b""),
                }
                for a in (attachments or [])
            ],
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
        for attachment in attachments or []:
            data = attachment.get("data") or b""
            msg.add_attachment(
                data,
                maintype=attachment.get("maintype") or "application",
                subtype=attachment.get("subtype") or "octet-stream",
                filename=attachment.get("filename") or "attachment.bin",
            )

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
        context.setdefault("app_name", APP_DISPLAY_NAME)
        return render_template_string(raw, **context)

    @staticmethod
    def send_bill_pdf(
        *,
        to: str,
        customer_name: str | None,
        business_name: str,
        bill_number: str,
        amount: str,
        pdf_bytes: bytes,
        filename: str,
    ):
        display_name = (customer_name or "Customer").strip() or "Customer"
        html = EmailService._render(
            "bill_delivery.html",
            customer_name=display_name,
            business_name=business_name,
            bill_number=bill_number,
            amount=amount,
        )
        EmailService.send_email(
            to=to,
            subject=f"Your bill {bill_number} from {business_name}",
            html_body=html,
            text_body=(
                f"Hello {display_name},\n\n"
                f"Please find bill {bill_number} (₹{amount}) attached as a PDF.\n"
                f"— {business_name}\n"
            ),
            attachments=[
                {
                    "filename": filename,
                    "maintype": "application",
                    "subtype": "pdf",
                    "data": pdf_bytes,
                }
            ],
        )

    @staticmethod
    def send_verification_email(*, to: str, name: str, verify_url: str):
        html = EmailService._render(
            "verify_email.html",
            name=name,
            verify_url=verify_url,
        )
        EmailService.send_email(
            to=to,
            subject="Verify your business account",
            html_body=html,
            text_body=f"Hello {name},\n\nVerify your account: {verify_url}\n",
        )

    @staticmethod
    def send_password_reset_email(*, to: str, name: str, reset_url: str):
        html = EmailService._render(
            "reset_password.html",
            name=name,
            reset_url=reset_url,
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
        )
        EmailService.send_email(
            to=to,
            subject="New login to your account",
            html_body=html,
            text_body=f"Hello {name},\n\nNew login detected from {ip_address or 'unknown'}.\n",
        )

    @staticmethod
    def send_registration_received_email(*, to: str, name: str, business_name: str):
        html = EmailService._render(
            "registration_received.html",
            name=name,
            business_name=business_name,
        )
        EmailService.send_email(
            to=to,
            subject="We received your Business Billing registration",
            html_body=html,
            text_body=(
                f"Hello {name},\n\n"
                f"Your registration request for {business_name} has been submitted successfully. "
                "Your account will be activated after approval by Prabha Technology.\n"
            ),
        )

    @staticmethod
    def send_registration_approved_email(
        *,
        to: str,
        name: str,
        business_name: str,
        login_url: str,
        trial_days: int | None = None,
        trial_ends_at: str | None = None,
    ):
        html = EmailService._render(
            "registration_approved.html",
            name=name,
            business_name=business_name,
            login_url=login_url,
            trial_days=trial_days,
            trial_ends_at=trial_ends_at,
        )
        trial_line = ""
        if trial_days:
            trial_line = (
                f"Your free trial is {trial_days} days"
                + (f" (until {trial_ends_at}).\n" if trial_ends_at else ".\n")
            )
        EmailService.send_email(
            to=to,
            subject="Your Business Billing account is approved",
            html_body=html,
            text_body=(
                f"Hello {name},\n\n"
                f"Your registration for {business_name} has been approved. "
                f"{trial_line}"
                f"You can sign in at {login_url}\n"
            ),
        )

    @staticmethod
    def send_registration_rejected_email(
        *, to: str, name: str, business_name: str, reason: str
    ):
        html = EmailService._render(
            "registration_rejected.html",
            name=name,
            business_name=business_name,
            reason=reason,
        )
        EmailService.send_email(
            to=to,
            subject="Update on your Business Billing registration",
            html_body=html,
            text_body=(
                f"Hello {name},\n\n"
                f"Your registration for {business_name} was not approved.\n"
                f"Reason: {reason}\n"
            ),
        )

    @staticmethod
    def send_subscription_expiring_email(
        *,
        to: str,
        name: str,
        business_name: str,
        remaining_days: int,
        login_url: str,
        ends_at: str | None = None,
    ):
        days = int(remaining_days)
        day_word = "day" if days == 1 else "days"
        html = EmailService._render(
            "subscription_expiring.html",
            name=name,
            business_name=business_name,
            remaining_days=days,
            day_word=day_word,
            ends_at=ends_at,
            login_url=login_url,
        )
        until = f" (until {ends_at})" if ends_at else ""
        EmailService.send_email(
            to=to,
            subject=f"Your {APP_DISPLAY_NAME} subscription expires in {days} {day_word}",
            html_body=html,
            text_body=(
                f"Hello {name},\n\n"
                f"Your subscription for {business_name} expires in {days} {day_word}{until}. "
                "Contact Prabha Technology to renew access.\n"
                f"Sign in: {login_url}\n"
            ),
        )

    @staticmethod
    def send_subscription_expired_email(
        *,
        to: str,
        name: str,
        business_name: str,
        login_url: str,
    ):
        html = EmailService._render(
            "subscription_expired.html",
            name=name,
            business_name=business_name,
            login_url=login_url,
        )
        EmailService.send_email(
            to=to,
            subject=f"Your {APP_DISPLAY_NAME} subscription has expired",
            html_body=html,
            text_body=(
                f"Hello {name},\n\n"
                f"Your subscription for {business_name} has expired. "
                "You can still sign in, but billing is locked until Prabha Technology renews access.\n"
                f"Sign in: {login_url}\n"
            ),
        )
