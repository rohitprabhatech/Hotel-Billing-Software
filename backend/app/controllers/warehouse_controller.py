"""Warehouse HTTP controller (BIZ-38)."""

from flask import request

from app.schemas.warehouse_schemas import (
    create_stock_transfer_schema,
    create_warehouse_schema,
    update_warehouse_schema,
)
from app.services.warehouse_service import WarehouseService
from app.utils.responses import success_response


def list_warehouses():
    include_inactive = str(request.args.get("include_inactive", "")).lower() in {
        "1",
        "true",
        "yes",
    }
    return success_response(
        data=WarehouseService.list_warehouses(include_inactive=include_inactive)
    )


def create_warehouse():
    payload = create_warehouse_schema.load(request.get_json() or {})
    data = WarehouseService.create_warehouse(
        code=payload["code"],
        name=payload["name"],
        address=payload.get("address"),
        notes=payload.get("notes"),
        is_default=payload.get("is_default") or False,
    )
    return success_response(data=data, status_code=201)


def update_warehouse(warehouse_id: str):
    payload = update_warehouse_schema.load(request.get_json() or {})
    data = WarehouseService.update_warehouse(
        warehouse_id,
        name=payload.get("name"),
        address=payload.get("address"),
        notes=payload.get("notes"),
        is_active=payload.get("is_active"),
        is_default=payload.get("is_default"),
    )
    return success_response(data=data)


def list_stocks():
    data, meta = WarehouseService.list_stocks(
        warehouse_id=request.args.get("warehouse_id"),
        item_id=request.args.get("item_id"),
        page=int(request.args.get("page", 1)),
        per_page=int(request.args.get("per_page", 100)),
    )
    return success_response(data=data, meta=meta)


def list_transfers():
    data, meta = WarehouseService.list_transfers(
        page=int(request.args.get("page", 1)),
        per_page=int(request.args.get("per_page", 50)),
    )
    return success_response(data=data, meta=meta)


def get_transfer(transfer_id: str):
    return success_response(data=WarehouseService.get_transfer(transfer_id))


def create_transfer():
    payload = create_stock_transfer_schema.load(request.get_json() or {})
    data = WarehouseService.create_transfer(
        from_warehouse_id=payload["from_warehouse_id"],
        to_warehouse_id=payload["to_warehouse_id"],
        items=payload["items"],
        notes=payload.get("notes"),
    )
    return success_response(data=data, status_code=201)
