from django import template

register = template.Library()

@register.filter
def get(dictionary, key):
    """
    Permite acceder a un valor de diccionario usando una clave dinámica
    dentro de las plantillas de Django.
    Uso: {{ diccionario|get:clave }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None


@register.filter
def subtract(value, arg):
    """
    Resta dos valores numéricos dentro de plantillas de Django.
    Uso: {{ valor1|subtract:valor2 }}
    """
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0
