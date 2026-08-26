"""Pluggable rule-based industry analyzers for AI assistant (BIZ-62).

Plugin pattern
--------------
Each analyzer is a callable registered with one or more module codes.
`run_industry_analyzers` only invokes analyzers whose modules are enabled
for the tenant. Analyzers must:

- Query only `tenant_id`-scoped data
- Return structured insights with `based_on` citations (no invented numbers)
- Stay deterministic (no LLM / external calls)

To add an industry insight: implement a function matching
`AnalyzerFn` and append an entry to `INDUSTRY_ANALYZERS`.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import func

from app.extensions import db
from app.models.serial_unit import STATUS_IN_STOCK, SerialUnit
from app.repositories.fb_report_repository import FbReportRepository
from app.repositories.party_ledger_repository import PartyLedgerRepository
from app.repositories.travel_agent_repository import TravelCommissionRepository
from app.services.module_service import ModuleService

AnalyzerFn = Callable[[str, datetime, datetime, str], dict[str, Any] | None]


def _money(value) -> str:
    return f"₹{float(value or 0):,.2f}"


def analyze_fb_channels(tenant_id: str, start: datetime, end: datetime, label: str):
    channels = FbReportRepository.channel_wise(tenant_id, start, end)
    tables = FbReportRepository.table_wise(tenant_id, start, end)
    wastage = FbReportRepository.wastage_summary(tenant_id, start, end)
    if not channels and not tables and not (wastage or {}).get("entry_count"):
        return {
            "module": "order_channels",
            "title": "F&B activity",
            "insufficient_data": True,
            "insights": [],
            "message": f"No channel/table/wastage activity recorded for {label}.",
        }

    insights = []
    if channels:
        top = channels[0]
        insights.append(
            {
                "type": "fb_channel_leader",
                "title": "Top order channel",
                "detail": (
                    f"{top['channel_label']} led channel sales for {label} with "
                    f"{_money(top['total_sales'])} across {top['bill_count']} bill(s)."
                ),
                "based_on": {
                    "channel": top["channel"],
                    "total_sales": top["total_sales"],
                    "bill_count": top["bill_count"],
                },
            }
        )
    if tables:
        top_table = tables[0]
        insights.append(
            {
                "type": "fb_table_leader",
                "title": "Busiest table",
                "detail": (
                    f"Table {top_table['table_code']} produced "
                    f"{_money(top_table['total_sales'])} from {top_table['bill_count']} "
                    f"bill(s) in {label}."
                ),
                "based_on": {
                    "table_code": top_table["table_code"],
                    "total_sales": top_table["total_sales"],
                    "bill_count": top_table["bill_count"],
                },
            }
        )
    entry_count = int((wastage or {}).get("entry_count") or 0)
    if entry_count > 0:
        insights.append(
            {
                "type": "fb_wastage",
                "title": "Wastage logged",
                "detail": (
                    f"{entry_count} wastage entr(y/ies) totaling quantity "
                    f"{(wastage or {}).get('total_quantity') or 0} during {label}."
                ),
                "based_on": {
                    "entry_count": entry_count,
                    "total_quantity": (wastage or {}).get("total_quantity"),
                },
            }
        )
    return {
        "module": "order_channels",
        "title": "F&B Insights",
        "insufficient_data": False,
        "insights": insights,
        "metrics": {
            "channel_count": len(channels),
            "table_count": len(tables),
            "wastage_entries": entry_count,
        },
    }


def analyze_serial_stock_aging(tenant_id: str, start: datetime, end: datetime, label: str):
    # Aging is a stock snapshot (not period-bound sales); start/end unused intentionally.
    _ = (start, end, label)
    from sqlalchemy import case

    now = datetime.utcnow()
    cutoff_90 = now - timedelta(days=90)
    agg = (
        db.session.query(
            func.count(SerialUnit.id),
            func.coalesce(
                func.sum(case((SerialUnit.received_at < cutoff_90, 1), else_=0)),
                0,
            ),
        )
        .filter(
            SerialUnit.tenant_id == tenant_id,
            SerialUnit.status == STATUS_IN_STOCK,
        )
        .one()
    )
    in_stock = int(agg[0] or 0)
    aged_90 = int(agg[1] or 0)
    if in_stock == 0:
        return {
            "module": "serial_imei",
            "title": "IMEI / Serial stock",
            "insufficient_data": True,
            "insights": [],
            "message": "No IN_STOCK serial units to analyze.",
        }
    insights = [
        {
            "type": "serial_stock_snapshot",
            "title": "In-stock serial units",
            "detail": f"{in_stock} serial unit(s) currently IN_STOCK.",
            "based_on": {"in_stock": in_stock},
        }
    ]
    if aged_90 > 0:
        insights.append(
            {
                "type": "serial_aging_90",
                "title": "Aging stock (90+ days)",
                "detail": (
                    f"{aged_90} of {in_stock} in-stock unit(s) were received more than "
                    "90 days ago — review for promotions or clearance."
                ),
                "based_on": {"aged_90_plus": aged_90, "in_stock": in_stock},
            }
        )
    return {
        "module": "serial_imei",
        "title": "IMEI / Serial Insights",
        "insufficient_data": False,
        "insights": insights,
        "metrics": {"in_stock": in_stock, "aged_90_plus": aged_90},
    }


def analyze_customer_credit(tenant_id: str, start: datetime, end: datetime, label: str):
    _ = (start, end, label)
    summary = PartyLedgerRepository.outstanding_summary(tenant_id)
    customer_amt = float(summary.get("outstanding_amount") or 0)
    supplier_amt = float(summary.get("supplier_outstanding_amount") or 0)
    customers = int(summary.get("customer_count") or 0)
    if customer_amt <= 0 and supplier_amt <= 0:
        return {
            "module": "customer_credit",
            "title": "Credit / Udhari",
            "insufficient_data": True,
            "insights": [],
            "message": "No outstanding customer or supplier balances.",
        }
    insights = []
    if customer_amt > 0:
        insights.append(
            {
                "type": "credit_customer_outstanding",
                "title": "Customer outstanding",
                "detail": (
                    f"{customers} customer(s) owe {_money(customer_amt)} in open credit."
                ),
                "based_on": {
                    "outstanding_amount": customer_amt,
                    "customer_count": customers,
                },
            }
        )
    if supplier_amt > 0:
        insights.append(
            {
                "type": "credit_supplier_outstanding",
                "title": "Supplier outstanding",
                "detail": f"Supplier dues total {_money(supplier_amt)}.",
                "based_on": {"supplier_outstanding_amount": supplier_amt},
            }
        )
    return {
        "module": "customer_credit",
        "title": "Credit Insights",
        "insufficient_data": False,
        "insights": insights,
        "metrics": summary,
    }


def analyze_travel_commission(tenant_id: str, start: datetime, end: datetime, label: str):
    _ = (start, end, label)
    rows = TravelCommissionRepository.report_by_agent(tenant_id)
    if not rows:
        return {
            "module": "travel_commission",
            "title": "Travel commission",
            "insufficient_data": True,
            "insights": [],
            "message": "No commission entries yet.",
        }
    pending = sum(float(row.get("pending_total") or 0) for row in rows)
    paid = sum(float(row.get("paid_total") or 0) for row in rows)
    top = max(rows, key=lambda row: float(row.get("commission_total") or 0))
    insights = [
        {
            "type": "travel_commission_pending",
            "title": "Pending commission",
            "detail": (
                f"Pending agent commission totals {_money(pending)}; "
                f"paid to date {_money(paid)}."
            ),
            "based_on": {"pending_total": pending, "paid_total": paid},
        },
        {
            "type": "travel_commission_leader",
            "title": "Top agent by commission",
            "detail": (
                f"{top['agent_code']} · {top['agent_name']} has "
                f"{_money(top['commission_total'])} accrued across "
                f"{top['entry_count']} booking(s)."
            ),
            "based_on": {
                "agent_id": top["agent_id"],
                "commission_total": float(top["commission_total"] or 0),
                "entry_count": top["entry_count"],
            },
        },
    ]
    return {
        "module": "travel_commission",
        "title": "Travel Commission Insights",
        "insufficient_data": False,
        "insights": insights,
        "metrics": {
            "agent_count": len(rows),
            "pending_total": pending,
            "paid_total": paid,
        },
    }


# module code(s) → analyzer. First matching enabled module wins per entry.
INDUSTRY_ANALYZERS: tuple[tuple[frozenset[str], AnalyzerFn], ...] = (
    (frozenset({"order_channels"}), analyze_fb_channels),
    (frozenset({"serial_imei"}), analyze_serial_stock_aging),
    (frozenset({"customer_credit"}), analyze_customer_credit),
    (frozenset({"travel_commission"}), analyze_travel_commission),
)


def run_industry_analyzers(
    tenant,
    *,
    start: datetime,
    end: datetime,
    label: str,
) -> list[dict[str, Any]]:
    enabled = set(ModuleService.enabled_codes_for_tenant(tenant))
    results: list[dict[str, Any]] = []
    for modules, analyzer in INDUSTRY_ANALYZERS:
        if not (modules & enabled):
            continue
        packet = analyzer(tenant.id, start, end, label)
        if packet is None:
            continue
        packet["modules"] = sorted(modules & enabled)
        results.append(packet)
    return results
