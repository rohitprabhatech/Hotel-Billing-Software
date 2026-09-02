"""Travel agents and commissions routes (BIZ-59)."""

from flask import Blueprint

from app.constants.permissions import PERM_BILLING
from app.controllers import travel_agent_controller
from app.middleware.auth import roles_required
from app.models.role import ROLE_BILLING_USER, ROLE_MANAGER, ROLE_OWNER
from app.utils.module_access import module_required
from app.utils.permission_access import permission_required

travel_agents_bp = Blueprint("travel_agents", __name__, url_prefix="/travel-agents")
commissions_bp = Blueprint("commissions", __name__, url_prefix="/commissions")

_READ = (ROLE_OWNER, ROLE_MANAGER, ROLE_BILLING_USER)
_WRITE = (ROLE_OWNER,)


@travel_agents_bp.get("")
@roles_required(*_READ)
@module_required("travel_commission")
@permission_required(PERM_BILLING)
def list_agents():
    return travel_agent_controller.list_agents()


@travel_agents_bp.post("")
@roles_required(*_WRITE)
@module_required("travel_commission")
@permission_required(PERM_BILLING)
def create_agent():
    return travel_agent_controller.create_agent()


@travel_agents_bp.get("/<agent_id>")
@roles_required(*_READ)
@module_required("travel_commission")
@permission_required(PERM_BILLING)
def get_agent(agent_id):
    return travel_agent_controller.get_agent(agent_id)


@travel_agents_bp.patch("/<agent_id>")
@roles_required(*_WRITE)
@module_required("travel_commission")
@permission_required(PERM_BILLING)
def update_agent(agent_id):
    return travel_agent_controller.update_agent(agent_id)


@travel_agents_bp.delete("/<agent_id>")
@roles_required(ROLE_OWNER)
@module_required("travel_commission")
@permission_required(PERM_BILLING)
def delete_agent(agent_id):
    return travel_agent_controller.delete_agent(agent_id)


@commissions_bp.get("")
@roles_required(*_READ)
@module_required("travel_commission")
@permission_required(PERM_BILLING)
def list_commissions():
    return travel_agent_controller.list_commissions()


@commissions_bp.get("/report")
@roles_required(*_READ)
@module_required("travel_commission")
@permission_required(PERM_BILLING)
def commission_report():
    return travel_agent_controller.commission_report()


@commissions_bp.post("")
@roles_required(*_WRITE)
@module_required("travel_commission")
@permission_required(PERM_BILLING)
def create_commission():
    return travel_agent_controller.create_commission()


@commissions_bp.patch("/<entry_id>/status")
@roles_required(*_WRITE)
@module_required("travel_commission")
@permission_required(PERM_BILLING)
def update_commission_status(entry_id):
    return travel_agent_controller.update_commission_status(entry_id)
