"""Tour package HTTP controller (BIZ-56)."""

from flask import request

from app.schemas.tour_package_schemas import (
    bill_tour_package_schema,
    create_tour_package_schema,
    update_tour_package_schema,
)
from app.services.tour_package_service import TourPackageService
from app.utils.responses import success_response


def list_packages():
    active = request.args.get("active_only", "false").lower() in {"1", "true", "yes"}
    data, meta = TourPackageService.list_packages(
        q=request.args.get("q"),
        active_only=active,
        page=int(request.args.get("page", 1)),
        per_page=int(request.args.get("per_page", 50)),
    )
    return success_response(data=data, meta=meta)


def get_package(package_id: str):
    return success_response(data=TourPackageService.get_package(package_id))


def create_package():
    payload = create_tour_package_schema.load(request.get_json() or {})
    data = TourPackageService.create(**payload)
    return success_response(data=data, status_code=201)


def update_package(package_id: str):
    payload = update_tour_package_schema.load(request.get_json() or {})
    data = TourPackageService.update(package_id, **payload)
    return success_response(data=data)


def bill_package(package_id: str):
    payload = bill_tour_package_schema.load(request.get_json() or {})
    data = TourPackageService.bill_package(package_id, **payload)
    return success_response(data=data, status_code=201)
