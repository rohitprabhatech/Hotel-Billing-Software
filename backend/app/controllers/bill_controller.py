"""Bill HTTP controller."""

from flask import request

from app.schemas.bill_schemas import (
    cancel_bill_schema,
    create_bill_schema,
    send_email_bill_schema,
)
from app.services.bill_service import BillService
from app.utils.responses import success_response


def create_bill():
    payload = create_bill_schema.load(request.get_json() or {})
    reference = payload.get("reference")
    if reference is None or reference == "":
        reference = payload.get("table_number")
    data = BillService.create_bill(
        items=payload["items"],
        discount=payload.get("discount", 0),
        reference=reference,
        payment_method=payload.get("payment_method"),
        customer_name=payload.get("customer_name"),
        customer_phone_country_code=payload.get("customer_phone_country_code"),
        customer_phone=payload.get("customer_phone"),
        customer_email=payload.get("customer_email"),
    )
    return success_response(data=data, status_code=201)


def list_bills():
    status = request.args.get("status")
    q = request.args.get("q")
    payment_method = request.args.get("payment_method")
    whatsapp_status = request.args.get("whatsapp_status")
    email_status = request.args.get("email_status")
    today_only = str(request.args.get("today", "")).lower() in {"1", "true", "yes"}
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    data, meta = BillService.list_bills(
        status=status,
        page=page,
        per_page=per_page,
        today_only=today_only,
        q=q,
        payment_method=payment_method,
        whatsapp_status=whatsapp_status,
        email_status=email_status,
    )
    return success_response(data=data, meta=meta)


def get_bill(bill_id: str):
    return success_response(data=BillService.get_bill(bill_id))


def today_summary():
    return success_response(data=BillService.today_summary())


def cancel_bill(bill_id: str):
    payload = cancel_bill_schema.load(request.get_json() or {})
    data = BillService.cancel_bill(bill_id, payload["reason"])
    return success_response(data=data)


def print_bill(bill_id: str):
    data = BillService.record_print(bill_id)
    return success_response(data=data)


def download_bill_pdf(bill_id: str):
    from flask import Response

    from app.repositories.bill_repository import BillRepository
    from app.services.bill_pdf_service import BillPdfService
    from app.utils.exceptions import NotFoundError
    from app.utils.request_context import require_request_context

    ctx = require_request_context()
    bill = BillRepository.get_by_id_and_tenant(bill_id, ctx.tenant_id)
    if bill is None:
        raise NotFoundError("Bill not found")
    pdf = BillPdfService.build_pdf_bytes(bill)
    filename = f"{bill.bill_number}.pdf".replace('"', "")
    return Response(
        pdf,
        mimetype="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def send_bill_email(bill_id: str):
    from app.services.email_bill_service import EmailBillService

    payload = send_email_bill_schema.load(request.get_json() or {})
    data = EmailBillService.send_bill(
        bill_id,
        email=payload.get("email"),
        customer_name=payload.get("customer_name"),
    )
    return success_response(data=data)