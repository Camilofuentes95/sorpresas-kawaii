"""
Procesadores de Contexto Globales - Sorpresas Kawaii.

Inyectan variables globales en el contexto de renderizado de todas las plantillas HTML:
- Conteo en tiempo real de articulos en el carrito de compras.
- Parametros globales de disponibilidad de la tienda (ConfiguracionTienda).
- Estado global de Lista de Deseos / Favoritos.
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


def fidelizacion_y_deseos_context(request):
    """
    Inyecta datos globales de la lista de deseos:
    - deseos_total_items: cantidad de articulos favoritos guardados.
    - deseos_producto_ids: conjunto de IDs de productos guardados para pintar corazones activos en catalogos.
    - deseos_combo_ids: conjunto de IDs de combos guardados en favoritos.
    """
    deseos_total = 0
    deseos_producto_ids = set()
    deseos_combo_ids = set()

    if request.user.is_authenticated:
        try:
            from .models import ListaDeseos
            items_deseos = ListaDeseos.objects.filter(usuario=request.user).values('producto_id', 'combo_id')
            deseos_total = len(items_deseos)
            for d in items_deseos:
                if d['producto_id']:
                    deseos_producto_ids.add(str(d['producto_id']))
                if d['combo_id']:
                    deseos_combo_ids.add(str(d['combo_id']))
        except Exception:
            pass

    return {
        'deseos_total_items': deseos_total,
        'deseos_producto_ids': deseos_producto_ids,
        'deseos_combo_ids': deseos_combo_ids,
    }
