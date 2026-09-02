"""Tour package routes (BIZ-56)."""

from flask import Blueprint

from app.constants.permissions import PERM_BILLING, PERM_ITEMS_READ, PERM_ITEMS_WRITE
from app.controllers import (
    tour_package_controller,
    travel_agent_controller,
    travel_booking_controller,
    travel_booking_detail_controller,
)
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

tour_packages_bp = Blueprint("tour_packages", __name__, url_prefix="/tour-packages")
travel_bp = Blueprint("travel", __name__, url_prefix="/travel")

_READ = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
# items.write is Owner-only (BIZ-03 / BIZ-65 matrix).
_WRITE = (ROLE_OWNER,)
_BOOKING_WRITE = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
_MANAGE = (ROLE_OWNER, ROLE_MANAGER)
_OWNER = (ROLE_OWNER,)


@tour_packages_bp.get("")
@roles_required(*_READ)
@module_required("tour_packages")
@permission_required(PERM_ITEMS_READ)
def list_packages():
    return tour_package_controller.list_packages()


@tour_packages_bp.post("")
@roles_required(*_WRITE)
@module_required("tour_packages")
@permission_required(PERM_ITEMS_WRITE)
def create_package():
    return tour_package_controller.create_package()


@tour_packages_bp.get("/<package_id>")
@roles_required(*_READ)
@module_required("tour_packages")
@permission_required(PERM_ITEMS_READ)
def get_package(package_id):
    return tour_package_controller.get_package(package_id)


@tour_packages_bp.patch("/<package_id>")
@roles_required(*_WRITE)
@module_required("tour_packages")
@permission_required(PERM_ITEMS_WRITE)
def update_package(package_id):
    return tour_package_controller.update_package(package_id)


@tour_packages_bp.delete("/<package_id>")
@roles_required(ROLE_OWNER)
@module_required("tour_packages")
@permission_required(PERM_ITEMS_WRITE)
def delete_package(package_id):
    return tour_package_controller.delete_package(package_id)


@tour_packages_bp.post("/<package_id>/bill")
@roles_required(*_READ)
@module_required("tour_packages")
@permission_required(PERM_BILLING)
def bill_package(package_id):
    return tour_package_controller.bill_package(package_id)


# Travel namespace aliases (docs: /travel/packages)
@travel_bp.get("/packages")
@roles_required(*_READ)
@module_required("tour_packages")
@permission_required(PERM_ITEMS_READ)
def travel_list_packages():
    return tour_package_controller.list_packages()


@travel_bp.post("/packages")
@roles_required(*_WRITE)
@module_required("tour_packages")
@permission_required(PERM_ITEMS_WRITE)
def travel_create_package():
    return tour_package_controller.create_package()


@travel_bp.get("/packages/<package_id>")
@roles_required(*_READ)
@module_required("tour_packages")
@permission_required(PERM_ITEMS_READ)
def travel_get_package(package_id):
    return tour_package_controller.get_package(package_id)


@travel_bp.patch("/packages/<package_id>")
@roles_required(*_WRITE)
@module_required("tour_packages")
@permission_required(PERM_ITEMS_WRITE)
def travel_update_package(package_id):
    return tour_package_controller.update_package(package_id)


@travel_bp.delete("/packages/<package_id>")
@roles_required(ROLE_OWNER)
@module_required("tour_packages")
@permission_required(PERM_ITEMS_WRITE)
def travel_delete_package(package_id):
    return tour_package_controller.delete_package(package_id)


@travel_bp.post("/packages/<package_id>/bill")
@roles_required(*_READ)
@module_required("tour_packages")
@permission_required(PERM_BILLING)
def travel_bill_package(package_id):
    return tour_package_controller.bill_package(package_id)


@travel_bp.get("/bookings")
@roles_required(*_READ)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def travel_list_bookings():
    return travel_booking_controller.list_bookings()


@travel_bp.post("/bookings")
@roles_required(*_BOOKING_WRITE)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def travel_create_booking():
    return travel_booking_controller.create_booking()


@travel_bp.get("/bookings/<booking_id>")
@roles_required(*_READ)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def travel_get_booking(booking_id):
    return travel_booking_controller.get_booking(booking_id)


@travel_bp.patch("/bookings/<booking_id>")
@roles_required(ROLE_OWNER)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def travel_update_booking(booking_id):
    return travel_booking_controller.update_booking(booking_id)


