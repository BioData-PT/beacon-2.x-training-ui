from django import template

register = template.Library()

@register.filter
def lookup(d, key):
    try:
        value = d[key]
        return value
    except:
        return "-"