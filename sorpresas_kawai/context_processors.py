"""
Procesadores de Contexto Globales - Sorpresas Kawaii.

Inyectan variables globales en el contexto de renderizado de todas las plantillas HTML:
- Conteo en tiempo real de articulos en el carrito de compras.
- Parametros globales de disponibilidad de la tienda (ConfiguracionTienda).
"""

from django.db.models import Sum
from .models import ItemCarrito


def carrito_context(request):
    """
    Calcula y suministra de forma global la variable 'carrito_total_items'
    para actualizar la insignia numerica en la barra de navegacion (navbar).
    """
    total_items = 0
    if request.user.is_authenticated:
        try:
            resultado = ItemCarrito.objects.filter(
                carrito__usuario=request.user
            ).aggregate(total=Sum('cantidad'))
            total_items = resultado.get('total') or 0
        except Exception:
            total_items = 0

    return {
        'carrito_total_items': total_items,
    }


def configuracion_tienda_context(request):
    """
    Suministra la instancia singleton de configuracion global ('config_tienda')
    a todas las plantillas para verificar el estado de los interruptores de mantenimiento
    y las politicas de envio en tiempo real.
    """
    try:
        from .models import ConfiguracionTienda
        config = ConfiguracionTienda.get_solo()
    except Exception:
        config = None

    return {
        'config_tienda': config,
    }
