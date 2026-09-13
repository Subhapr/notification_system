"""
Registry describing which {{variables}} are available for each trigger
code, and how to build the actual substitution context for a given
user + extra event data.

Adding a new trigger only requires adding an entry here (plus a
Trigger row in the database) - no changes to the engine itself.
"""
from django.conf import settings

# Variables that are always available, regardless of trigger.
COMMON_VARIABLES = ["user_name", "email", "phone", "site_name"]

TRIGGER_VARIABLES = {
    "LOGIN": COMMON_VARIABLES + ["login_time"],
    "LOGOUT": COMMON_VARIABLES + ["logout_time"],
    "NOT_LOGGED_IN_1_DAY": COMMON_VARIABLES + ["last_login_time"],
    "NOT_LOGGED_IN_1_WEEK": COMMON_VARIABLES + ["last_login_time"],
    "PASSWORD_RESET": COMMON_VARIABLES + ["reset_link"],
    "ORDER_PLACED": COMMON_VARIABLES + ["order_id", "order_total"],
}


def available_variables_for(trigger_code: str) -> list:
    return TRIGGER_VARIABLES.get(trigger_code, COMMON_VARIABLES)


def build_context(user, extra_context: dict = None) -> dict:
    """
    Builds the substitution context for a notification. `extra_context`
    (event-specific data, e.g. login_time) always wins over defaults.
    """
    context = {
        "user_name": getattr(user, "display_name", "") if user else "",
        "email": getattr(user, "email", "") if user else "",
        "phone": getattr(user, "phone_number", "") if user else "",
        "site_name": settings.SITE_NAME,
    }
    if extra_context:
        context.update(extra_context)
    return context
