"""Clothing POS HTTP controller (BIZ-26)."""

from flask import request

from app.constants.perf import POS_CATALOG_DEFAULT_LIMIT
from app.services.clothing_pos_service import ClothingPosService
from app.utils.responses import success_response


def pos_catalog():
    q = request.args.get("q")
    limit = int(request.args.get("limit", POS_CATALOG_DEFAULT_LIMIT))
    return success_response(data=ClothingPosService.pos_catalog(q=q, limit=limit))
