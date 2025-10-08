from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    try:
        return dictionary.get(key, "-")
    except:
        return "-"
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
from django import template

register = template.Library()

@register.filter
def get_item(value, arg):
    # Ensure value is a dictionary
    if isinstance(value, dict):
        return value.get(arg, 'default_value')  # Adjust default_value as needed
    return ''  # Or any fallback if value is not a dictionary

