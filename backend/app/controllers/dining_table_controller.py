"""Dining table HTTP controller (BIZ-12)."""

from flask import request

from app.schemas.dining_table_schemas import (
    create_dining_table_schema,
    dining_table_status_schema,
    merge_dining_tables_schema,
    unmerge_dining_tables_schema,
    update_dining_table_schema,
)
from app.services.dining_table_service import DiningTableService
from app.utils.responses import success_response


def list_tables():
    section = request.args.get("section")
    status = request.args.get("status")
    include_merged = request.args.get("include_merged_children", "").lower() in {"1", "true", "yes"}
    data = DiningTableService.list_tables(
        section=section,
        status=status,
        include_merged_children=include_merged,
    )
    return success_response(data=data, meta={"total": len(data)})


def get_table(table_id: str):
    return success_response(data=DiningTableService.get_table(table_id))


def create_table():
    payload = create_dining_table_schema.load(request.get_json() or {})
    data = DiningTableService.create_table(
        code=payload["code"],
        section=payload.get("section"),
        capacity=payload.get("capacity"),
    )
    return success_response(data=data, status_code=201)


def update_table(table_id: str):
    raw = request.get_json() or {}
    payload = update_dining_table_schema.load(raw)
    data = DiningTableService.update_table(
        table_id,
        code=payload.get("code") if "code" in raw else None,
        section=payload.get("section") if "section" in raw else None,
        capacity=payload.get("capacity") if "capacity" in raw else None,
        code_provided="code" in raw,
        section_provided="section" in raw,
        capacity_provided="capacity" in raw,
    )
    return success_response(data=data)


def deactivate_table(table_id: str):
    data = DiningTableService.deactivate_table(table_id)
    return success_response(data=data)


def set_table_status(table_id: str):
    payload = dining_table_status_schema.load(request.get_json() or {})
    data = DiningTableService.set_status(table_id, payload["status"])
    return success_response(data=data)


def merge_tables():
    payload = merge_dining_tables_schema.load(request.get_json() or {})
    data = DiningTableService.merge_tables(
        primary_table_id=payload["primary_table_id"],
        secondary_table_ids=payload["secondary_table_ids"],
    )
    return success_response(data=data)


def unmerge_tables():
    payload = unmerge_dining_tables_schema.load(request.get_json() or {})
    data = DiningTableService.unmerge_tables(primary_table_id=payload["primary_table_id"])
    return success_response(data=data)
