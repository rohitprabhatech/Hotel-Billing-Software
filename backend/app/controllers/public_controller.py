"""Anonymous/public landing APIs."""

from app.services.plan_service import PlanService
from app.utils.responses import success_response


def list_public_plans():
    return success_response(data=PlanService.list_public_plans())
