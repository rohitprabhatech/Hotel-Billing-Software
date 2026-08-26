"""Delivery challan HTTP controller (BIZ-36)."""

from flask import Response, request

from app.schemas.challan_schemas import (
    convert_challan_schema,
    create_challan_schema,
    update_challan_status_schema,
)
from app.services.delivery_challan_pdf_service import DeliveryChallanPdfService
from app.services.delivery_challan_service import DeliveryChallanService
from app.utils.responses import success_response


def list_challans():
    data, meta = DeliveryChallanService.list_challans(
        status=request.args.get("status"),
        page=int(request.args.get("page", 1)),
        per_page=int(request.args.get("per_page", 100)),
    )
    return success_response(data=data, meta=meta)


def get_challan(challan_id: str):
    return success_response(data=DeliveryChallanService.get(challan_id))


def create_challan():
    payload = create_challan_schema.load(request.get_json() or {})
    data = DeliveryChallanService.create(
        items=payload["items"],
        customer_id=payload.get("customer_id"),
        customer_name=payload.get("customer_name"),
        customer_phone=payload.get("customer_phone"),
        delivery_address=payload.get("delivery_address"),
        vehicle_number=payload.get("vehicle_number"),
        notes=payload.get("notes"),
        quotation_id=payload.get("quotation_id"),
        transport_charge=payload.get("transport_charge") or 0,
    )
    return success_response(data=data, status_code=201)


def update_challan_status(challan_id: str):
    payload = update_challan_status_schema.load(request.get_json() or {})
    data = DeliveryChallanService.update_status(
        challan_id,
        status=payload["status"],
        notes=payload.get("notes"),
    )
    return success_response(data=data)


def convert_challan(challan_id: str):
    payload = convert_challan_schema.load(request.get_json() or {})
    data = DeliveryChallanService.convert_to_bill(
        challan_id, payment_method=payload.get("payment_method")
    )
    return success_response(data=data)


def download_challan_pdf(challan_id: str):
    challan = DeliveryChallanService.get_entity(challan_id)
    pdf = DeliveryChallanPdfService.build_pdf_bytes(challan)
    DeliveryChallanService.record_print(challan_id)
    return Response(
        pdf,
        mimetype="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{challan.challan_number}.pdf"'
        },
    )
