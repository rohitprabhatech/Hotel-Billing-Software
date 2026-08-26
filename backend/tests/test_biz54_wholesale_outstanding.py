"""Sprint BIZ-54 — wholesale aged outstanding, challan alias, GST invoice."""

from datetime import datetime, timedelta
from decimal import Decimal

from app.extensions import db
from app.models.party_ledger_entry import ENTRY_CREDIT_SALE, PartyLedgerEntry
from tests.conftest import login


def _switch(client, headers, business_type):
    response = client.put(
        "/api/v1/tenants/me",
        headers=headers,
        json={"business_type": business_type},
    )
    assert response.status_code == 200, response.get_json()


def _category(client, headers, name="Trade"):
    response = client.post("/api/v1/categories", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]["id"]


def _item(client, headers, category_id, name="Carton", **overrides):
    payload = {
        "name": name,
        "category_id": category_id,
        "price": "100",
        "gst_percentage": "18",
        "stock_quantity": "200",
        "uom": "pcs",
    }
    payload.update(overrides)
    response = client.post("/api/v1/items", headers=headers, json=payload)
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _customer(client, headers, name="Dealer"):
    response = client.post(
        "/api/v1/customers",
        headers=headers,
        json={"name": name, "phone_country_code": "+91", "phone": "9876501234"},
    )
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def _supplier(client, headers, name="Mill"):
    response = client.post("/api/v1/suppliers", headers=headers, json={"name": name})
    assert response.status_code == 201, response.get_json()
    return response.get_json()["data"]


def test_aged_outstanding_buckets_customer_and_supplier(client, app):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "wholesale")
    cat_id = _category(client, owner)
    item = _item(client, owner, cat_id, gst_percentage="0")
    customer = _customer(client, owner)
    supplier = _supplier(client, owner)

    # Fresh credit sale → 0–30 bucket
    fresh = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "items": [{"item_id": item["id"], "quantity": "2"}],
            "payment_method": "credit",
            "customer_id": customer["id"],
        },
    )
    assert fresh.status_code == 201, fresh.get_json()
    assert Decimal(str(fresh.get_json()["data"]["grand_total"])) == Decimal("200")

    # Older credit sale backdated → 61–90
    older = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "items": [{"item_id": item["id"], "quantity": "1"}],
            "payment_method": "credit",
            "customer_id": customer["id"],
        },
    )
    assert older.status_code == 201, older.get_json()
    older_bill_id = older.get_json()["data"]["id"]

    with app.app_context():
        entry = (
            db.session.query(PartyLedgerEntry)
            .filter_by(
                reference_id=older_bill_id,
                entry_type=ENTRY_CREDIT_SALE,
            )
            .one()
        )
        entry.created_at = datetime.utcnow() - timedelta(days=70)
        db.session.commit()

    purchase = client.post(
        "/api/v1/purchases",
        headers=owner,
        json={
            "supplier_id": supplier["id"],
            "payment_method": "credit",
            "items": [{"item_id": item["id"], "quantity": "3", "unit_cost": "50"}],
        },
    )
    assert purchase.status_code == 201, purchase.get_json()

    report = client.get("/api/v1/reports/outstanding", headers=owner)
    assert report.status_code == 200, report.get_json()
    data = report.get_json()["data"]
    assert "0_30" in data["buckets"]
    assert "90_plus" in data["buckets"]

    cust = next(p for p in data["customers"]["parties"] if p["id"] == customer["id"])
    assert Decimal(str(cust["aging"]["0_30"])) == Decimal("200")
    assert Decimal(str(cust["aging"]["61_90"])) == Decimal("100")
    assert Decimal(str(cust["aging"]["total"])) == Decimal("300")
    assert Decimal(str(cust["balance"])) == Decimal("300")

    assert Decimal(str(data["customers"]["summary"]["total"])) >= Decimal("300")

    supp = next(p for p in data["suppliers"]["parties"] if p["id"] == supplier["id"])
    assert Decimal(str(supp["aging"]["0_30"])) == Decimal("150")
    assert Decimal(str(supp["balance"])) == Decimal("150")


