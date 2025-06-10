from django import template

register = template.Library()

@register.filter(name='resize')
def resize(value):
    """Removes all values of arg from the given string"""
    return value.replace("__medium", '')


@register.filter(name='uncdn')
def uncdn(value):
    """Removes all references to CDN"""
    url = value.replace("cdn.nivoli.com/adventuregamers", 'adventuregamers.com')
    if "wp-content" not in url:
        url = url.replace("adventuregamers.com/", 'adventuregamers.com/wp-content/uploads/')
    return url
