from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """{{ my_dict|get_item:key }}"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.filter
def widget_type(field):
    """Returns the widget class name for a BoundField. Usage: {{ field|widget_type }}"""
    return field.field.widget.__class__.__name__


@register.filter
def is_checkbox_select(field):
    """Returns True if the widget is CheckboxSelectMultiple."""
    return 'CheckboxSelectMultiple' in field.field.widget.__class__.__name__
