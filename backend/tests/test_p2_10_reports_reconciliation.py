"""P2-10: reconcile report/dashboard totals against manual sample bills."""

from app.utils.money import calculate_bill_totals
from tests.conftest import login, login_master


def _manual_grand(unit_price, qty, gst_percentage, discount=0, payment_method="cash"):
    """Mirror server bill math for one line (payment unused; for documentation)."""
    result = calculate_bill_totals(
        [
            {
                "item_id": "x",
                "item_name": "sample",
                "quantity": qty,
                "unit_price": unit_price,
                "gst_percentage": gst_percentage,
            }
        ],
        discount,
    )
    return result


def _register_owner(client, app, suffix: str):
    email = f"p210-{suffix}@reconcile.test"
    response = client.post(
        "/api/v1/auth/register-business",
        json={
            "business_name": f"Reconcile Shop {suffix}",
            "business_type": "grocery_kirana",
            "mobile": "9000000010",
            "owner_name": "Reconcile Owner",
            "owner_email": email,
            "password": "Reconcile@12345",
            "confirm_password": "Reconcile@12345",
            "terms_accepted": True,
        },
    )
    assert response.status_code == 201, response.get_json()
    master = login_master(client, app)
    request_id = response.get_json()["data"]["request_id"]
    approved = client.post(
        f"/api/v1/master/registration-requests/{request_id}/approve",
        headers=master,
    )
    assert approved.status_code == 200, approved.get_json()
    return login(client, email, "Reconcile@12345")


def test_summary_today_week_month_match_manual_sample_bills(client, app):
    """Isolated tenant: two finalized bills + one cancelled; metrics must match hand calc."""
    owner = _register_owner(client, app, "a")

    category_id = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Grocery"},
    ).get_json()["data"]["id"]

    rice = client.post(
        "/api/v1/items",
        headers=owner,
        json={
            "name": "Rice 1kg",
            "category_id": category_id,
            "price": 100,
            "gst_percentage": 5,
        },
    ).get_json()["data"]
    oil = client.post(
        "/api/v1/items",
        headers=owner,
        json={
            "name": "Oil 1L",
            "category_id": category_id,
            "price": 200,
            "gst_percentage": 5,
        },
    ).get_json()["data"]

    # Bill A — cash: Rice × 2, no discount
    # Manual: subtotal 200, GST 5% → 210.00 (no round-off)
    calc_a = _manual_grand(100, 2, 5, discount=0)
    bill_a = client.post(
        "/api/v1/bills",
        headers=owner,
        json={
            "payment_method": "cash",
            "discount": 0,
            "items": [{"item_id": rice["id"], "quantity": 2}],
        },
    ).get_json()["data"]
    assert bill_a["grand_total"] == float(calc_a["grand_total"])
    assert bill_a["payment_method"] == "cash"

    # Bill B — online: Oil × 1, discount 10
    # Manual: subtotal 200, discount 10, taxable 190, GST 9.50 → 199.50 → round ₹200
    calc_b = _manual_grand(200, 1, 5, discount=10)
    bill_b = client.post(
        "/api/v1/bills",
        headers=owner,
        json={
            "payment_method": "online",
            "discount": 10,
            "items": [{"item_id": oil["id"], "quantity": 1}],
        },
    ).get_json()["data"]
    assert bill_b["grand_total"] == float(calc_b["grand_total"])
    assert bill_b["payment_method"] == "online"

    # Bill C — cash then cancelled (must NOT count in total_sales)
    bill_c = client.post(
        "/api/v1/bills",
        headers=owner,
        json={
            "payment_method": "cash",
            "items": [{"item_id": rice["id"], "quantity": 1}],
        },
    ).get_json()["data"]
    assert (
        client.post(
            f"/api/v1/bills/{bill_c['id']}/cancel",
            headers=owner,
            json={"reason": "Wrong entry for reconciliation"},
        ).status_code
        == 200
    )

    expected_sales = float(calc_a["grand_total"] + calc_b["grand_total"])
    expected_cash = float(calc_a["grand_total"])
    expected_online = float(calc_b["grand_total"])
    expected_bills = 2
    expected_cancelled = 1
    expected_avg = round(expected_sales / expected_bills, 2)

    for period in ("today", "this_week", "this_month"):
        response = client.get(
            "/api/v1/reports/summary",
            headers=owner,
            query_string={"period": period},
        )
        assert response.status_code == 200, response.get_json()
        current = response.get_json()["data"]["current"]

        assert current["bill_count"] == expected_bills, period
        assert current["total_sales"] == expected_sales, period
        assert current["cash_sales"] == expected_cash, period
        assert current["online_sales"] == expected_online, period
        assert current["cash_bill_count"] == 1, period
        assert current["online_bill_count"] == 1, period
        assert current["cancelled_bills"] == expected_cancelled, period
        assert current["average_bill"] == expected_avg, period

    # Dashboard uses the same summary endpoint (OwnerDashboardPage).
    weekly = client.get("/api/v1/reports/weekly-sales", headers=owner).get_json()["data"]
    assert weekly["metrics"]["total_sales"] == expected_sales
    assert weekly["metrics"]["bill_count"] == expected_bills


def test_billing_home_today_summary_matches_finalized_only(client, app):
    """Billing home KPI path (/bills/today-summary) agrees with report today sales."""
    owner = _register_owner(client, app, "b")
    category_id = client.post(
        "/api/v1/categories",
        headers=owner,
        json={"name": "Counter"},
    ).get_json()["data"]["id"]
    item = client.post(
        "/api/v1/items",
        headers=owner,
        json={
            "name": "Packet Salt",
            "category_id": category_id,
            "price": 50,
            "gst_percentage": 0,
        },
    ).get_json()["data"]

    calc = _manual_grand(50, 3, 0, discount=0)
    bill = client.post(
        "/api/v1/bills",
        headers=owner,
        json={
            "payment_method": "cash",
            "items": [{"item_id": item["id"], "quantity": 3}],
        },
    ).get_json()["data"]
    assert bill["grand_total"] == float(calc["grand_total"])

    summary = client.get(
        "/api/v1/reports/summary",
        headers=owner,
        query_string={"period": "today"},
    ).get_json()["data"]["current"]
    today = client.get("/api/v1/bills/today-summary", headers=owner).get_json()["data"]

    assert summary["total_sales"] == float(calc["grand_total"])
    assert today["total_sales"] == summary["total_sales"]
    assert today["bill_count"] == summary["bill_count"] == 1