def test_fifo_payment_reduces_oldest_bucket(client, app):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "wholesale")
    cat_id = _category(client, owner)
    item = _item(client, owner, cat_id, price="100", gst_percentage="0")
    customer = _customer(client, owner, name="FIFO Dealer")

    old_bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "items": [{"item_id": item["id"], "quantity": "1"}],
            "payment_method": "credit",
            "customer_id": customer["id"],
        },
    ).get_json()["data"]
    new_bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "items": [{"item_id": item["id"], "quantity": "1"}],
            "payment_method": "credit",
            "customer_id": customer["id"],
        },
    ).get_json()["data"]

    with app.app_context():
        entry = (
            db.session.query(PartyLedgerEntry)
            .filter_by(reference_id=old_bill["id"], entry_type=ENTRY_CREDIT_SALE)
            .one()
        )
        entry.created_at = datetime.utcnow() - timedelta(days=45)
        db.session.commit()

    paid = client.post(
        f"/api/v1/customers/{customer['id']}/payments",
        headers=owner,
        json={"amount": "60", "collection_method": "cash"},
    )
    assert paid.status_code == 201, paid.get_json()

    report = client.get(
        "/api/v1/wholesale/reports/outstanding",
        headers=owner,
        query_string={"party_type": "customer"},
    )
    assert report.status_code == 200, report.get_json()
    cust = next(
        p
        for p in report.get_json()["data"]["customers"]["parties"]
        if p["id"] == customer["id"]
    )
    # 60 applied to oldest (45-day) charge of 100 → 40 left in 31–60; new 100 in 0–30
    assert Decimal(str(cust["aging"]["31_60"])) == Decimal("40")
    assert Decimal(str(cust["aging"]["0_30"])) == Decimal("100")
    assert Decimal(str(cust["aging"]["total"])) == Decimal("140")
    assert report.get_json()["data"]["suppliers"]["parties"] == []


def test_wholesale_challan_alias_and_tax_invoice_pdf(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "wholesale")
    cat_id = _category(client, owner)
    item = _item(client, owner, cat_id, price="200", gst_percentage="18")

    challan = client.post(
        "/api/v1/wholesale/challans",
        headers=owner,
        json={
            "customer_name": "Retailer",
            "items": [{"item_id": item["id"], "quantity": "2"}],
        },
    )
    assert challan.status_code == 201, challan.get_json()
    challan_id = challan.get_json()["data"]["id"]

    listed = client.get("/api/v1/wholesale/challans", headers=owner)
    assert listed.status_code == 200, listed.get_json()
    assert any(row["id"] == challan_id for row in listed.get_json()["data"])

    pdf = client.get(f"/api/v1/wholesale/challans/{challan_id}/pdf", headers=owner)
    assert pdf.status_code == 200, pdf.data[:80]
    assert pdf.headers.get("Content-Type", "").startswith("application/pdf")

    bill = client.post(
        "/api/v1/bills",
        headers=billing,
        json={
            "items": [{"item_id": item["id"], "quantity": "1"}],
            "payment_method": "cash",
            "customer_name": "GST Buyer",
        },
    )
    assert bill.status_code == 201, bill.get_json()
    bill_id = bill.get_json()["data"]["id"]
    assert Decimal(str(bill.get_json()["data"]["gst_amount"])) > 0

    invoice = client.get(f"/api/v1/bills/{bill_id}/pdf", headers=billing)
    assert invoice.status_code == 200
    assert invoice.headers.get("Content-Type", "").startswith("application/pdf")
    # Title metadata is stored uncompressed in the PDF Info dict
    assert b"TAX INVOICE" in invoice.data


def test_billing_user_cannot_access_outstanding_report(client):
    owner = login(client, "owner@hotela.com", "Owner@12345")
    billing = login(client, "billing@hotela.com", "Billing@12345")
    _switch(client, owner, "wholesale")
    denied = client.get("/api/v1/reports/outstanding", headers=billing)
    assert denied.status_code in (403, 401)
