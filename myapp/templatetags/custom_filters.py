# custom_filters.py
from django import template

register = template.Library()

@register.filter
def get_range(value, start=0):
    return range(start, value)
