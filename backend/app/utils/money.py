"""Decimal money helpers and bill calculation."""

from decimal import ROUND_HALF_UP, Decimal


TWOPLACES = Decimal("0.01")
ZERO = Decimal("0.00")


def money(value) -> Decimal:
    return Decimal(str(value)).quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def qty(value) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)


def calculate_bill_totals(lines: list[dict], discount_amount, service_charge_amount=0) -> dict:
    """
    Line-level GST with proportional bill discount allocation.

    lines: [{item_id, item_name, quantity, unit_price, gst_percentage}]
    service_charge_amount: flat fee added after GST (before rupee rounding).
    """
    prepared = []
    subtotal = ZERO
    for line in lines:
        quantity = qty(line["quantity"])
        unit_price = money(line["unit_price"])
        gst_percentage = money(line["gst_percentage"])
        line_gross = money(unit_price * quantity)
        prepared.append(
            {
                **line,
                "quantity": quantity,
                "unit_price": unit_price,
                "gst_percentage": gst_percentage,
                "line_gross": line_gross,
            }
        )
        subtotal = money(subtotal + line_gross)

    discount = money(discount_amount or 0)
    if discount < ZERO:
        raise ValueError("Discount cannot be negative")
    if discount > subtotal:
        raise ValueError("Discount cannot exceed subtotal")

    allocated = ZERO
    result_lines = []
    for index, line in enumerate(prepared):
        if subtotal == ZERO:
            line_discount = ZERO
        elif index == len(prepared) - 1:
            line_discount = money(discount - allocated)
        else:
            share = line["line_gross"] / subtotal
            line_discount = money(discount * share)
            allocated = money(allocated + line_discount)

        line_taxable = money(line["line_gross"] - line_discount)
        half_rate = line["gst_percentage"] / Decimal("2")
        line_cgst = money(line_taxable * half_rate / Decimal("100"))
        line_sgst = money(line_taxable * half_rate / Decimal("100"))
        line_total = money(line_taxable + line_cgst + line_sgst)

        result_lines.append(
            {
                "item_id": line.get("item_id"),
                "variant_id": line.get("variant_id"),
                "serial_unit_id": line.get("serial_unit_id"),
                "serial_number": line.get("serial_number"),
                "item_name": line["item_name"],
                "quantity": line["quantity"],
                "unit_price": line["unit_price"],
                "gst_percentage": line["gst_percentage"],
                "discount": line_discount,
                "taxable_amount": line_taxable,
                "cgst_amount": line_cgst,
                "sgst_amount": line_sgst,
                "total": line_total,
            }
        )

    taxable_amount = money(sum((x["taxable_amount"] for x in result_lines), ZERO))
    cgst_amount = money(sum((x["cgst_amount"] for x in result_lines), ZERO))
    sgst_amount = money(sum((x["sgst_amount"] for x in result_lines), ZERO))
    gst_amount = money(cgst_amount + sgst_amount)
    service_charge = money(service_charge_amount or 0)
    if service_charge < ZERO:
        raise ValueError("Service charge cannot be negative")
    pre_round = money(taxable_amount + gst_amount + service_charge)
    grand_total = pre_round.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    round_off = money(grand_total - pre_round)

    return {
        "subtotal": subtotal,
        "discount": discount,
        "taxable_amount": taxable_amount,
        "cgst_amount": cgst_amount,
        "sgst_amount": sgst_amount,
        "gst_amount": gst_amount,
        "service_charge": service_charge,
        "round_off": round_off,
        "grand_total": money(grand_total),
        "lines": result_lines,
    }