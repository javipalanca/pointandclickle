from django import template

register = template.Library()

@register.filter(name='resize')
def resize(value):
    """Removes all values of arg from the given string"""
    return value.replace("__medium", '')

