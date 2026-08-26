"""Generate delivery challan PDF bytes (BIZ-36)."""

from __future__ import annotations

import io
from decimal import Decimal

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.repositories.tenant_repository import TenantRepository


class DeliveryChallanPdfService:
    @staticmethod
    def build_pdf_bytes(challan) -> bytes:
        tenant = TenantRepository.get_by_id(challan.tenant_id)
        business = (tenant.business_name or tenant.name or "Business") if tenant else "Business"
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
        y -= 6
        line("DELIVERY CHALLAN", bold=True, size=13, gap=18)
        line(f"Challan No: {challan.challan_number}", bold=True)
        if challan.created_at:
            line(f"Date: {challan.created_at.strftime('%Y-%m-%d %H:%M')}", size=10, gap=14)
        line(f"Status: {challan.status}", size=10, gap=14)
        if challan.customer_name:
            line(f"Customer: {challan.customer_name}", size=10, gap=14)
        if challan.customer_phone:
            line(f"Mobile: {challan.customer_phone}", size=10, gap=14)
        if challan.delivery_address:
            line(f"Deliver to: {challan.delivery_address}", size=10, gap=14)
        if challan.vehicle_number:
            line(f"Vehicle: {challan.vehicle_number}", size=10, gap=14)
        if float(getattr(challan, "transport_charge", 0) or 0):
            line(
                f"Transport charge: {float(challan.transport_charge):.2f} (non-GST)",
                size=10,
                gap=14,
            )
        if challan.notes:
            line(f"Notes: {challan.notes}", size=10, gap=14)

        line("Items", bold=True, gap=14)
        line("----------------------------------------------", size=9, gap=12)
        for item in challan.items or []:
            qty = float(Decimal(item.quantity))
            uom = (item.uom or "pcs").upper()
            line(f"{item.item_name}", size=10, gap=12)
            price_part = ""
            if item.unit_price is not None:
                price_part = f" @ {float(Decimal(item.unit_price)):.2f}"
            line(f"  Qty {qty:g} {uom}{price_part}", size=9, gap=13)
        line("----------------------------------------------", size=9, gap=14)
        line("Goods received in good condition.", size=10, gap=16)
        line("Receiver signature: ____________________", size=10, gap=18)

        c.showPage()
        c.save()
        mem.seek(0)
        return mem.read()
