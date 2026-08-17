"""Tenant-scoped business analysis and decision support from real sales only."""

from flask import current_app

from app.models.role import ROLE_OWNER
from app.repositories.report_repository import ReportRepository
from app.repositories.tenant_repository import TenantRepository
from app.utils.exceptions import ForbiddenError, ValidationError
from app.utils.periods import resolve_period
from app.utils.request_context import require_request_context

ALLOWED_PERIODS = frozenset(
    {"today", "yesterday", "this_week", "this_month", "last_month", "custom"}
)
TOP_N = 5


def _money(value) -> str:
    return f"₹{float(value or 0):,.2f}"


def _pct(part, whole) -> float | None:
    whole = float(whole or 0)
    if whole <= 0:
        return None
    return round(100.0 * float(part or 0) / whole, 1)


def _delta_pct(current, previous) -> float | None:
    previous = float(previous or 0)
    if previous == 0:
        return None
    return round(100.0 * (float(current or 0) - previous) / previous, 1)


class AiAssistantService:
    @staticmethod
    def _ensure_owner():
        ctx = require_request_context()
        if ctx.role != ROLE_OWNER:
            raise ForbiddenError("Only business owners can access the AI assistant")
        return ctx

    @staticmethod
    def _tz():
        return current_app.config.get("REPORT_TIMEZONE", "Asia/Kolkata")

    @staticmethod
    def _bounds(period: str, from_date=None, to_date=None):
        period = (period or "today").lower()
        if period not in ALLOWED_PERIODS:
            raise ValidationError(
                "period must be today, yesterday, this_week, this_month, last_month, or custom"
            )
        try:
            return resolve_period(period, AiAssistantService._tz(), from_date, to_date)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc

    @staticmethod
    def _empty_decisions(*, message: str):
        return {
            "insufficient_data": True,
            "message": message,
            "best_movers": [],
            "slow_movers": [],
            "demand_hints": [],
            "demand_insufficient": True,
            "recommendations": [],
            "outlook": {
                "available": False,
                "detail": None,
                "based_on": None,
            },
        }

    @staticmethod
    def analyze(period: str = "today", from_date=None, to_date=None):
        """
        Build an analysis + decision packet from tenant sales only.
        Never invents metrics — every insight/recommendation cites computed values.
        """
        ctx = AiAssistantService._ensure_owner()
        start, end, label, prev_start, prev_end, prev_label = AiAssistantService._bounds(
            period, from_date, to_date
        )

        metrics = ReportRepository.period_metrics(ctx.tenant_id, start, end)
        previous = ReportRepository.period_metrics(ctx.tenant_id, prev_start, prev_end)
        item_wise = ReportRepository.item_wise(ctx.tenant_id, start, end)
        previous_items = ReportRepository.item_wise(
            ctx.tenant_id, prev_start, prev_end
        )
        category_wise = ReportRepository.category_wise(ctx.tenant_id, start, end)
        day_wise = ReportRepository.day_wise(ctx.tenant_id, start, end)

        tenant = TenantRepository.get_by_id(ctx.tenant_id)
        business_name = (
            (tenant.business_name if tenant else None) or "Your business"
        ).strip()

        period_key = (period or "today").lower()
        has_sales = int(metrics.get("bill_count") or 0) > 0
        if not has_sales:
            message = (
                f"Not enough sales data for {label} to produce an analysis. "
                "Generate finalized bills in this period, then try again."
            )
            return {
                "insufficient_data": True,
                "message": message,
                "period": period_key,
                "label": label,
                "previous_label": prev_label,
                "business_name": business_name,
                "metrics": metrics,
                "previous_metrics": previous,
                "payment_mix": {
                    "cash_sales": metrics["cash_sales"],
                    "online_sales": metrics["online_sales"],
                    "cash_share_pct": None,
                    "online_share_pct": None,
                },
                "top_items": [],
                "low_items": [],
                "category_sales": [],
                "day_wise": day_wise,
                "insights": [],
                "summary": (
                    f"No finalized bills were found for {business_name} during {label}."
                ),
                "decisions": AiAssistantService._empty_decisions(
                    message=(
                        f"Not enough sales history for {label} to produce recommendations. "
                        "Decision support needs finalized bills in this period."
                    )
                ),
                "data_source": "tenant_sales_reports",
            }

        top_items = item_wise[:TOP_N]
        low_items = sorted(
            item_wise, key=lambda row: (row["revenue"], row["quantity"])
        )[:TOP_N]

        cash_share = _pct(metrics["cash_sales"], metrics["total_sales"])
        online_share = _pct(metrics["online_sales"], metrics["total_sales"])
        sales_delta = _delta_pct(metrics["total_sales"], previous["total_sales"])
        bills_delta = _delta_pct(metrics["bill_count"], previous["bill_count"])

        insights = AiAssistantService._build_insights(
            label=label,
            prev_label=prev_label,
            metrics=metrics,
            previous=previous,
            top_items=top_items,
            low_items=low_items,
            category_wise=category_wise,
            day_wise=day_wise,
            cash_share=cash_share,
            online_share=online_share,
            sales_delta=sales_delta,
            bills_delta=bills_delta,
        )
        decisions = AiAssistantService._build_decisions(
            label=label,
            prev_label=prev_label,
            metrics=metrics,
            previous=previous,
            item_wise=item_wise,
            previous_items=previous_items,
            category_wise=category_wise,
            day_wise=day_wise,
            cash_share=cash_share,
            online_share=online_share,
            sales_delta=sales_delta,
        )

        summary_parts = [
            f"{business_name} recorded {_money(metrics['total_sales'])} across "
            f"{int(metrics['bill_count'])} finalized bill(s) for {label}."
        ]
        if cash_share is not None:
            summary_parts.append(
                f"Payment mix: Cash {cash_share}% · Online {online_share or 0}%."
            )
        if top_items:
            summary_parts.append(
                f"Top item by revenue: {top_items[0]['item_name']} "
                f"({_money(top_items[0]['revenue'])})."
            )
        if sales_delta is not None:
            direction = "up" if sales_delta >= 0 else "down"
            summary_parts.append(
                f"Sales are {direction} {abs(sales_delta)}% vs {prev_label}."
            )

        return {
            "insufficient_data": False,
            "message": None,
            "period": period_key,
            "label": label,
            "previous_label": prev_label,
            "business_name": business_name,
            "metrics": metrics,
            "previous_metrics": previous,
            "payment_mix": {
                "cash_sales": metrics["cash_sales"],
                "online_sales": metrics["online_sales"],
                "cash_share_pct": cash_share,
                "online_share_pct": online_share,
            },
            "top_items": top_items,
            "low_items": low_items,
            "category_sales": category_wise,
            "day_wise": day_wise,
            "insights": insights,
            "summary": " ".join(summary_parts),
            "decisions": decisions,
            "data_source": "tenant_sales_reports",
        }

    @staticmethod
    def decisions(period: str = "today", from_date=None, to_date=None):
        """Decision-support slice (same tenant data as analyze)."""
        packet = AiAssistantService.analyze(period, from_date, to_date)
        return {
            "insufficient_data": packet["insufficient_data"],
            "message": packet["message"]
            if packet["insufficient_data"]
            else packet["decisions"].get("message"),
            "period": packet["period"],
            "label": packet["label"],
            "previous_label": packet["previous_label"],
            "business_name": packet["business_name"],
            "metrics": packet["metrics"],
            "previous_metrics": packet["previous_metrics"],
            "decisions": packet["decisions"],
            "data_source": packet["data_source"],
        }

    @staticmethod
    def _build_decisions(
        *,
        label,
        prev_label,
        metrics,
        previous,
        item_wise,
        previous_items,
        category_wise,
        day_wise,
        cash_share,
        online_share,
        sales_delta,
    ):
        by_qty_desc = sorted(
            item_wise, key=lambda row: (row["quantity"], row["revenue"]), reverse=True
        )
        by_qty_asc = sorted(
            item_wise, key=lambda row: (row["quantity"], row["revenue"])
        )
        best_movers = [
            {
                "item_name": row["item_name"],
                "quantity": row["quantity"],
                "revenue": row["revenue"],
                "rank_by": "quantity",
            }
            for row in by_qty_desc[:TOP_N]
        ]
        slow_movers = [
            {
                "item_name": row["item_name"],
                "quantity": row["quantity"],
                "revenue": row["revenue"],
                "rank_by": "quantity",
            }
            for row in by_qty_asc[:TOP_N]
        ]

        prev_bills = int(previous.get("bill_count") or 0)
        demand_insufficient = prev_bills == 0
        demand_hints = []
        if not demand_insufficient:
            prev_map = {row["item_name"]: row for row in previous_items}
            for row in item_wise:
                prior = prev_map.get(row["item_name"])
                if prior is None:
                    continue
                qty_change = float(row["quantity"]) - float(prior["quantity"])
                if qty_change == 0:
                    continue
                revenue_change = float(row["revenue"]) - float(prior["revenue"])
                demand_hints.append(
                    {
                        "item_name": row["item_name"],
                        "quantity": row["quantity"],
                        "previous_quantity": prior["quantity"],
                        "quantity_change": qty_change,
                        "revenue": row["revenue"],
                        "previous_revenue": prior["revenue"],
                        "revenue_change": revenue_change,
                        "direction": "up" if qty_change > 0 else "down",
                    }
                )
            demand_hints.sort(key=lambda row: abs(row["quantity_change"]), reverse=True)
            demand_hints = demand_hints[:TOP_N]

        outlook = AiAssistantService._build_outlook(
            label=label,
            prev_label=prev_label,
            metrics=metrics,
            previous=previous,
            day_wise=day_wise,
            sales_delta=sales_delta,
        )

        recommendations = AiAssistantService._build_recommendations(
            label=label,
            prev_label=prev_label,
            metrics=metrics,
            best_movers=best_movers,
            slow_movers=slow_movers,
            demand_hints=demand_hints,
            demand_insufficient=demand_insufficient,
            category_wise=category_wise,
            cash_share=cash_share,
            online_share=online_share,
            sales_delta=sales_delta,
            outlook=outlook,
        )

        return {
            "insufficient_data": False,
            "message": None,
            "best_movers": best_movers,
            "slow_movers": slow_movers,
            "demand_hints": demand_hints,
            "demand_insufficient": demand_insufficient,
            "demand_message": (
                f"No finalized sales in {prev_label} — demand change hints need a prior period."
                if demand_insufficient
                else None
            ),
            "recommendations": recommendations,
            "outlook": outlook,
        }

    @staticmethod
    def _build_outlook(*, label, prev_label, metrics, previous, day_wise, sales_delta):
        if sales_delta is not None:
            direction = "higher" if sales_delta >= 0 else "lower"
            return {
                "available": True,
                "detail": (
                    f"Observed trend: sales are {direction} by {abs(sales_delta)}% "
                    f"vs {prev_label} "
                    f"({_money(previous['total_sales'])} → {_money(metrics['total_sales'])}). "
                    "This cites recorded totals only — not a predictive model."
                ),
                "based_on": {
                    "current_sales": metrics["total_sales"],
                    "previous_sales": previous["total_sales"],
                    "delta_pct": sales_delta,
                    "current_label": label,
                    "previous_label": prev_label,
                },
            }

        if len(day_wise) >= 2:
            days = len(day_wise)
            avg_daily = float(metrics["total_sales"]) / days
            return {
                "available": True,
                "detail": (
                    f"Observed daily average for {label}: {_money(avg_daily)} "
                    f"across {days} day(s) with sales. "
                    "Not a forecast — only the recorded average."
                ),
                "based_on": {
                    "average_daily_sales": round(avg_daily, 2),
                    "days_with_sales": days,
                    "total_sales": metrics["total_sales"],
                    "label": label,
                },
            }

        return {
            "available": False,
            "detail": (
                f"Not enough history to describe a trend vs {prev_label} "
                "or a multi-day average."
            ),
            "based_on": None,
        }

    @staticmethod
    def _build_recommendations(
        *,
        label,
        prev_label,
        metrics,
        best_movers,
        slow_movers,
        demand_hints,
        demand_insufficient,
        category_wise,
        cash_share,
        online_share,
        sales_delta,
        outlook,
    ):
        recs = []
        if best_movers:
            top = best_movers[0]
            recs.append(
                {
                    "type": "best_mover",
                    "title": "Keep best mover available",
                    "detail": (
                        f"{top['item_name']} leads quantity in {label} "
                        f"({top['quantity']:g} sold, {_money(top['revenue'])}). "
                        "Prioritize stock/availability for this item."
                    ),
                    "based_on": top,
                }
            )

        if slow_movers and len(best_movers) > 1:
            slow = slow_movers[0]
            if slow["item_name"] != best_movers[0]["item_name"]:
                recs.append(
                    {
                        "type": "slow_mover",
                        "title": "Review slow mover",
                        "detail": (
                            f"{slow['item_name']} is among the lowest quantity sellers "
                            f"({slow['quantity']:g} sold, {_money(slow['revenue'])}). "
                            "Review pricing, placement, or promotions using this history."
                        ),
                        "based_on": slow,
                    }
                )

        rising = [h for h in demand_hints if h["direction"] == "up"]
        falling = [h for h in demand_hints if h["direction"] == "down"]
        if rising:
            tip = rising[0]
            recs.append(
                {
                    "type": "demand_up",
                    "title": "Rising demand",
                    "detail": (
                        f"{tip['item_name']} quantity rose "
                        f"{tip['previous_quantity']:g} → {tip['quantity']:g} "
                        f"vs {prev_label}. Plan inventory around this observed increase."
                    ),
                    "based_on": tip,
                }
            )
        if falling:
            tip = falling[0]
            recs.append(
                {
                    "type": "demand_down",
                    "title": "Softening demand",
                    "detail": (
                        f"{tip['item_name']} quantity fell "
                        f"{tip['previous_quantity']:g} → {tip['quantity']:g} "
                        f"vs {prev_label}. Investigate before over-ordering."
                    ),
                    "based_on": tip,
                }
            )
        elif demand_insufficient:
            recs.append(
                {
                    "type": "demand_insufficient",
                    "title": "Demand comparison unavailable",
                    "detail": (
                        f"No finalized sales in {prev_label}, so item demand change "
                        "hints cannot be computed yet."
                    ),
                    "based_on": {"previous_label": prev_label},
                }
            )

        if category_wise:
            lead = category_wise[0]
            recs.append(
                {
                    "type": "category_focus",
                    "title": "Category focus",
                    "detail": (
                        f"{lead['category_name']} is the top category in {label} "
                        f"({_money(lead['revenue'])}). Align promotions with this category."
                    ),
                    "based_on": lead,
                }
            )

        if cash_share is not None and cash_share >= 60:
            recs.append(
                {
                    "type": "payment_cash",
                    "title": "Cash-heavy mix",
                    "detail": (
                        f"Cash is {cash_share}% of sales "
                        f"({_money(metrics['cash_sales'])}). "
                        "Ensure end-of-day cash reconciliation capacity."
                    ),
                    "based_on": {
                        "cash_share_pct": cash_share,
                        "cash_sales": metrics["cash_sales"],
                    },
                }
            )
        elif online_share is not None and online_share >= 60:
            recs.append(
                {
                    "type": "payment_online",
                    "title": "Online-heavy mix",
                    "detail": (
                        f"Online is {online_share}% of sales "
                        f"({_money(metrics['online_sales'])}). "
                        "Confirm settlement reports match billed online totals."
                    ),
                    "based_on": {
                        "online_share_pct": online_share,
                        "online_sales": metrics["online_sales"],
                    },
                }
            )

        if int(metrics.get("cancelled_bills") or 0) > 0:
            recs.append(
                {
                    "type": "cancellations",
                    "title": "Review cancellations",
                    "detail": (
                        f"{int(metrics['cancelled_bills'])} cancelled bill(s) in {label}. "
                        "Check audit reasons to reduce repeat voids."
                    ),
                    "based_on": {"cancelled_bills": metrics["cancelled_bills"]},
                }
            )

        if sales_delta is not None and sales_delta < -10:
            recs.append(
                {
                    "type": "sales_down",
                    "title": "Sales down vs prior period",
                    "detail": (
                        f"Sales dropped {abs(sales_delta)}% vs {prev_label}. "
                        "Use top/slow movers above to focus recovery actions."
                    ),
                    "based_on": {"delta_pct": sales_delta, "previous_label": prev_label},
                }
            )

        if outlook.get("available"):
            recs.append(
                {
                    "type": "outlook",
                    "title": "Observed outlook",
                    "detail": outlook["detail"],
                    "based_on": outlook.get("based_on"),
                }
            )

        return recs

    @staticmethod
    def _build_insights(
        *,
        label,
        prev_label,
        metrics,
        previous,
        top_items,
        low_items,
        category_wise,
        day_wise,
        cash_share,
        online_share,
        sales_delta,
        bills_delta,
    ):
        insights = [
            {
                "type": "sales",
                "title": "Sales total",
                "detail": (
                    f"Total sales for {label}: {_money(metrics['total_sales'])} "
                    f"from {int(metrics['bill_count'])} bill(s); "
                    f"average bill {_money(metrics['average_bill'])}."
                ),
            }
        ]

        if sales_delta is not None:
            insights.append(
                {
                    "type": "trend",
                    "title": f"Vs {prev_label}",
                    "detail": (
                        f"Sales changed {sales_delta:+.1f}% "
                        f"({_money(previous['total_sales'])} → {_money(metrics['total_sales'])})."
                    ),
                }
            )
        elif int(previous.get("bill_count") or 0) == 0:
            insights.append(
                {
                    "type": "trend",
                    "title": f"Vs {prev_label}",
                    "detail": f"No finalized sales in {prev_label} for comparison.",
                }
            )

        if bills_delta is not None:
            insights.append(
                {
                    "type": "bills",
                    "title": "Bill volume",
                    "detail": (
                        f"Bill count changed {bills_delta:+.1f}% "
                        f"({int(previous['bill_count'])} → {int(metrics['bill_count'])})."
                    ),
                }
            )

        if cash_share is not None:
            insights.append(
                {
                    "type": "payment_mix",
                    "title": "Payment mix",
                    "detail": (
                        f"Cash {_money(metrics['cash_sales'])} ({cash_share}%) · "
                        f"Online {_money(metrics['online_sales'])} ({online_share or 0}%)."
                    ),
                }
            )

        if top_items:
            lines = ", ".join(
                f"{row['item_name']} ({_money(row['revenue'])})" for row in top_items[:3]
            )
            insights.append(
                {
                    "type": "top_items",
                    "title": "Top items",
                    "detail": f"Highest revenue items: {lines}.",
                }
            )

        if low_items and len(top_items) > 1:
            lines = ", ".join(
                f"{row['item_name']} ({_money(row['revenue'])})"
                for row in low_items[:3]
            )
            insights.append(
                {
                    "type": "low_items",
                    "title": "Lowest revenue items",
                    "detail": f"Lowest revenue among sold items: {lines}.",
                }
            )

        if category_wise:
            top_cat = category_wise[0]
            insights.append(
                {
                    "type": "categories",
                    "title": "Category lead",
                    "detail": (
                        f"{top_cat['category_name']} leads with "
                        f"{_money(top_cat['revenue'])} "
                        f"({float(top_cat['quantity']):.0f} qty)."
                    ),
                }
            )

        if int(metrics.get("cancelled_bills") or 0) > 0:
            insights.append(
                {
                    "type": "cancelled",
                    "title": "Cancelled bills",
                    "detail": (
                        f"{int(metrics['cancelled_bills'])} cancelled bill(s) in {label} "
                        "(excluded from sales totals)."
                    ),
                }
            )

        if len(day_wise) >= 2:
            best = max(day_wise, key=lambda row: row["total_sales"])
            insights.append(
                {
                    "type": "day_trend",
                    "title": "Strongest day",
                    "detail": (
                        f"{best['date']} had the highest sales "
                        f"({_money(best['total_sales'])}, {int(best['bill_count'])} bills)."
                    ),
                }
            )

        return insights
