from django import template
import json

register = template.Library()

@register.filter
def tojson(value):
    """
    Converts a Python object (e.g., dict) to a formatted JSON string with indentation.
    """
    return json.dumps(value, indent=2, ensure_ascii=False)