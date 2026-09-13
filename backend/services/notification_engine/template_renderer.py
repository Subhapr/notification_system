"""
Controlled variable-substitution renderer.

Deliberately does NOT use Python's str.format, Django templates with
arbitrary context, or any eval-based mechanism - only a fixed
{{variable_name}} pattern is substituted, and only with values from a
known, explicit context dict. Unknown variables are left as an empty
string rather than raising, so a misconfigured template never crashes
the send pipeline.
"""
import re

VARIABLE_PATTERN = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")


def render_template_string(template_string: str, context: dict) -> str:
    if not template_string:
        return ""

    def _replace(match):
        key = match.group(1)
        value = context.get(key, "")
        return "" if value is None else str(value)

    return VARIABLE_PATTERN.sub(_replace, template_string)


def extract_variable_names(template_string: str) -> list:
    """Returns the distinct {{variable}} names referenced in a template string."""
    if not template_string:
        return []
    seen = []
    for match in VARIABLE_PATTERN.finditer(template_string):
        name = match.group(1)
        if name not in seen:
            seen.append(name)
    return seen
