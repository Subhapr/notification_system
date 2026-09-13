"""
Consistent API response envelope used across every endpoint in the
project, so frontend code can rely on a single predictable shape.
"""
from rest_framework.response import Response


def success_response(data=None, message="", status=200, meta=None):
    payload = {"success": True, "message": message, "data": data}
    if meta is not None:
        payload["meta"] = meta
    return Response(payload, status=status)


def error_response(message="Something went wrong.", errors=None, status=400):
    return Response(
        {"success": False, "message": message, "errors": errors or {}},
        status=status,
    )
