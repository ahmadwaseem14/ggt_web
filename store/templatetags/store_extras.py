from django import template
from django.utils.safestring import mark_safe
import json

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using a variable key"""
    return dictionary.get(key)

@register.filter
def get_attr(obj, attr):
    """Get an attribute from an object using a variable attribute name"""
    try:
        return getattr(obj, attr)
    except (AttributeError, TypeError):
        return None

@register.filter
def getattribute(obj, attr):
    """Get an attribute from an object using a variable attribute name"""
    try:
        return getattr(obj, attr)
    except (AttributeError, TypeError):
        return None

@register.filter
def jsonify(value):
    """Convert a Python object to a JSON string"""
    return mark_safe(json.dumps(value))

@register.filter
def display_field_value(obj, field_name):
    """Format field values for display in comparison table"""
    value = getattr(obj, field_name, None)
    
    # Handle boolean values
    if isinstance(value, bool):
        return "Yes" if value else "No"
    
    # Handle None values
    if value is None:
        return "N/A"
    
    # Return the value as string
    return str(value) 