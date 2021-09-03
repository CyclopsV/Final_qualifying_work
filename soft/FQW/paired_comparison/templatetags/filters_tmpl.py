from django.template.defaulttags import register


@register.filter
def get_range(value):
    if type(value) == int:
        result = range(value)
    else:
        result = range(len(value))
    return result


@register.filter
def get_index(value, i):
    return value[i]


@register.filter
def sum_list(value):
    result = 0
    for i in value:
        if i:
            result += i
    return result
