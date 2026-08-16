"""Send existing bills via email PDF (never creates a new bill)."""

from datetime import datetime, timezone

from app.extensions import db
from app.models.bill_delivery import BillDelivery
from app.repositories.bill_delivery_repository import BillDeliveryRepository
from app.repositories.bill_repository import BillRepository
from app.repositories.tenant_repository import TenantRepository
from app.services.audit_service import AuditService
from app.services.bill_pdf_service import BillPdfService
from app.services.bill_service import BillService
from app.services.email_service import EmailService
from app.utils.email_address import mask_email, normalize_email
from app.utils.exceptions import NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.request_context import require_request_context


class EmailBillService:
    @staticmethod
    def send_bill(
        bill_id: str,
        *,
        email: str | None = None,
        customer_name: str | None = None,
    ):
        ctx = require_request_context()
        bill = BillRepository.get_by_id_and_tenant(bill_id, ctx.tenant_id)
        if bill is None:
            raise NotFoundError("Bill not found")
        if bill.status != "FINALIZED":
            raise ValidationError("Only finalized bills can be sent by email.")

        if customer_name is not None and str(customer_name).strip():
            bill.customer_name = str(customer_name).strip()[:120]

        try:
            if email is not None and str(email).strip():
                resolved = normalize_email(email)
            elif bill.customer_email:
                resolved = normalize_email(bill.customer_email)
            else:
                raise ValidationError("Customer email is required to send this bill.")
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

        bill.customer_email = resolved
        masked = mask_email(resolved)

        delivery = BillDelivery(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            bill_id=bill.id,
            delivery_method="EMAIL",
            recipient_email=resolved,
            recipient_email_masked=masked,
            status="PENDING",
            attempted_by=ctx.user_id,
        )
        BillDeliveryRepository.add(delivery)
        db.session.flush()

        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        business_name = (
            (tenant.business_name or tenant.name or "Business") if tenant else "Business"
        )
        pdf_bytes = BillPdfService.build_pdf_bytes(bill)
        filename = f"{bill.bill_number}.pdf"

        try:
            EmailService.send_bill_pdf(
                to=resolved,
                customer_name=bill.customer_name,
                business_name=business_name,
                bill_number=bill.bill_number,
                amount=f"{float(bill.grand_total):.2f}",
                pdf_bytes=pdf_bytes,
                filename=filename,
            )
        except Exception as exc:
            delivery.status = "FAILED"
            delivery.error_message = str(exc)[:500]
            AuditService.log(
                tenant_id=ctx.tenant_id,
                action="BILL_EMAIL_FAILED",
                entity_type="BILL",
                entity_id=bill.id,
                new_data={
                    "bill_number": bill.bill_number,
                    "recipient": masked,
                    "delivery_id": delivery.id,
                    "error": delivery.error_message,
                },
            )
            from app.services.notification_service import NotificationService

            NotificationService.notify_email_delivery_failed(
                tenant_id=ctx.tenant_id,
                bill_id=bill.id,
                delivery_id=delivery.id,
                bill_number=bill.bill_number,
                error_message=delivery.error_message,
                recipient_masked=masked,
            )
            db.session.commit()
            raise ValidationError(
                "Unable to send the bill by email. Please try again or use Print Bill."
            ) from exc

        delivery.status = "SENT"
        delivery.sent_at = datetime.now(timezone.utc).replace(tzinfo=None)
        delivery.error_message = None
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="BILL_SENT_EMAIL",
            entity_type="BILL",
            entity_id=bill.id,
            new_data={
                "bill_number": bill.bill_number,
                "recipient": masked,
                "delivery_id": delivery.id,
            },
        )
        db.session.commit()

        from app.services.whatsapp_bill_service import WhatsappBillService

        return {
            "message": "Bill sent successfully by email.",
            "delivery": WhatsappBillService.serialize_delivery(delivery),
            "bill": BillService.serialize(
                bill,
                include_items=True,
                email_delivery_status="SENT",
            ),
        }
