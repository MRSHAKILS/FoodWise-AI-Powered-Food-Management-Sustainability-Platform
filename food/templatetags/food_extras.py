"""Custom template tags and filters for food app"""
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key"""
    if dictionary is None:
        return None
    return dictionary.get(key)