@travel_bp.delete("/bookings/<booking_id>")
@roles_required(ROLE_OWNER)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def travel_delete_booking(booking_id):
    return travel_booking_controller.delete_booking(booking_id)


@travel_bp.patch("/bookings/<booking_id>/status")
@roles_required(*_MANAGE)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def travel_update_booking_status(booking_id):
    return travel_booking_controller.update_booking_status(booking_id)


@travel_bp.post("/bookings/<booking_id>/payments")
@roles_required(*_BOOKING_WRITE)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def travel_record_payment(booking_id):
    return travel_booking_controller.record_payment(booking_id)


@travel_bp.get("/bookings/<booking_id>/itinerary")
@roles_required(*_READ)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def travel_list_itinerary(booking_id):
    return travel_booking_detail_controller.list_itinerary(booking_id)


@travel_bp.post("/bookings/<booking_id>/itinerary")
@roles_required(*_MANAGE)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def travel_create_itinerary(booking_id):
    return travel_booking_detail_controller.create_itinerary(booking_id)


@travel_bp.patch("/bookings/<booking_id>/itinerary/<item_id>")
@roles_required(*_MANAGE)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def travel_update_itinerary(booking_id, item_id):
    return travel_booking_detail_controller.update_itinerary(booking_id, item_id)


@travel_bp.delete("/bookings/<booking_id>/itinerary/<item_id>")
@roles_required(*_MANAGE)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def travel_delete_itinerary(booking_id, item_id):
    return travel_booking_detail_controller.delete_itinerary(booking_id, item_id)


@travel_bp.get("/bookings/<booking_id>/documents")
@roles_required(*_READ)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def travel_list_documents(booking_id):
    return travel_booking_detail_controller.list_documents(booking_id)


@travel_bp.post("/bookings/<booking_id>/documents")
@roles_required(*_MANAGE)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def travel_create_document(booking_id):
    return travel_booking_detail_controller.create_document(booking_id)


@travel_bp.delete("/bookings/<booking_id>/documents/<document_id>")
@roles_required(*_MANAGE)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def travel_delete_document(booking_id, document_id):
    return travel_booking_detail_controller.delete_document(booking_id, document_id)


@travel_bp.get("/agents")
@roles_required(*_READ)
@module_required("travel_commission")
@permission_required(PERM_BILLING)
def travel_list_agents():
    return travel_agent_controller.list_agents()


@travel_bp.post("/agents")
@roles_required(*_OWNER)
@module_required("travel_commission")
@permission_required(PERM_BILLING)
def travel_create_agent():
    return travel_agent_controller.create_agent()


@travel_bp.get("/agents/<agent_id>")
@roles_required(*_READ)
@module_required("travel_commission")
@permission_required(PERM_BILLING)
def travel_get_agent(agent_id):
    return travel_agent_controller.get_agent(agent_id)


@travel_bp.patch("/agents/<agent_id>")
@roles_required(*_OWNER)
@module_required("travel_commission")
@permission_required(PERM_BILLING)
def travel_update_agent(agent_id):
    return travel_agent_controller.update_agent(agent_id)


@travel_bp.delete("/agents/<agent_id>")
@roles_required(ROLE_OWNER)
@module_required("travel_commission")
@permission_required(PERM_BILLING)
def travel_delete_agent(agent_id):
    return travel_agent_controller.delete_agent(agent_id)


@travel_bp.get("/commissions")
@roles_required(*_READ)
@module_required("travel_commission")
@permission_required(PERM_BILLING)
def travel_list_commissions():
    return travel_agent_controller.list_commissions()


@travel_bp.get("/commissions/report")
@roles_required(*_READ)
@module_required("travel_commission")
@permission_required(PERM_BILLING)
def travel_commission_report():
    return travel_agent_controller.commission_report()


@travel_bp.post("/commissions")
@roles_required(*_OWNER)
@module_required("travel_commission")
@permission_required(PERM_BILLING)
def travel_create_commission():
    return travel_agent_controller.create_commission()


@travel_bp.patch("/commissions/<entry_id>/status")
@roles_required(*_OWNER)
@module_required("travel_commission")
@permission_required(PERM_BILLING)
def travel_update_commission_status(entry_id):
    return travel_agent_controller.update_commission_status(entry_id)
