"""Grocery fast POS HTTP controller (BIZ-20)."""

from flask import request

from app.services.grocery_pos_service import GroceryPosService
from app.utils.responses import success_response


def pos_catalog():
    q = request.args.get("q")
    limit = int(request.args.get("limit", 200))
    return success_response(data=GroceryPosService.pos_catalog(q=q, limit=limit))
