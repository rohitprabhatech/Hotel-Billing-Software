"""Generate bill PDF bytes from saved bill snapshots (no recalculation)."""

from __future__ import annotations

import io
from decimal import Decimal

from reportlab.lib.pagesizes import A4, A5
from reportlab.pdfgen import canvas

from app.constants.billing_format import TRAVEL, normalize_bill_format
from app.constants.payments import payment_method_label
from app.repositories.tenant_repository import TenantRepository


class BillPdfService:
    @staticmethod
    def _format_rupee(value) -> str:
        amount = float(value or 0)
        return f"Rs. {amount:,.2f}"

    @staticmethod
    def build_pdf_bytes(bill) -> bytes:
        tenant = TenantRepository.get_by_id(bill.tenant_id)
        business = (tenant.business_name or tenant.name or "Business") if tenant else "Business"
        business_type = getattr(tenant, "business_type", None) if tenant else None
        bill_format = (
            normalize_bill_format(getattr(tenant, "bill_format", None), business_type=business_type)
            if tenant
            else "standard"
        )
        is_travel = bill_format == TRAVEL
        is_tax_invoice = bool(
            tenant
            and not is_travel
            and (
                getattr(tenant, "gst_number", None)
                or business_type == "wholesale"
                or float(bill.gst_amount or 0) > 0
            )
        )
        page_size = A5 if is_travel else A4
        mem = io.BytesIO()
        c = canvas.Canvas(mem, pagesize=page_size)
        width, height = page_size
        margin_x = 36
        margin_top = height - 42
        y = margin_top
        content_width = width - (margin_x * 2)

        def line(text, *, bold=False, size=10, gap=14, x=None):
            nonlocal y
            if y < 72:
                c.showPage()
                y = margin_top
            c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
            c.drawString(x if x is not None else margin_x, y, str(text)[:120])
            y -= gap

        def rule(gap=10):
            nonlocal y
            c.line(margin_x, y, margin_x + content_width, y)
            y -= gap

        if is_travel:
            c.setLineWidth(1.5)
            c.rect(margin_x - 8, 28, content_width + 16, height - 56)
            c.setLineWidth(1)

        line(business, bold=True, size=16 if is_travel else 14, gap=18)
        if tenant:
            addr_parts = [
                p
                for p in [
                    tenant.address,
                    ", ".join([x for x in [tenant.city, tenant.state, tenant.pincode] if x]),
                ]
                if p
            ]
            for part in addr_parts:
                line(part, size=9, gap=12)
            contact_bits = [b for b in [tenant.phone, tenant.email] if b]
            if contact_bits:
                line(" | ".join(contact_bits), size=9, gap=12)
            if tenant.gst_number and not is_travel:
                line(f"GSTIN: {tenant.gst_number}", size=9, gap=12)
            if tenant.state and not is_travel:
                line(f"Place of supply: {tenant.state}", size=9, gap=12)

        y -= 4
        rule(14)
        if is_travel:
            line("TRAVEL BOOKING VOUCHER", bold=True, size=13, gap=16)
            c.setTitle(f"Travel Voucher {bill.bill_number}")
        elif is_tax_invoice:
            line("TAX INVOICE", bold=True, size=13, gap=16)
            c.setTitle("TAX INVOICE")
        else:
            c.setTitle(f"Bill {bill.bill_number}")
        rule(14)

        if is_travel:
            line(f"Voucher No: {bill.bill_number}", bold=True, size=11, gap=14)
            if bill.created_at:
                line(f"Date: {bill.created_at.strftime('%a, %d %b %Y, %I:%M %p')}", size=10, gap=14)
            line(f"Guest Name: {bill.customer_name or 'Walk-in'}", size=10, gap=14)
            if bill.customer_phone_e164:
                line(f"Mobile: {bill.customer_phone_e164}", size=10, gap=14)
            if bill.table_number:
                line(f"Reference: {bill.table_number}", size=10, gap=14)
            line(f"Booked By: {getattr(bill, 'created_by_name', None) or '-'}", size=10, gap=14)
            line(f"Payment: {payment_method_label(bill.payment_method)}", size=10, gap=16)
        else:
            line(f"Bill No: {bill.bill_number}", bold=True)
            if bill.created_at:
                line(f"Date: {bill.created_at.strftime('%Y-%m-%d %H:%M')}", size=10, gap=14)
            line(f"Bill to: {bill.customer_name or 'Walk-in'}", size=10, gap=14)
            if bill.customer_phone_e164:
                line(f"Mobile: {bill.customer_phone_e164}", size=10, gap=14)
            if bill.table_number:
                line(f"Reference: {bill.table_number}", size=10, gap=14)
            line(f"Payment: {payment_method_label(bill.payment_method)}", size=10, gap=18)

        section = "Package / Service Details" if is_travel else "Items"
        line(section, bold=True, gap=14)
        rule(12)
        for index, item in enumerate(bill.items or [], start=1):
            qty = float(Decimal(item.quantity))
            price = float(Decimal(item.unit_price))
            total = float(Decimal(item.total))
            gst_pct = float(Decimal(getattr(item, "gst_percentage", 0) or 0))
            prefix = f"{index}. " if is_travel else ""
            line(f"{prefix}{item.item_name}", size=10, gap=12)
            if is_travel:
                line(
                    f"   Pax {qty:g} x {BillPdfService._format_rupee(price)}  =  {BillPdfService._format_rupee(total)}",
                    size=9,
                    gap=13,
                )
            else:
                gst_bit = f"  GST {gst_pct:g}%" if gst_pct else ""
                line(
                    f"  Qty {qty:g} x {price:.2f}{gst_bit}  =  {total:.2f}",
                    size=9,
                    gap=13,
                )
            if getattr(item, "warranty_until", None):
                line(
                    f"  Warranty valid until: {item.warranty_until.isoformat()}",
                    size=8,
                    gap=12,
                )
        rule(14)
        line(f"Subtotal: {BillPdfService._format_rupee(bill.subtotal) if is_travel else f'{float(bill.subtotal):.2f}'}")
        if float(bill.discount or 0):
            line(f"Discount: {BillPdfService._format_rupee(bill.discount) if is_travel else f'{float(bill.discount):.2f}'}")
        if not is_travel:
            line(f"Taxable: {float(bill.taxable_amount):.2f}")
        line(f"CGST: {BillPdfService._format_rupee(bill.cgst_amount) if is_travel else f'{float(bill.cgst_amount):.2f}'}")
        line(f"SGST: {BillPdfService._format_rupee(bill.sgst_amount) if is_travel else f'{float(bill.sgst_amount):.2f}'}")
        if not is_travel:
            line(f"GST: {float(bill.gst_amount):.2f}")
        if float(getattr(bill, "service_charge", 0) or 0):
            line(f"Service charge: {float(bill.service_charge):.2f}")
        if float(getattr(bill, "transport_charge", 0) or 0):
            line(f"Transport: {float(bill.transport_charge):.2f}")
        if float(bill.round_off or 0):
            line(f"Round off: {BillPdfService._format_rupee(bill.round_off) if is_travel else f'{float(bill.round_off):.2f}'}")
        total_label = "TOTAL PAYABLE" if is_travel else "Grand Total"
        total_value = (
            BillPdfService._format_rupee(bill.grand_total)
            if is_travel
            else f"{float(bill.grand_total):.2f}"
        )
        line(f"{total_label}: {total_value}", bold=True, size=12, gap=18)

        if is_travel:
            if tenant and tenant.gst_number:
                line(f"GSTIN: {tenant.gst_number}", size=9, gap=12)
            line("Please carry this voucher during your journey.", size=9, gap=12)
            line("Guest Signature: ____________________", size=9, gap=18)
            line("Authorized Signatory: ____________________", size=9, gap=18)
            line(f"Thank you for choosing {business}", size=10, gap=12)
            line("Safe journey & happy travels!", size=10, gap=14)
        elif is_tax_invoice:
            line("This is a computer-generated tax invoice.", size=8, gap=12)
            line("Thank you for your purchase.", size=10, gap=14)
        else:
            line("Thank you for your purchase.", size=10, gap=14)

        c.showPage()
        c.save()
        mem.seek(0)
        return mem.read()
