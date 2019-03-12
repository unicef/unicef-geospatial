import json

from django import template

register = template.Library()


@register.filter
def pretty(value):
    return json.dumps(value, indent=4)
