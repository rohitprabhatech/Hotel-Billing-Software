"""Travel booking routes (BIZ-57)."""

from flask import Blueprint

from app.constants.permissions import PERM_BILLING
from app.controllers import travel_booking_controller, travel_booking_detail_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

travel_bookings_bp = Blueprint("travel_bookings", __name__, url_prefix="/travel-bookings")

_READ = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
_WRITE = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
_MANAGE = (ROLE_OWNER, ROLE_MANAGER)


@travel_bookings_bp.get("")
@roles_required(*_READ)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def list_bookings():
    return travel_booking_controller.list_bookings()


@travel_bookings_bp.post("")
@roles_required(*_WRITE)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def create_booking():
    return travel_booking_controller.create_booking()


@travel_bookings_bp.get("/<booking_id>")
@roles_required(*_READ)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def get_booking(booking_id):
    return travel_booking_controller.get_booking(booking_id)


@travel_bookings_bp.patch("/<booking_id>")
@roles_required(ROLE_OWNER)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def update_booking(booking_id):
    return travel_booking_controller.update_booking(booking_id)


@travel_bookings_bp.delete("/<booking_id>")
@roles_required(ROLE_OWNER)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def delete_booking(booking_id):
    return travel_booking_controller.delete_booking(booking_id)


@travel_bookings_bp.patch("/<booking_id>/status")
@roles_required(*_MANAGE)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def update_booking_status(booking_id):
    return travel_booking_controller.update_booking_status(booking_id)


@travel_bookings_bp.post("/<booking_id>/payments")
@roles_required(*_WRITE)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def record_payment(booking_id):
    return travel_booking_controller.record_payment(booking_id)


@travel_bookings_bp.get("/<booking_id>/itinerary")
@roles_required(*_READ)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def list_itinerary(booking_id):
    return travel_booking_detail_controller.list_itinerary(booking_id)


@travel_bookings_bp.post("/<booking_id>/itinerary")
@roles_required(*_MANAGE)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def create_itinerary(booking_id):
    return travel_booking_detail_controller.create_itinerary(booking_id)


@travel_bookings_bp.patch("/<booking_id>/itinerary/<item_id>")
@roles_required(*_MANAGE)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def update_itinerary(booking_id, item_id):
    return travel_booking_detail_controller.update_itinerary(booking_id, item_id)


@travel_bookings_bp.delete("/<booking_id>/itinerary/<item_id>")
@roles_required(*_MANAGE)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def delete_itinerary(booking_id, item_id):
    return travel_booking_detail_controller.delete_itinerary(booking_id, item_id)


@travel_bookings_bp.get("/<booking_id>/documents")
@roles_required(*_READ)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def list_documents(booking_id):
    return travel_booking_detail_controller.list_documents(booking_id)


@travel_bookings_bp.post("/<booking_id>/documents")
@roles_required(*_MANAGE)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def create_document(booking_id):
    return travel_booking_detail_controller.create_document(booking_id)


@travel_bookings_bp.delete("/<booking_id>/documents/<document_id>")
@roles_required(*_MANAGE)
@module_required("travel_bookings")
@permission_required(PERM_BILLING)
def delete_document(booking_id, document_id):
    return travel_booking_detail_controller.delete_document(booking_id, document_id)
