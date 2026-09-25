from django.contrib import admin
from .models import (
    Categoria, Producto, Combo, CombosProductos,
    Pedido, DetallePedido, UserProfile, CarritoDeCompras, ItemCarrito,
    ConfiguracionTienda, Sorpresa
)

admin.site.register(Categoria)
admin.site.register(CombosProductos)
admin.site.register(UserProfile)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'id_categoria', 'valor_unitario', 'descuento_porcentaje', 'stock', 'es_nuevo', 'activo', 'id')
    list_filter = ('activo', 'es_nuevo', 'id_categoria')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('valor_unitario', 'descuento_porcentaje', 'stock', 'es_nuevo', 'activo')
    ordering = ('nombre',)
    actions = ['enviar_alerta_stock_email_action']
    fieldsets = (
        ('Información General', {
            'fields': ('nombre', 'descripcion', 'id_categoria', 'imagen', 'imagen_url'),
            'description': 'Puedes subir una imagen desde tu computador o indicar un enlace URL.'
        }),
        ('Datos de Inventario, Precio y Descuento', {
            'fields': ('valor_unitario', 'descuento_porcentaje', 'stock', 'es_nuevo', 'activo'),
        }),
    )

    @admin.action(description="📧 Enviar alerta de stock por correo de los seleccionados")
    def enviar_alerta_stock_email_action(self, request, queryset):
        from django.contrib import messages
        from .emails import enviar_correo_alerta_stock_bajo
        enviado = enviar_correo_alerta_stock_bajo(list(queryset), motivo="Selección manual en Django Admin")
        if enviado:
            self.message_user(request, f"📧 Se envió la alerta de correo para {queryset.count()} producto(s) exitosamente.", level=messages.SUCCESS)
        else:
            self.message_user(request, "No se pudo enviar el correo de alerta. Verifica la configuración de ADMIN_EMAIL.", level=messages.WARNING)


