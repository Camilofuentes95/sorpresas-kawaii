from datetime import datetime, time, timedelta
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from django.http import HttpResponseForbidden

from .models import Pedido, DetallePedido, Producto, Combo, Categoria
from .exportar_excel import generar_excel_metricas_ventas


def obtener_datos_metricas(request):
    """
    Función utilitaria que procesa los filtros por fecha, estado y categoría,
    y calcula todos los agregados cuantitativos de ventas, inventario y KPIs.
    """
    rango = request.GET.get('rango', 'mes')
    fecha_inicio_str = request.GET.get('fecha_inicio', '').strip()
    fecha_fin_str = request.GET.get('fecha_fin', '').strip()
    estado_filtro = request.GET.get('estado', 'CONFIRMADOS')
    categoria_filtro = request.GET.get('categoria', 'all')

    ahora = timezone.localtime(timezone.now())
    hoy = ahora.date()
    
    fecha_desde = None
    fecha_hasta = ahora

    rango_etiqueta = "Este Mes"

    if rango == 'hoy':
        fecha_desde = timezone.make_aware(datetime.combine(hoy, time.min))
        fecha_hasta = timezone.make_aware(datetime.combine(hoy, time.max))
        rango_etiqueta = f"Hoy ({hoy.strftime('%d/%m/%Y')})"
    elif rango == '7dias':
        fecha_desde = ahora - timedelta(days=7)
        rango_etiqueta = "Últimos 7 Días"
    elif rango == 'mes':
        primer_dia_mes = hoy.replace(day=1)
        fecha_desde = timezone.make_aware(datetime.combine(primer_dia_mes, time.min))
        rango_etiqueta = f"Este Mes ({hoy.strftime('%B %Y')})"
    elif rango == '30dias':
        fecha_desde = ahora - timedelta(days=30)
        rango_etiqueta = "Últimos 30 Días"
    elif rango == 'anio':
        primer_dia_anio = hoy.replace(month=1, day=1)
        fecha_desde = timezone.make_aware(datetime.combine(primer_dia_anio, time.min))
        rango_etiqueta = f"Este Año ({hoy.year})"
    elif rango == 'todo':
        fecha_desde = None
        rango_etiqueta = "Histórico Completo (Todo el tiempo)"
    elif rango == 'personalizado':
        rango_etiqueta = "Rango Personalizado"
        if fecha_inicio_str:
            try:
                d_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
                fecha_desde = timezone.make_aware(datetime.combine(d_inicio, time.min))
            except ValueError:
                pass
        if fecha_fin_str:
            try:
                d_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
                fecha_hasta = timezone.make_aware(datetime.combine(d_fin, time.max))
            except ValueError:
                pass
        if fecha_desde and fecha_hasta:
            rango_etiqueta = f"Del {fecha_desde.strftime('%d/%m/%Y')} al {fecha_hasta.strftime('%d/%m/%Y')}"

    # Query base de pedidos
    pedidos_base = Pedido.objects.all().select_related('id_usuario')

    if fecha_desde:
        pedidos_base = pedidos_base.filter(fecha_pedido__gte=fecha_desde)
    if fecha_hasta:
        pedidos_base = pedidos_base.filter(fecha_pedido__lte=fecha_hasta)

    # Filtrado por estado
    estado_etiqueta = "Confirmados (Pagados / Enviados / Entregados)"
    pedidos_filtrados = pedidos_base

    if estado_filtro == 'CONFIRMADOS':
        pedidos_filtrados = pedidos_base.filter(estado__in=['PAGADO', 'ENVIADO', 'ENTREGADO'])
        estado_etiqueta = "Pedidos Confirmados (Pagado, Enviado, Entregado)"
    elif estado_filtro == 'TODOS':
        pedidos_filtrados = pedidos_base
        estado_etiqueta = "Todos los Estados"
    elif estado_filtro in dict(Pedido.ESTADOS):
        pedidos_filtrados = pedidos_base.filter(estado=estado_filtro)
        estado_etiqueta = dict(Pedido.ESTADOS).get(estado_filtro, estado_filtro)

    # KPIs Generales sobre el período seleccionado
    total_pedidos_periodo = pedidos_base.count()
    pedidos_pagados_count = pedidos_base.filter(estado__in=['PAGADO', 'ENVIADO', 'ENTREGADO']).count()
    pedidos_pendientes_count = pedidos_base.filter(estado='PENDIENTE').count()
    pedidos_cancelados_count = pedidos_base.filter(estado='CANCELADO').count()

    ingresos_confirmados = pedidos_base.filter(
        estado__in=['PAGADO', 'ENVIADO', 'ENTREGADO']
    ).aggregate(total=Sum('valor_pagado'))['total'] or 0.0

    ingresos_totales_brutos = pedidos_base.aggregate(total=Sum('valor_pagado'))['total'] or 0.0

    ticket_promedio = (ingresos_confirmados / pedidos_pagados_count) if pedidos_pagados_count > 0 else 0.0
    tasa_conversion = ((pedidos_pagados_count / total_pedidos_periodo) * 100) if total_pedidos_periodo > 0 else 0.0

    # -------------------------------------------------------------
    # Detalle de Ventas por Producto
    # -------------------------------------------------------------
    detalles_prod = DetallePedido.objects.filter(
        pedido__in=pedidos_filtrados,
        producto__isnull=False
    ).select_related('producto', 'producto__id_categoria')

    if categoria_filtro != 'all':
        detalles_prod = detalles_prod.filter(producto__id_categoria_id=categoria_filtro)

    # Agrupar productos
    prod_map = {}
    for d in detalles_prod:
        p = d.producto
        pid = str(p.id)
        if pid not in prod_map:
            prod_map[pid] = {
                'id': p.id,
                'nombre': p.nombre,
                'categoria': p.id_categoria.nombre if p.id_categoria else 'Sin Categoría',
                'categoria_id': str(p.id_categoria.id) if p.id_categoria else None,
                'valor_unitario': p.valor_unitario,
                'stock': p.stock,
                'unidades_vendidas': 0,
                'ingresos_generados': 0.0,
                'imagen_url': p.get_imagen_url,
            }
        prod_map[pid]['unidades_vendidas'] += d.cantidad
        prod_map[pid]['ingresos_generados'] += (d.cantidad * d.precio_item)

    # Contemplar pedidos antiguos directos (id_producto_opcional)
    pedidos_prod_directo = pedidos_filtrados.filter(id_producto_opcional__isnull=False)
    for p_dir in pedidos_prod_directo:
        p = p_dir.id_producto_opcional
        pid = str(p.id)
        if pid not in prod_map:
            prod_map[pid] = {
                'id': p.id,
                'nombre': p.nombre,
                'categoria': p.id_categoria.nombre if p.id_categoria else 'Sin Categoría',
                'categoria_id': str(p.id_categoria.id) if p.id_categoria else None,
                'valor_unitario': p.valor_unitario,
                'stock': p.stock,
                'unidades_vendidas': 0,
                'ingresos_generados': 0.0,
                'imagen_url': p.get_imagen_url,
            }
        prod_map[pid]['unidades_vendidas'] += 1
        prod_map[pid]['ingresos_generados'] += p_dir.valor_pagado

    productos_metricas = list(prod_map.values())
    productos_metricas.sort(key=lambda x: (x['unidades_vendidas'], x['ingresos_generados']), reverse=True)

    total_unidades_productos = sum(p['unidades_vendidas'] for p in productos_metricas)

    # -------------------------------------------------------------
    # Detalle de Ventas por Combo
    # -------------------------------------------------------------
    detalles_combos = DetallePedido.objects.filter(
        pedido__in=pedidos_filtrados,
        combo__isnull=False
    ).select_related('combo')

    combo_map = {}
    for d in detalles_combos:
        c = d.combo
        cid = str(c.id)
        if cid not in combo_map:
            combo_map[cid] = {
                'id': c.id,
                'nombre': c.nombre or f"Combo {c.id}",
                'valor_combo': c.valor_combo,
                'activo': c.activo,
                'unidades_vendidas': 0,
                'ingresos_generados': 0.0,
                'imagen_url': c.get_imagen_url,
            }
        combo_map[cid]['unidades_vendidas'] += d.cantidad
        combo_map[cid]['ingresos_generados'] += (d.cantidad * d.precio_item)

    # Pedidos antiguos directos (combo_opcional)
    pedidos_combo_directo = pedidos_filtrados.filter(combo_opcional__isnull=False)
    for c_dir in pedidos_combo_directo:
        c = c_dir.combo_opcional
        cid = str(c.id)
        if cid not in combo_map:
            combo_map[cid] = {
                'id': c.id,
                'nombre': c.nombre or f"Combo {c.id}",
                'valor_combo': c.valor_combo,
                'activo': c.activo,
                'unidades_vendidas': 0,
                'ingresos_generados': 0.0,
                'imagen_url': c.get_imagen_url,
            }
        combo_map[cid]['unidades_vendidas'] += 1
        combo_map[cid]['ingresos_generados'] += c_dir.valor_pagado

    combos_metricas = list(combo_map.values())
    combos_metricas.sort(key=lambda x: (x['unidades_vendidas'], x['ingresos_generados']), reverse=True)

    total_unidades_combos = sum(c['unidades_vendidas'] for c in combos_metricas)

    # -------------------------------------------------------------
    # Ventas por Categoría
    # -------------------------------------------------------------
    categoria_ventas = {}
    for item in productos_metricas:
        cat_nom = item['categoria']
        if cat_nom not in categoria_ventas:
            categoria_ventas[cat_nom] = {'categoria': cat_nom, 'unidades': 0, 'ingresos': 0.0}
        categoria_ventas[cat_nom]['unidades'] += item['unidades_vendidas']
        categoria_ventas[cat_nom]['ingresos'] += item['ingresos_generados']

    categorias_lista = list(categoria_ventas.values())
    categorias_lista.sort(key=lambda x: x['ingresos'], reverse=True)

    # -------------------------------------------------------------
    # Alertas de Inventario / Stock Bajo
    # -------------------------------------------------------------
    alertas_stock = Producto.objects.filter(
        activo=True,
        stock__lte=5
    ).select_related('id_categoria').order_by('stock', 'nombre')

    productos_alerta_stock_count = alertas_stock.count()

    # -------------------------------------------------------------
    # Datos para Gráfica de Tendencia Diaria (Últimos 14 días o días del rango)
    # -------------------------------------------------------------
    # Generar agrupamiento diario sobre pedidos_filtrados
    pedidos_para_grafico = pedidos_filtrados.order_by('fecha_pedido')
    fechas_map = {}
    
    for p in pedidos_para_grafico:
        f_str = p.fecha_pedido.strftime("%d/%m") if p.fecha_pedido else "N/A"
        if f_str not in fechas_map:
            fechas_map[f_str] = {'fecha': f_str, 'ingresos': 0.0, 'pedidos': 0}
        fechas_map[f_str]['ingresos'] += p.valor_pagado
        fechas_map[f_str]['pedidos'] += 1

    chart_labels = list(fechas_map.keys())
    chart_ingresos = [fechas_map[k]['ingresos'] for k in chart_labels]
    chart_pedidos = [fechas_map[k]['pedidos'] for k in chart_labels]

    # Resumen empaquetado
    resumen_data = {
        'ingresos_confirmados': ingresos_confirmados,
        'ingresos_totales': ingresos_totales_brutos,
        'total_pedidos': total_pedidos_periodo,
        'pedidos_pagados': pedidos_pagados_count,
        'pedidos_pendientes': pedidos_pendientes_count,
        'pedidos_cancelados': pedidos_cancelados_count,
        'ticket_promedio': ticket_promedio,
        'tasa_conversion': round(tasa_conversion, 1),
        'unidades_productos_vendidas': total_unidades_productos,
        'unidades_combos_vendidas': total_unidades_combos,
        'productos_alerta_stock': productos_alerta_stock_count,
    }

    return {
        'rango': rango,
        'fecha_inicio': fecha_inicio_str,
        'fecha_fin': fecha_fin_str,
        'estado_filtro': estado_filtro,
        'categoria_filtro': categoria_filtro,
        'rango_etiqueta': rango_etiqueta,
        'estado_etiqueta': estado_etiqueta,
        'pedidos_qs': pedidos_filtrados.order_by('-fecha_pedido'),
        'resumen': resumen_data,
        'productos_metricas': productos_metricas,
        'combos_metricas': combos_metricas,
        'categorias_ventas': categorias_lista,
        'alertas_stock': alertas_stock,
        'chart_labels': chart_labels,
        'chart_ingresos': chart_ingresos,
        'chart_pedidos': chart_pedidos,
        'todas_categorias': Categoria.objects.all().order_by('nombre'),
    }


