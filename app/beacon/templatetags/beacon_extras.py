from django import template

register = template.Library()

@register.filter
def lookup(d, key):
    try:
        value = d[key]
        return value
    except:
        return "-"

@register.filter
def startswith(string, pattern):
    if string.startswith(pattern):
        return True
    return False