@admin.register(Sorpresa)
class SorpresaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'valor_unitario', 'descuento_porcentaje', 'stock', 'es_nuevo', 'activo')
    list_filter = ('activo', 'es_nuevo')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('valor_unitario', 'descuento_porcentaje', 'stock', 'es_nuevo', 'activo')
    ordering = ('nombre',)
    actions = ['enviar_alerta_stock_email_action']
    fieldsets = (
        ('Información de la Experiencia / Sorpresa', {
            'fields': ('nombre', 'descripcion', 'imagen', 'imagen_url'),
            'description': 'Configura el nombre (ej: Lucky Pop, Scoop Normal), descripción e imagen de la máquina o experiencia.'
        }),
        ('Precio, Inventario y Promociones', {
            'fields': ('valor_unitario', 'descuento_porcentaje', 'stock', 'es_nuevo', 'activo'),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(id_categoria__nombre__iexact='Sorpresa')

    def save_model(self, request, obj, form, change):
        if not obj.id_categoria or obj.id_categoria.nombre.lower() != 'sorpresa':
            cat_sorpresa, _ = Categoria.objects.get_or_create(nombre='Sorpresa')
            obj.id_categoria = cat_sorpresa
        super().save_model(request, obj, form, change)

    @admin.action(description="📧 Enviar alerta de stock por correo de las sorpresas seleccionadas")
    def enviar_alerta_stock_email_action(self, request, queryset):
        from django.contrib import messages
        from .emails import enviar_correo_alerta_stock_bajo
        enviado = enviar_correo_alerta_stock_bajo(list(queryset), motivo="Selección manual en Django Admin")
        if enviado:
            self.message_user(request, f"📧 Se envió la alerta de correo para {queryset.count()} experiencia(s) exitosamente.", level=messages.SUCCESS)
        else:
            self.message_user(request, "No se pudo enviar el correo de alerta. Verifica la configuración de ADMIN_EMAIL.", level=messages.WARNING)



class CombosProductosInline(admin.TabularInline):
    """Permite editar los productos dentro del formulario de Combo"""
    model = Combo.productos.through
    extra = 0


@admin.register(Combo)
class ComboAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'valor_combo', 'descuento_porcentaje', 'valido_hasta', 'es_nuevo', 'activo')
    search_fields = ('nombre', 'descripcion', 'usuario_id__username')
    list_filter = ('activo', 'es_nuevo', 'valido_hasta')
    list_editable = ('valor_combo', 'descuento_porcentaje', 'es_nuevo', 'activo')
    ordering = ('nombre',)
    inlines = [CombosProductosInline]
    exclude = ('productos',)
    fieldsets = (
        ('Información del combo', {
            'fields': ('nombre', 'descripcion', 'imagen', 'imagen_url', 'es_nuevo', 'activo'),
            'description': 'Puedes subir una imagen desde tu computador o indicar un enlace URL.'
        }),
        ('Precio y vigencia', {
            'fields': ('valor_combo', 'descuento_porcentaje', 'valido_hasta'),
        }),
        ('Información adicional', {
            'fields': ('usuario_id', 'numero_productos'),
        }),
    )


class DetallePedidoInline(admin.TabularInline):
    """Muestra los productos y combos incluidos en el pedido."""
    model = DetallePedido
    extra = 0
    readonly_fields = ('producto', 'combo', 'cantidad', 'precio_item')


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    change_list_template = 'admin/sorpresas_kawai/pedido/change_list.html'
    list_display = ('id_corto', 'id_usuario', 'fecha_pedido', 'valor_pagado', 'estado', 'empresa_envio', 'numero_guia', 'tiene_comprobante')
    list_editable = ('estado', 'empresa_envio', 'numero_guia')
    list_filter = ('estado', 'fecha_pedido')
    search_fields = ('id', 'id_usuario__username', 'id_usuario__email', 'numero_guia', 'empresa_envio')
    ordering = ('-fecha_pedido',)
    inlines = [DetallePedidoInline]
    actions = ['exportar_pedidos_seleccionados_excel']
    fieldsets = (
        ('Información del Pedido', {
            'fields': ('id_usuario', 'estado', 'valor_pagado', 'metodo_pago', 'detalle_pago'),
        }),
        ('Comprobante de Pago', {
            'fields': ('comprobante_pago',),
            'description': 'Sube la imagen o foto del comprobante de transferencia / pago de la orden.'
        }),
        ('Información de Envío y Guía', {
            'fields': ('empresa_envio', 'numero_guia'),
            'description': 'Completa estos campos cuando el pedido esté enviado para que el cliente pueda ver su guía en "Mis Pedidos".'
        }),
    )

    def id_corto(self, obj):
        return obj.codigo_pedido
    id_corto.short_description = "N° Pedido"

    def tiene_comprobante(self, obj):
        return bool(obj.comprobante_pago)
    tiene_comprobante.boolean = True
    tiene_comprobante.short_description = "Comprobante"

    @admin.action(description="📥 Descargar pedidos seleccionados en Excel (.xlsx)")
    def exportar_pedidos_seleccionados_excel(self, request, queryset):
        from django.db.models import Sum
        from .exportar_excel import generar_excel_metricas_ventas
        from .models import DetallePedido, Producto

        pedidos_qs = queryset.select_related('id_usuario').order_by('-fecha_pedido')
        total_pedidos = pedidos_qs.count()
        pedidos_pagados = pedidos_qs.filter(estado__in=['PAGADO', 'ENVIADO', 'ENTREGADO']).count()
        pedidos_pendientes = pedidos_qs.filter(estado='PENDIENTE').count()
        pedidos_cancelados = pedidos_qs.filter(estado='CANCELADO').count()

        ingresos_confirmados = pedidos_qs.filter(
            estado__in=['PAGADO', 'ENVIADO', 'ENTREGADO']
        ).aggregate(total=Sum('valor_pagado'))['total'] or 0.0

        ingresos_totales = pedidos_qs.aggregate(total=Sum('valor_pagado'))['total'] or 0.0
        ticket_promedio = (ingresos_confirmados / pedidos_pagados) if pedidos_pagados > 0 else 0.0

        detalles_prod = DetallePedido.objects.filter(
            pedido__in=pedidos_qs,
            producto__isnull=False
        ).select_related('producto', 'producto__id_categoria')

        prod_map = {}
        for d in detalles_prod:
            p = d.producto
            pid = str(p.id)
            if pid not in prod_map:
                prod_map[pid] = {
                    'id': p.id,
                    'nombre': p.nombre,
                    'categoria': p.id_categoria.nombre if p.id_categoria else 'Sin Categoría',
                    'valor_unitario': p.valor_unitario,
                    'stock': p.stock,
                    'unidades_vendidas': 0,
                    'ingresos_generados': 0.0,
                }
            prod_map[pid]['unidades_vendidas'] += d.cantidad
            prod_map[pid]['ingresos_generados'] += (d.cantidad * d.precio_item)

        productos_metricas = list(prod_map.values())
        productos_metricas.sort(key=lambda x: x['unidades_vendidas'], reverse=True)

        detalles_combos = DetallePedido.objects.filter(
            pedido__in=pedidos_qs,
            combo__isnull=False
        ).select_related('combo')

        combo_map = {}
        for d in detalles_combos:
            c = d.combo
            cid = str(c.id)
            if cid not in combo_map:
                combo_map[cid] = {
                    'id': c.id,
                    'nombre': c.nombre,
                    'valor_combo': c.valor_combo,
                    'activo': c.activo,
                    'unidades_vendidas': 0,
                    'ingresos_generados': 0.0,
                }
            combo_map[cid]['unidades_vendidas'] += d.cantidad
            combo_map[cid]['ingresos_generados'] += (d.cantidad * d.precio_item)

        combos_metricas = list(combo_map.values())
        combos_metricas.sort(key=lambda x: x['unidades_vendidas'], reverse=True)

        alertas_stock = Producto.objects.filter(activo=True, stock__lte=5).select_related('id_categoria').order_by('stock')

        resumen_data = {
            'ingresos_confirmados': ingresos_confirmados,
            'ingresos_totales': ingresos_totales,
            'total_pedidos': total_pedidos,
            'pedidos_pagados': pedidos_pagados,
            'pedidos_pendientes': pedidos_pendientes,
            'pedidos_cancelados': pedidos_cancelados,
            'ticket_promedio': ticket_promedio,
            'unidades_productos_vendidas': sum(p['unidades_vendidas'] for p in productos_metricas),
            'unidades_combos_vendidas': sum(c['unidades_vendidas'] for c in combos_metricas),
            'productos_alerta_stock': alertas_stock.count(),
        }

        return generar_excel_metricas_ventas(
            pedidos_qs=pedidos_qs,
            resumen_data=resumen_data,
            productos_metricas=productos_metricas,
            combos_metricas=combos_metricas,
            alertas_stock=alertas_stock,
            usuario_generador=request.user.username,
            rango_etiqueta=f"Selección en Panel Admin ({total_pedidos} pedidos)",
            estado_etiqueta="Filtro manual de selección"
        )


class ItemCarritoInline(admin.TabularInline):
    """
    Define cómo se mostrarán los ItemsCarrito dentro de CarritoDeCompras.
    """
    model = ItemCarrito
    fields = ('producto', 'combo', 'cantidad', 'fecha_agregado')
    readonly_fields = ('fecha_agregado',)
    extra = 1


@admin.register(CarritoDeCompras)
class CarritoDeComprasAdmin(admin.ModelAdmin):
    """
    Configuración para mostrar la información del Carrito.
    """
    list_display = ('usuario', 'fecha_creacion', 'contar_productos')
    search_fields = ('usuario__username', 'usuario__first_name')
    inlines = [ItemCarritoInline]
    def contar_productos(self, obj):
        return obj.items.count()
    contar_productos.short_description = "N° de Productos"


from .models import ConfiguracionTienda

@admin.register(ConfiguracionTienda)
class ConfiguracionTiendaAdmin(admin.ModelAdmin):
    """
    Panel administrativo singleton para gestionar la activación de módulos,
    configuración de envíos y mensajes de mantenimiento en la tienda.
    """
    fieldsets = (
        ('🚚 Configuración de Envíos y Domicilios', {
            'fields': ('monto_minimo_envio_gratis', 'costo_envio_estandar'),
            'description': 'Configura el monto mínimo de compra para Envío Gratis y el costo del flete estándar.'
        }),
        ('🛒 Proceso de Checkout y Compras', {
            'fields': ('compras_habilitadas', 'mensaje_mantenimiento_compras'),
            'description': 'Controla si los clientes pueden finalizar compras desde el carrito.'
        }),
        ('🛍️ Catálogo de Productos', {
            'fields': ('modulo_productos_habilitado', 'mensaje_mantenimiento_productos'),
            'description': 'Activa o pausa la página y catálogo general de productos.'
        }),
        ('🎁 Sección de Sorpresas', {
            'fields': ('modulo_sorpresas_habilitado', 'mensaje_mantenimiento_sorpresas'),
            'description': 'Activa o pausa la página y experiencia de scoops sorpresa.'
        }),
        ('🍱 Sección de Combos', {
            'fields': ('modulo_combos_habilitado', 'mensaje_mantenimiento_combos'),
            'description': 'Activa o pausa la página y catálogo de combos.'
        }),
    )

    def has_add_permission(self, request):
        # Solo permite agregar si no existe la instancia singleton
        return not ConfiguracionTienda.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Evita borrar la configuración principal
        return False