def es_staff_check(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(es_staff_check, login_url='/login/')
def metricas_ventas_dashboard(request):
    """
    Vista del Dashboard de Métricas y Analítica de Ventas en el Panel de Administración.
    Solo accesible para usuarios administradores / staff (PO de Costos / PO de Catálogo / Admin).
    """
    datos = obtener_datos_metricas(request)
    
    contexto = {
        'title': 'Métricas y Reportes de Ventas',
        'has_permission': True,
        'site_title': 'Sorpresas Kawaii Admin',
        'site_header': 'Sorpresas Kawaii - Panel de Gestión',
        **datos,
    }
    return render(request, 'admin/metricas_ventas.html', contexto)


@user_passes_test(es_staff_check, login_url='/login/')
def exportar_metricas_excel(request):
    """
    Descarga el reporte de métricas y ventas en formato Microsoft Excel (.xlsx).
    Solo accesible para usuarios staff y administradores.
    """
    datos = obtener_datos_metricas(request)
    
    return generar_excel_metricas_ventas(
        pedidos_qs=datos['pedidos_qs'],
        resumen_data=datos['resumen'],
        productos_metricas=datos['productos_metricas'],
        combos_metricas=datos['combos_metricas'],
        alertas_stock=datos['alertas_stock'],
        usuario_generador=request.user.username,
        rango_etiqueta=datos['rango_etiqueta'],
        estado_etiqueta=datos['estado_etiqueta']
    )


@user_passes_test(es_staff_check, login_url='/login/')
def enviar_alerta_stock_email_manual(request):
    """
    Dispara manualmente el envío del correo de alerta de inventario bajo
    con todos los productos que actualmente tienen stock <= 5 unidades o agotados.
    """
    from django.contrib import messages
    from .emails import enviar_correo_alerta_stock_bajo
    
    alertas_stock = Producto.objects.filter(
        activo=True,
        stock__lte=5
    ).select_related('id_categoria').order_by('stock', 'nombre')
    
    if not alertas_stock.exists():
        messages.info(request, "¡Excelente! En este momento no hay productos con existencias bajas o agotadas.")
    else:
        enviado = enviar_correo_alerta_stock_bajo(list(alertas_stock), motivo="Solicitud Manual desde Panel")
        if enviado:
            messages.success(request, f"📧 ¡Alerta enviada exitosamente! Se notificó al correo sobre {alertas_stock.count()} producto(s) en alerta.")
        else:
            messages.warning(request, "No se pudo despachar el correo (verifica la configuración de ADMIN_EMAIL en el servidor).")
            
    return redirect(request.META.get('HTTP_REFERER', 'admin_metricas_ventas'))
