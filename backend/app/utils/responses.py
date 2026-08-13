"""Standard API success/error envelopes."""

from flask import jsonify


def success_response(data=None, meta=None, status_code: int = 200):
    return (
        jsonify(
            {
                "success": True,
                "data": data,
                "meta": meta,
                "error": None,
            }
        ),
        status_code,
    )


def error_response(
    message: str,
    code: str = "ERROR",
    status_code: int = 400,
    details=None,
):
    return (
        jsonify(
            {
                "success": False,
                "data": None,
                "meta": None,
                "error": {
                    "code": code,
                    "message": message,
                    "details": details or {},
                },
            }
        ),
        status_code,
    )