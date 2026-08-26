"""Travel agent / commission HTTP controller (BIZ-59)."""

from flask import request

from app.schemas.travel_agent_schemas import (
    create_commission_entry_schema,
    create_travel_agent_schema,
    update_commission_status_schema,
    update_travel_agent_schema,
)
from app.services.travel_agent_service import TravelAgentService
from app.utils.responses import success_response


def list_agents():
    active_only = str(request.args.get("active_only", "")).lower() in ("1", "true", "yes")
    data, meta = TravelAgentService.list_agents(
        active_only=active_only,
        page=int(request.args.get("page", 1)),
        per_page=int(request.args.get("per_page", 50)),
    )
    return success_response(data=data, meta=meta)


def get_agent(agent_id: str):
    return success_response(data=TravelAgentService.get_agent(agent_id))


def create_agent():
    payload = create_travel_agent_schema.load(request.get_json() or {})
    data = TravelAgentService.create_agent(**payload)
    return success_response(data=data, status_code=201)


def update_agent(agent_id: str):
    raw = request.get_json() or {}
    payload = update_travel_agent_schema.load(raw)
    fields = {key: payload[key] for key in payload if key in raw}
    data = TravelAgentService.update_agent(agent_id, **fields)
    return success_response(data=data)


def list_commissions():
    data, meta = TravelAgentService.list_commissions(
        agent_id=request.args.get("agent_id"),
        status=request.args.get("status"),
        page=int(request.args.get("page", 1)),
        per_page=int(request.args.get("per_page", 50)),
    )
    return success_response(data=data, meta=meta)


def commission_report():
    return success_response(data=TravelAgentService.commission_report())


def create_commission():
    payload = create_commission_entry_schema.load(request.get_json() or {})
    data = TravelAgentService.create_commission(**payload)
    return success_response(data=data, status_code=201)


def update_commission_status(entry_id: str):
    payload = update_commission_status_schema.load(request.get_json() or {})
    data = TravelAgentService.update_commission_status(entry_id, **payload)
    return success_response(data=data)
