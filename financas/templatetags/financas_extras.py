from datetime import date

from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def query_params(context, **kwargs):
    """Retorna a query string atual substituindo os parâmetros fornecidos."""
    request = context['request']
    params = request.GET.copy()
    for key, value in kwargs.items():
        params[key] = value
    return params.urlencode()


@register.filter
def dias_para(data):
    """Retorna número de dias entre hoje e a data informada (negativo = passada)."""
    if not data:
        return None
    return (data - date.today()).days


@register.filter
def brl(value):
    """Formata um número como moeda brasileira: 1.234,56"""
    try:
        return f'{float(value):,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    except (ValueError, TypeError):
        return '0,00'
