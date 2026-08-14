"""Send existing bills via WhatsApp Cloud API (never creates a new bill)."""

from datetime import datetime, timezone

from app.extensions import db
from app.models.bill_delivery import BillDelivery
from app.repositories.bill_delivery_repository import BillDeliveryRepository
from app.repositories.bill_repository import BillRepository
from app.services.audit_service import AuditService
from app.services.bill_pdf_service import BillPdfService
from app.services.bill_service import BillService
from app.services.whatsapp_config_service import WhatsappConfigService
from app.services.whatsapp_provider import WhatsAppProviderError, get_whatsapp_provider
from app.utils.exceptions import NotFoundError, ValidationError
from app.utils.ids import new_uuid
from app.utils.phone import normalize_phone
from app.utils.request_context import require_request_context
from app.utils.secret_box import decrypt_secret


class WhatsappBillService:
    @staticmethod
    def send_bill(
        bill_id: str,
        *,
        country_code: str | None = None,
        phone: str | None = None,
        customer_name: str | None = None,
    ):
        ctx = require_request_context()
        bill = BillRepository.get_by_id_and_tenant(bill_id, ctx.tenant_id)
        if bill is None:
            raise NotFoundError("Bill not found")
        if bill.status != "FINALIZED":
            raise ValidationError("Only finalized bills can be sent on WhatsApp.")

        # Resolve / update customer contact without recreating bill
        if customer_name is not None and str(customer_name).strip():
            bill.customer_name = str(customer_name).strip()[:120]

        if (country_code and phone) or (phone and str(phone).strip().startswith("+")) or phone:
            parsed = normalize_phone(country_code=country_code, national_number=phone, e164=None)
            bill.customer_phone_country_code = parsed["country_code"]
            bill.customer_phone_national = parsed["national"]
            bill.customer_phone_e164 = parsed["e164"]
        elif bill.customer_phone_e164:
            parsed = normalize_phone(e164=bill.customer_phone_e164)
        elif bill.customer_phone_country_code and bill.customer_phone_national:
            parsed = normalize_phone(
                country_code=bill.customer_phone_country_code,
                national_number=bill.customer_phone_national,
            )
            bill.customer_phone_e164 = parsed["e164"]
        else:
            raise ValidationError(
                "Customer WhatsApp number is required to send this bill."
            )

        config = WhatsappConfigService.require_ready_config(ctx.tenant_id)
        token = decrypt_secret(config.access_token_encrypted)

        delivery = BillDelivery(
            id=new_uuid(),
            tenant_id=ctx.tenant_id,
            bill_id=bill.id,
            delivery_method="WHATSAPP",
            recipient_phone_e164=parsed["e164"],
            recipient_phone_masked=parsed["masked"],
            status="PENDING",
            attempted_by=ctx.user_id,
        )
        BillDeliveryRepository.add(delivery)
        db.session.flush()

        pdf_bytes = BillPdfService.build_pdf_bytes(bill)
        filename = f"{bill.bill_number}.pdf"
        from app.repositories.tenant_repository import TenantRepository

        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        business_name = (tenant.business_name or tenant.name or "Business") if tenant else "Business"
        body_params = [
            business_name,
            bill.bill_number,
            f"{float(bill.grand_total):.2f}",
        ]

        provider = get_whatsapp_provider()
        try:
            result = provider.send_bill_document(
                access_token=token,
                phone_number_id=config.phone_number_id,
                recipient_e164=parsed["e164"],
                template_name=config.template_name,
                template_language=config.template_language or "en",
                pdf_bytes=pdf_bytes,
                filename=filename,
                body_params=body_params,
            )
        except WhatsAppProviderError as exc:
            delivery.status = "FAILED"
            delivery.error_message = exc.message
            AuditService.log(
                tenant_id=ctx.tenant_id,
                action="BILL_WHATSAPP_FAILED",
                entity_type="BILL",
                entity_id=bill.id,
                new_data={
                    "bill_number": bill.bill_number,
                    "recipient": parsed["masked"],
                    "delivery_id": delivery.id,
                    "error": exc.message,
                },
            )
            db.session.commit()
            raise ValidationError(
                "Unable to send the bill on WhatsApp. Please try again or use Print Bill."
            ) from exc

        if not result.success:
            delivery.status = "FAILED"
            delivery.error_message = result.error_message or "WhatsApp delivery failed."
            AuditService.log(
                tenant_id=ctx.tenant_id,
                action="BILL_WHATSAPP_FAILED",
                entity_type="BILL",
                entity_id=bill.id,
                new_data={
                    "bill_number": bill.bill_number,
                    "recipient": parsed["masked"],
                    "delivery_id": delivery.id,
                    "error": delivery.error_message,
                },
            )
            db.session.commit()
            raise ValidationError(
                result.error_message
                or "Unable to send the bill on WhatsApp. Please try again or use Print Bill."
            )

        delivery.status = "SENT"
        delivery.provider_message_id = result.provider_message_id
        delivery.sent_at = datetime.now(timezone.utc).replace(tzinfo=None)
        delivery.error_message = None
        AuditService.log(
            tenant_id=ctx.tenant_id,
            action="BILL_SENT_WHATSAPP",
            entity_type="BILL",
            entity_id=bill.id,
            new_data={
                "bill_number": bill.bill_number,
                "recipient": parsed["masked"],
                "delivery_id": delivery.id,
                "provider_message_id": result.provider_message_id,
            },
        )
        db.session.commit()

        return {
            "message": "Bill sent successfully on WhatsApp.",
            "delivery": WhatsappBillService.serialize_delivery(delivery),
            "bill": BillService.serialize(
                bill, include_items=True, whatsapp_delivery_status="SENT"
            ),
        }

    @staticmethod
    def serialize_delivery(row: BillDelivery):
        return {
            "id": row.id,
            "bill_id": row.bill_id,
            "delivery_method": row.delivery_method,
            "recipient_phone_masked": row.recipient_phone_masked,
            "status": row.status,
            "provider_message_id": row.provider_message_id,
            "error_message": row.error_message,
            "sent_at": row.sent_at.isoformat() if row.sent_at else None,
            "delivered_at": row.delivered_at.isoformat() if getattr(row, "delivered_at", None) else None,
            "read_at": row.read_at.isoformat() if getattr(row, "read_at", None) else None,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
