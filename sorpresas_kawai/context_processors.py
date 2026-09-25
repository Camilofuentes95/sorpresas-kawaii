from django.db.models import Sum
from .models import ItemCarrito


def carrito_context(request):
    """
    Context processor para suministrar la cantidad total de artículos
    en el carrito a todas las plantillas y vistas del sistema.
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
    Suministra la configuración global de la tienda (activación de checkout,
    módulo de sorpresas, combos y mensajes de mantenimiento) a todos los templates.
    """
    try:
        from .models import ConfiguracionTienda
        config = ConfiguracionTienda.get_solo()
    except Exception:
        config = None

    return {
        'config_tienda': config,
    }

