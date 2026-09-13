"""
Central exception handler. Ensures the API never leaks stack traces
or internal error details to clients, while still logging the full
detail server-side for debugging.
"""
import logging

from rest_framework.views import exception_handler

logger = logging.getLogger("notifications")


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        detail = response.data
        message = "Request failed."
        if isinstance(detail, dict) and "detail" in detail:
            message = str(detail["detail"])
        elif isinstance(detail, list) and detail:
            message = str(detail[0])

        response.data = {
            "success": False,
            "message": message,
            "errors": detail if isinstance(detail, dict) else {"detail": detail},
        }
        return response

    # Unhandled exception: log full detail, return a safe generic message.
    logger.exception("Unhandled exception in API view: %s", exc)
    from apps.core.responses import error_response

    return error_response(
        message="An unexpected error occurred. Please try again later.",
        status=500,
    )
