"""Generate bill PDF bytes from saved bill snapshots (no recalculation)."""

from __future__ import annotations

import io
from decimal import Decimal

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.constants.payments import payment_method_label
from app.repositories.tenant_repository import TenantRepository


class BillPdfService:
    @staticmethod
    def build_pdf_bytes(bill) -> bytes:
        tenant = TenantRepository.get_by_id(bill.tenant_id)
        business = (tenant.business_name or tenant.name or "Business") if tenant else "Business"
        business_type = getattr(tenant, "business_type", None) if tenant else None
        is_tax_invoice = bool(
            tenant
            and (
                getattr(tenant, "gst_number", None)
                or business_type == "wholesale"
                or float(bill.gst_amount or 0) > 0
            )
        )
        mem = io.BytesIO()
        c = canvas.Canvas(mem, pagesize=A4)
        width, height = A4
        y = height - 48

        def line(text, *, bold=False, size=11, gap=16):
            nonlocal y
            if y < 56:
                c.showPage()
                y = height - 48
                c.setFont("Helvetica", 11)
            c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
            c.drawString(40, y, str(text)[:110])
            y -= gap

        line(business, bold=True, size=14, gap=18)
        if tenant:
            addr_parts = [
                p
                for p in [
                    tenant.address,
                    ", ".join([x for x in [tenant.city, tenant.state] if x]),
                    tenant.pincode,
                ]
                if p
            ]
            for part in addr_parts:
                line(part, size=9, gap=12)
            if tenant.phone:
                line(f"Phone: {tenant.phone}", size=9, gap=12)
            if tenant.gst_number:
                line(f"GSTIN: {tenant.gst_number}", size=9, gap=12)
            if tenant.state:
                line(f"Place of supply: {tenant.state}", size=9, gap=12)
        y -= 6
        if is_tax_invoice:
            line("TAX INVOICE", bold=True, size=13, gap=16)
            c.setTitle("TAX INVOICE")
        else:
            c.setTitle(f"Bill {bill.bill_number}")
        line(f"Bill No: {bill.bill_number}", bold=True)
        if bill.created_at:
            line(f"Date: {bill.created_at.strftime('%Y-%m-%d %H:%M')}", size=10, gap=14)
        line(f"Bill to: {bill.customer_name or 'Walk-in'}", size=10, gap=14)
        if bill.customer_phone_e164:
            line(f"Mobile: {bill.customer_phone_e164}", size=10, gap=14)
        if bill.table_number:
            line(f"Reference: {bill.table_number}", size=10, gap=14)
        line(f"Payment: {payment_method_label(bill.payment_method)}", size=10, gap=18)

        line("Items", bold=True, gap=14)
        line("----------------------------------------------", size=9, gap=12)
        for item in bill.items or []:
            qty = float(Decimal(item.quantity))
            price = float(Decimal(item.unit_price))
            total = float(Decimal(item.total))
            gst_pct = float(Decimal(getattr(item, "gst_percentage", 0) or 0))
            line(f"{item.item_name}", size=10, gap=12)
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
        line("----------------------------------------------", size=9, gap=14)
        line(f"Subtotal: {float(bill.subtotal):.2f}")
        line(f"Discount: {float(bill.discount):.2f}")
        line(f"Taxable: {float(bill.taxable_amount):.2f}")
        line(f"CGST: {float(bill.cgst_amount):.2f}")
        line(f"SGST: {float(bill.sgst_amount):.2f}")
        line(f"GST: {float(bill.gst_amount):.2f}")
        if float(getattr(bill, "service_charge", 0) or 0):
            line(f"Service charge: {float(bill.service_charge):.2f}")
        if float(getattr(bill, "transport_charge", 0) or 0):
            line(f"Transport: {float(bill.transport_charge):.2f}")
        if float(bill.round_off or 0):
            line(f"Round off: {float(bill.round_off):.2f}")
        line(f"Grand Total: {float(bill.grand_total):.2f}", bold=True, size=12, gap=18)
        if is_tax_invoice:
            line("This is a computer-generated tax invoice.", size=8, gap=12)
        line("Thank you for your purchase.", size=10, gap=14)

        c.showPage()
        c.save()
        mem.seek(0)
        return mem.read()
