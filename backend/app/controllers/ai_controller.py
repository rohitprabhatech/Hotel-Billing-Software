"""AI business assistant HTTP controller."""

from flask import request

from app.services.ai_assistant_service import AiAssistantService
from app.utils.responses import success_response


def _period_args():
    return {
        "period": request.args.get("period", "today"),
        "from_date": request.args.get("from"),
        "to_date": request.args.get("to"),
    }


def analyze():
    args = _period_args()
    data = AiAssistantService.analyze(**args)
    return success_response(data=data)


def decisions():
    args = _period_args()
    data = AiAssistantService.decisions(**args)
    return success_response(data=data)
