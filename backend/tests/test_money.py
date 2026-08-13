"""Bill calculation unit tests."""

from decimal import Decimal

from app.utils.money import calculate_bill_totals


def test_line_level_gst_and_discount():
    result = calculate_bill_totals(
        [
            {
                "item_id": "1",
                "item_name": "Chicken Thali",
                "quantity": 1,
                "unit_price": 420,
                "gst_percentage": 5,
            },
            {
                "item_id": "2",
                "item_name": "Tea",
                "quantity": 2,
                "unit_price": 30,
                "gst_percentage": 5,
            },
        ],
        discount_amount=20,
    )
    assert result["subtotal"] == Decimal("480.00")
    assert result["discount"] == Decimal("20.00")
    assert result["taxable_amount"] == Decimal("460.00")
    assert result["cgst_amount"] == Decimal("11.50")
    assert result["sgst_amount"] == Decimal("11.50")
    assert result["gst_amount"] == Decimal("23.00")
    # 483.00 rounds to 483
    assert result["grand_total"] == Decimal("483.00")


def test_discount_cannot_exceed_subtotal():
    try:
        calculate_bill_totals(
            [
                {
                    "item_id": "1",
                    "item_name": "Tea",
                    "quantity": 1,
                    "unit_price": 30,
                    "gst_percentage": 5,
                }
            ],
            discount_amount=100,
        )
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert "exceed" in str(exc).lower()
