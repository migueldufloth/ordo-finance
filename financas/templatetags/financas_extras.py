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
