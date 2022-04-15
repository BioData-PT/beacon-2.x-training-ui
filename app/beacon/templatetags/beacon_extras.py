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

@register.filter
def sum_dict_values(d):
    values_list = d.values()
    return sum(values_list)