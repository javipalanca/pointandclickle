from django import template

register = template.Library()

@register.filter(name='resize')
def resize(value):
    """Removes all values of arg from the given string"""
    return value.replace("__medium", '')


@register.filter(name='uncdn')
def uncdn(value):
    """Removes all references to CDN"""
    return value.replace("cdn.nivoli.com/adventuregamers", 'adventuregamers.com')
