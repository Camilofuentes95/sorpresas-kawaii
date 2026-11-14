"""
Modulo de Vistas y Controladores - Sorpresas Kawaii.

Gestiona el flujo transaccional y la presentacion de la tienda en linea:
- Autenticacion de usuarios (login, registro seguro con validacion de politicas de contrasenas, logout).
- Navegacion y visualizacion de catalogos (inicio, catalogo general, combos y experiencias sorpresa).
- Administracion del carrito de compras (alta, baja, persistencia y calculo dinamico de fletes).
- Procesamiento de ordenes de compra con transacciones atomicas y actualizacion de inventario.
- Seguimiento post-venta y confirmacion con enlace preformateado a WhatsApp.
"""

import random
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.db import transaction, IntegrityError
from django.db.models import Count
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings

from .models import (
    Categoria, Producto, Combo, Pedido,
    DetallePedido, CarritoDeCompras, ItemCarrito,
    ConfiguracionTienda,
    ListaDeseos, Resena
)
from .metricas_views import (
    metricas_ventas_dashboard,
    exportar_metricas_excel,
    enviar_alerta_stock_email_manual
)

# Etiquetas textuales e iconografia de interfaz para destacar productos en portada
PRODUCT_BADGES = [
    {'icon': 'fa-solid fa-fire', 'text': 'Top Venta'},
    {'icon': 'fa-solid fa-star', 'text': 'Favorito'},
    {'icon': 'fa-solid fa-sparkles', 'text': 'Especial'},
    {'icon': 'fa-solid fa-heart', 'text': 'Mas Amado'},
    {'icon': 'fa-solid fa-bolt', 'text': 'Tendencia'},
    {'icon': 'fa-solid fa-crown', 'text': 'Imperdible'},
    {'icon': 'fa-solid fa-wand-magic-sparkles', 'text': 'Destacado'},
]

# Etiquetas textuales e iconografia de interfaz para destacar combos en portada
COMBO_BADGES = [
    {'icon': 'fa-solid fa-wand-magic-sparkles', 'text': 'Top Combo'},
    {'icon': 'fa-solid fa-crown', 'text': 'Combo Estrella'},
    {'icon': 'fa-solid fa-gift', 'text': 'Super Combo'},
    {'icon': 'fa-solid fa-gem', 'text': 'Combo Exclusivo'},
    {'icon': 'fa-solid fa-star', 'text': 'Combo Favorito'},
]


class NuevaContrasenaForm(SetPasswordForm):
    """
    Formulario personalizado para la captura y confirmacion de la nueva clave
    en el flujo de recuperacion de contrasena.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'placeholder': 'Nueva contrasena',
            'id': 'new_password1',
        })
        self.fields['new_password2'].widget.attrs.update({
            'placeholder': 'Repetir contrasena',
            'id': 'new_password2',
        })


def logout_view(request):
    """
    Cierra la sesion activa del usuario y redirige a la pantalla de inicio de sesion.
    """
    logout(request)
    return redirect('/login/')


def login_view(request):
    """
    Autentica credenciales de usuario (username/password).
    Redirige a usuarios con rol administrativo (is_staff) al panel de Django Admin
    y a clientes regulares a la pagina de inicio.
    """
    error = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.is_staff:
                return redirect('/admin/')
            else:
                return redirect('inicio')
        else:
            error = 'Usuario o contrasena incorrectos.'

    return render(request, 'admin/logintest.html', {'error': error})


def register_view(request):
    """
    Registra nuevos clientes en el sistema.
    Aplica politicas de seguridad y privacidad:
    - Captura formal de nombre y apellido para proteger el correo en resenas publicas.
    - Verificacion de correo electronico valido.
    - Concordancia entre contrasena y confirmacion.
    - Cumplimiento de longitud y complejidad mediante AUTH_PASSWORD_VALIDATORS.
    - Control de unicidad de cuentas para evitar duplicidad de correos.
    """
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        contexto_error = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email
        }

        if not first_name or not last_name or not email or not password1 or not password2:
            messages.error(request, "Todos los campos (nombre, apellido, correo y contraseña) son obligatorios.")
            return render(request, 'admin/register.html', contexto_error)

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Por favor ingresa un correo electrónico válido.")
            return render(request, 'admin/register.html', contexto_error)

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, 'admin/register.html', contexto_error)

        try:
            validate_password(password1)
        except ValidationError as error:
            for msg in error.messages:
                messages.error(request, msg)
            return render(request, 'admin/register.html', contexto_error)

        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            messages.error(request, "Ya existe un usuario registrado con este correo electrónico.")
            return render(request, 'admin/register.html', contexto_error)

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )
        user.save()

        return render(request, 'admin/register.html', {'messages_success': True})

    return render(request, 'admin/register.html')


def inicio(request):
    """
    Renderiza la pagina principal del comercio electronico.
    Presenta articulos destacados al azar, combos en vitrina y el estado del carrito
    para el usuario autenticado.
    """
    if not Producto.objects.exists():
        from .seed_data import seed_database
        seed_database()

    # Seleccionar 3 productos activos para la seccion de destacados
    productos_query = Producto.objects.filter(activo=True).exclude(
        id_categoria__nombre__iexact='Sorpresa'
    )
    if productos_query.count() < 3:
        productos_query = Producto.objects.filter(activo=True)

    productos_destacados = list(productos_query.order_by('?')[:3])

    # Asignar etiquetas destacadas segun condicion de novedad o rotacion
    badges_disponibles = PRODUCT_BADGES.copy()
    random.shuffle(badges_disponibles)
    for idx, prod in enumerate(productos_destacados):
        if prod.es_nuevo:
            prod.badge_icon = 'fa-solid fa-sparkles'
            prod.badge_text = 'Novedad'
        else:
            badge = badges_disponibles[idx % len(badges_disponibles)]
            prod.badge_icon = badge['icon']
            prod.badge_text = badge['text']

    # Seleccionar 1 combo activo para destacar en vitrina
    combos_destacados = list(Combo.objects.filter(activo=True).order_by('?')[:1])
    if combos_destacados:
        if combos_destacados[0].es_nuevo:
            combos_destacados[0].badge_icon = 'fa-solid fa-wand-magic-sparkles'
            combos_destacados[0].badge_text = 'Nuevo Combo'
        else:
            combo_tag = random.choice(COMBO_BADGES)
            combos_destacados[0].badge_icon = combo_tag['icon']
            combos_destacados[0].badge_text = combo_tag['text']

    # Mapeo de articulos actualmente presentes en el carrito del cliente
    productos_en_carrito = {}
    combos_en_carrito = {}
    if request.user.is_authenticated:
        try:
            carrito = CarritoDeCompras.objects.get(usuario=request.user)
            items = ItemCarrito.objects.filter(carrito=carrito)
            for item in items:
                if item.producto:
                    productos_en_carrito[item.producto.id] = item.cantidad
                if item.combo:
                    combos_en_carrito[item.combo.id] = item.cantidad
        except CarritoDeCompras.DoesNotExist:
            pass

    contexto = {
        'productos_destacados': productos_destacados,
        'combos_destacados': combos_destacados,
        'productos_en_carrito': productos_en_carrito,
        'combos_en_carrito': combos_en_carrito,
    }
    return render(request, 'inicio.html', contexto)


def sobre_nosotros(request):
    """
    Renderiza la pagina institucional con historia, mision y canales de comunicacion.
    """
    return render(request, 'sobre_nosotros.html')


def lista_productos(request):
    """
    Despliega el catalogo interactivo general de productos.
    Permite filtrado por categorias, paginacion estructurada (12 items por pagina)
    y sincronizacion con el estado del carrito.
    """
    config = ConfiguracionTienda.get_solo()
    if not config.modulo_productos_habilitado:
        return render(
            request,
            "productos/lista.html",
            {
                "modulo_habilitado": False,
                "mensaje_mantenimiento": config.mensaje_mantenimiento_productos,
                "titulo": "Catalogo en Mantenimiento",
            }
        )

    if not Producto.objects.exists():
        from .seed_data import seed_database
        seed_database()

    categoria_slug = request.GET.get('categoria')

    productos_query = Producto.objects.filter(
        activo=True
    ).exclude(
        id_categoria__nombre__iexact='Sorpresa'
    ).order_by("nombre")

    if categoria_slug:
        productos_query = productos_query.filter(
            id_categoria__nombre__iexact=categoria_slug
        )

    paginator = Paginator(productos_query, 12)
    page_number = request.GET.get('page', 1)
    try:
        productos_paginados = paginator.page(page_number)
    except PageNotAnInteger:
        productos_paginados = paginator.page(1)
    except EmptyPage:
        productos_paginados = paginator.page(paginator.num_pages)

    categorias = Categoria.objects.filter(
        productos__activo=True
    ).exclude(
        nombre__iexact='Sorpresa'
    ).annotate(
        num_productos=Count('productos')
    ).order_by('nombre')

    productos_en_carrito = {}
    if request.user.is_authenticated:
        try:
            carrito = CarritoDeCompras.objects.get(usuario=request.user)
            items = ItemCarrito.objects.filter(
                carrito=carrito,
                producto__isnull=False
            )
            for item in items:
                productos_en_carrito[item.producto.id] = item.cantidad
        except CarritoDeCompras.DoesNotExist:
            pass

    contexto = {
        "modulo_habilitado": True,
        "productos": productos_paginados,
        "page_obj": productos_paginados,
        "categorias": categorias,
        "categoria_seleccionada": categoria_slug,
        "titulo": "Nuestra Coleccion de Productos",
        "productos_en_carrito": productos_en_carrito,
    }

    return render(request, "productos/lista.html", contexto)


def lista_sorpresas(request):
    """
    Despliega la seccion especializada de experiencias de compra aleatorias (Mystery Boxes, Scoops).
    """
    config = ConfiguracionTienda.get_solo()
    if not config.modulo_sorpresas_habilitado:
        return render(request, 'productos/sorpresas.html', {
            'modulo_habilitado': False,
            'mensaje_mantenimiento': config.mensaje_mantenimiento_sorpresas,
        })

    if not Producto.objects.exists():
        from .seed_data import seed_database
        seed_database()

    sorpresas_qs = Producto.objects.filter(
        id_categoria__nombre__iexact='Sorpresa',
        activo=True,
    ).order_by('valor_unitario')

    carrito_cantidades = {}
    if request.user.is_authenticated:
        items = ItemCarrito.objects.filter(
            carrito__usuario=request.user,
            producto__in=sorpresas_qs
        ).values('producto_id', 'cantidad')
        for item in items:
            carrito_cantidades[item['producto_id']] = item['cantidad']

    sorpresas = []
    for s in sorpresas_qs:
        s.cant_carrito = carrito_cantidades.get(s.id, 0)
        sorpresas.append(s)

    scoop_normal = sorpresas_qs.filter(nombre='Scoop Normal').first()
    cantidad_en_carrito = carrito_cantidades.get(scoop_normal.id, 0) if scoop_normal else 0

    return render(request, 'productos/sorpresas.html', {
        'modulo_habilitado': True,
        'sorpresas': sorpresas,
        'scoop_normal': scoop_normal,
        'cantidad_en_carrito': cantidad_en_carrito,
    })


def lista_combos(request):
    """
    Despliega la coleccion de paquetes promocionales (Combos), mostrando los productos
    que integra cada kit, descuentos porcentuales y cantidades en carrito.
    """
    config = ConfiguracionTienda.get_solo()
    if not config.modulo_combos_habilitado:
        return render(
            request,
            "productos/combos.html",
            {
                "modulo_habilitado": False,
                "mensaje_mantenimiento": config.mensaje_mantenimiento_combos,
                "titulo": "Combos en Mantenimiento",
            }
        )

    if not Producto.objects.exists():
        from .seed_data import seed_database
        seed_database()

    combos = Combo.objects.filter(activo=True).order_by('nombre')

    combos_en_carrito = {}
    if request.user.is_authenticated:
        try:
            carrito = CarritoDeCompras.objects.get(usuario=request.user)
            items = ItemCarrito.objects.filter(
                carrito=carrito,
                combo__isnull=False
            )
            for item in items:
                combos_en_carrito[item.combo.id] = item.cantidad
        except CarritoDeCompras.DoesNotExist:
            pass

    for combo in combos:
        productos_lista = [
            f"{cp.cantidad}x {cp.producto.nombre}"
            for cp in combo.combosproductos_set.all()
        ]
        combo.descripcion_productos = ", ".join(productos_lista) if productos_lista else None

    paginator = Paginator(combos, 12)
    page_number = request.GET.get('page', 1)
    try:
        combos_paginados = paginator.page(page_number)
    except PageNotAnInteger:
        combos_paginados = paginator.page(1)
    except EmptyPage:
        combos_paginados = paginator.page(paginator.num_pages)

    contexto = {
        "modulo_habilitado": True,
        "combos": combos_paginados,
        "page_obj": combos_paginados,
        "titulo": "Nuestra Coleccion de Combos",
        "combos_en_carrito": combos_en_carrito,
    }

    return render(request, "productos/combos.html", contexto)


@login_required
def agregar_a_carrito(request, producto_id):
    """
    Incrementa en una unidad la cantidad de un producto dentro del carrito del usuario.
    Requiere metodo POST para prevenir solicitudes no deseadas por peticiones GET prefetch.
    """
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id)
        carrito, _ = CarritoDeCompras.objects.get_or_create(usuario=request.user)
        item_carrito, item_creado = ItemCarrito.objects.get_or_create(
            carrito=carrito,
            producto=producto,
            defaults={'cantidad': 1}
        )
        if not item_creado:
            item_carrito.cantidad += 1
            item_carrito.save()

        return redirect(request.META.get('HTTP_REFERER', 'lista_productos'))

    return redirect('lista_productos')


@login_required
def quitar_de_carrito(request, producto_id):
    """
    Disminuye en una unidad la cantidad de un producto en el carrito o lo elimina
    si la cantidad previa era igual a uno.
    """
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id)
        try:
            carrito = CarritoDeCompras.objects.get(usuario=request.user)
            item_carrito = ItemCarrito.objects.get(carrito=carrito, producto=producto)
            if item_carrito.cantidad > 1:
                item_carrito.cantidad -= 1
                item_carrito.save()
            elif item_carrito.cantidad == 1:
                item_carrito.delete()
        except (CarritoDeCompras.DoesNotExist, ItemCarrito.DoesNotExist):
            pass

        return redirect(request.META.get('HTTP_REFERER', 'lista_productos'))

    return redirect('lista_productos')


def _manejar_item_carrito(request, combo_id, action='add'):
    """
    Funcion auxiliar interna para incorporar o decrementar combos dentro del carrito.
    """
    if request.method != 'POST':
        return redirect('lista_combos')

    combo = get_object_or_404(Combo, id=combo_id)
    carrito, _ = CarritoDeCompras.objects.get_or_create(usuario=request.user)

    item_carrito, _ = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        combo=combo,
        producto=None,
        defaults={'cantidad': 0}
    )

    if action == 'add':
        item_carrito.cantidad += 1
        item_carrito.save()
    elif action == 'remove':
        if item_carrito.cantidad > 1:
            item_carrito.cantidad -= 1
            item_carrito.save()
        else:
            item_carrito.delete()

    return redirect(request.META.get('HTTP_REFERER', 'lista_combos'))


@login_required
def agregar_combo_a_carrito(request, combo_id):
    """
    Endpoint de agregacion para combos promocionales.
    """
    return _manejar_item_carrito(request, combo_id, action='add')


@login_required
def quitar_combo_de_carrito(request, combo_id):
    """
    Endpoint de remocion o decremento para combos promocionales.
    """
    return _manejar_item_carrito(request, combo_id, action='remove')


@login_required
def ver_carrito(request):
    """
    Presenta la vista detallada de compra (checkout preliminar):
    - Relacion de articulos, cantidades y subtotales.
    - Evaluacion del umbral de envio gratis (monto_minimo_envio_gratis).
    - Calculo del flete y total general liquidado.
    """
    carrito = None
    items_carrito = []
    subtotal = 0
    total = 0
    config = ConfiguracionTienda.get_solo()
    monto_minimo_envio_gratis = config.monto_minimo_envio_gratis
    costo_envio = config.costo_envio_estandar

    try:
        carrito = CarritoDeCompras.objects.get(usuario=request.user)
        items_carrito = ItemCarrito.objects.filter(carrito=carrito).select_related('producto', 'combo')
        for item in items_carrito:
            item.precio_unitario = (
                item.producto.precio_final if item.producto else item.combo.precio_final
            )
            item.precio_total = item.cantidad * item.precio_unitario
            subtotal += item.precio_total

    except CarritoDeCompras.DoesNotExist:
        pass

    envio_gratis = subtotal >= monto_minimo_envio_gratis
    falta_para_envio_gratis = max(0, monto_minimo_envio_gratis - subtotal)

    if envio_gratis:
        costo_envio = 0

    if subtotal > 0:
        total = subtotal + costo_envio

    contexto = {
        'carrito': carrito,
        'items': items_carrito,
        'subtotal': subtotal,
        'costo_envio': costo_envio,
        'total': total,
        'monto_minimo_envio_gratis': monto_minimo_envio_gratis,
        'falta_para_envio_gratis': falta_para_envio_gratis,
        'envio_gratis': envio_gratis,
        'finalizar_compra_habilitado': config.compras_habilitadas,
        'mensaje_mantenimiento_compras': config.mensaje_mantenimiento_compras,
    }

    return render(request, 'carrito/detalle.html', contexto)


@login_required
def finalizar_compra(request):
    """
    Procesa formalmente la orden de compra bajo una transaccion atomica de base de datos:
    1. Verifica que las compras esten habilitadas globalmente.
    2. Consolida los articulos del carrito y calcula el total liquidado.
    3. Crea la orden principal (Pedido) y sus detalles (DetallePedido).
    4. Descuenta en tiempo real las existencias de stock del inventario.
    5. Dispara alertas por correo si el stock desciende a niveles criticos (<= 5 unidades).
    6. Despacha correos de confirmacion al comprador y notificacion a administracion.
    7. Vacia el carrito y redirige a la pantalla de confirmacion con boton WhatsApp.
    """
    config = ConfiguracionTienda.get_solo()
    if not config.compras_habilitadas:
        messages.warning(
            request,
            config.mensaje_mantenimiento_compras or "La opcion de finalizar compras no se encuentra disponible temporalmente."
        )
        return redirect('ver_carrito')

    if request.method == 'POST':
        try:
            with transaction.atomic():
                carrito = get_object_or_404(CarritoDeCompras, usuario=request.user)
                items_carrito = ItemCarrito.objects.filter(carrito=carrito).select_related('producto', 'combo')

                if not items_carrito.exists():
                    return redirect('ver_carrito')

                subtotal = 0
                for item in items_carrito:
                    precio_unitario = (
                        item.producto.precio_final if item.producto else item.combo.precio_final
                    )
                    subtotal += item.cantidad * precio_unitario

                costo_envio = 0 if subtotal >= config.monto_minimo_envio_gratis else config.costo_envio_estandar
                valor_total_pagado = subtotal + costo_envio

                nuevo_pedido = Pedido.objects.create(
                    id_usuario=request.user,
                    valor_pagado=valor_total_pagado,
                    estado='PENDIENTE',
                    metodo_pago='Coordinar por WhatsApp',
                )

                productos_alerta_stock = []

                for item in items_carrito:
                    precio_unitario = (
                        item.producto.precio_final if item.producto else item.combo.precio_final
                    )
                    DetallePedido.objects.create(
                        pedido=nuevo_pedido,
                        producto=item.producto,
                        combo=item.combo,
                        cantidad=item.cantidad,
                        precio_item=precio_unitario
                    )

                    # Descuento atómico de existencias físicas
                    if item.producto:
                        item.producto.stock = max(0, item.producto.stock - item.cantidad)
                        item.producto.save(update_fields=['stock'])
                        if item.producto.stock <= 5 and item.producto not in productos_alerta_stock:
                            productos_alerta_stock.append(item.producto)
                    elif item.combo:
                        for cp in item.combo.combosproductos_set.all():
                            p_combo = cp.producto
                            cant_descontar = cp.cantidad * item.cantidad
                            p_combo.stock = max(0, p_combo.stock - cant_descontar)
                            p_combo.save(update_fields=['stock'])
                            if p_combo.stock <= 5 and p_combo not in productos_alerta_stock:
                                productos_alerta_stock.append(p_combo)

                items_carrito.delete()

                # Notificaciones por correo electronico
                try:
                    from .emails import (
                        enviar_correo_confirmacion_compra,
                        enviar_correo_nuevo_pedido_administrador,
                        enviar_correo_alerta_stock_bajo
                    )
                    enviar_correo_confirmacion_compra(nuevo_pedido)
                    enviar_correo_nuevo_pedido_administrador(nuevo_pedido)
                    if productos_alerta_stock:
                        enviar_correo_alerta_stock_bajo(
                            productos_alerta_stock,
                            motivo="Compra Realizada",
                            pedido=nuevo_pedido
                        )
                except Exception:
                    pass

                return redirect('pagina_confirmacion', pedido_id=nuevo_pedido.id)

        except CarritoDeCompras.DoesNotExist:
            return redirect('lista_productos')
        except IntegrityError:
            return render(request, 'error_transaccion.html', {'mensaje': 'Ocurrio un error al procesar el pedido.'})

    return redirect('ver_carrito')


@login_required
def pagina_confirmacion(request, pedido_id):
    """
    Presenta la pantalla de exito de la compra.
    Muestra el codigo #SK-XXXXXX generado, el desglose de articulos y el enlace directo
    a la API de WhatsApp para coordinar pago y direccion de despacho.
    """
    pedido = get_object_or_404(
        Pedido.objects.prefetch_related('detalles__producto', 'detalles__combo'),
        id=pedido_id,
        id_usuario=request.user
    )
    contexto = {
        'pedido': pedido,
        'detalles': pedido.detalles.all()
    }
    return render(request, 'pedido/confirmacion.html', contexto)


@login_required
def mis_pedidos(request):
    """
    Muestra el historial cronologico de ordenes de compra efectuadas por el cliente autenticado,
    permitiendo consultar el estado logistico, transportadora y numero de guia de rastreo.
    """
    pedidos = Pedido.objects.filter(
        id_usuario=request.user
    ).order_by('-fecha_pedido').prefetch_related('detalles__producto', 'detalles__combo')

    return render(request, 'pedido/mis_pedidos.html', {'pedidos': pedidos})


# =============================================================================
# VISTAS DE RESEÑAS Y LISTA DE DESEOS
# =============================================================================

def detalle_producto(request, producto_id):
    """
    Despliega la ficha tecnica y comercial detallada del producto o sorpresa.
    Incluye:
    - Galeria y datos del articulo (precio unitario, descuento vigente, stock).
    - Estado de inclusion en carrito y lista de deseos.
    - Calificacion promedio y distribucion de valoraciones en estrellas.
    - Listado de opiniones aprobadas con soporte para fotografias y badge de compra verificada.
    - Formulario para calificar si el usuario tiene una compra despachada o entregada.
    """
    producto = get_object_or_404(Producto.objects.select_related('id_categoria'), id=producto_id)
    resenas = producto.resenas.filter(aprobado=True).select_related('usuario').order_by('-fecha_creacion')

    usuario_compro = False
    mi_resena = None
    es_favorito = False
    cantidad_en_carrito = 0

    if request.user.is_authenticated:
        # Se restringe la calificacion exclusivamente a ordenes despachadas o entregadas
        pedidos_enviados = Pedido.objects.filter(
            id_usuario=request.user,
            estado__in=['ENVIADO', 'ENTREGADO']
        )
        usuario_compro = DetallePedido.objects.filter(
            pedido__in=pedidos_enviados, producto=producto
        ).exists() or pedidos_enviados.filter(id_producto_opcional=producto).exists()

        mi_resena = Resena.objects.filter(usuario=request.user, producto=producto).first()
        es_favorito = ListaDeseos.objects.filter(usuario=request.user, producto=producto).exists()

        try:
            item_c = ItemCarrito.objects.filter(carrito__usuario=request.user, producto=producto).first()
            if item_c:
                cantidad_en_carrito = item_c.cantidad
        except Exception:
            pass

    relacionados = Producto.objects.filter(
        id_categoria=producto.id_categoria,
        activo=True
    ).exclude(id=producto.id)[:4]

    contexto = {
        'producto': producto,
        'resenas': resenas,
        'total_resenas': resenas.count(),
        'desglose_calificaciones': producto.get_desglose_calificaciones(),
        'usuario_compro': usuario_compro,
        'mi_resena': mi_resena,
        'es_favorito': es_favorito,
        'cantidad_en_carrito': cantidad_en_carrito,
        'relacionados': relacionados,
    }
    return render(request, 'productos/detalle_producto.html', contexto)


def detalle_combo(request, combo_id):
    """
    Despliega la ficha comercial del combo promocional.
    Muestra los articulos integrantes, cantidades, descuento, resenas y valoraciones.
    """
    combo = get_object_or_404(Combo.objects.prefetch_related('combosproductos_set__producto'), id=combo_id)
    resenas = combo.resenas.filter(aprobado=True).select_related('usuario').order_by('-fecha_creacion')

    usuario_compro = False
    mi_resena = None
    es_favorito = False
    cantidad_en_carrito = 0

    if request.user.is_authenticated:
        # Se restringe la calificacion exclusivamente a ordenes despachadas o entregadas
        pedidos_enviados = Pedido.objects.filter(
            id_usuario=request.user,
            estado__in=['ENVIADO', 'ENTREGADO']
        )
        usuario_compro = DetallePedido.objects.filter(
            pedido__in=pedidos_enviados, combo=combo
        ).exists() or pedidos_enviados.filter(combo_opcional=combo).exists()

        mi_resena = Resena.objects.filter(usuario=request.user, combo=combo).first()
        es_favorito = ListaDeseos.objects.filter(usuario=request.user, combo=combo).exists()

        try:
            item_c = ItemCarrito.objects.filter(carrito__usuario=request.user, combo=combo).first()
            if item_c:
                cantidad_en_carrito = item_c.cantidad
        except Exception:
            pass

    contexto = {
        'combo': combo,
        'items_combo': combo.combosproductos_set.select_related('producto'),
        'resenas': resenas,
        'total_resenas': resenas.count(),
        'desglose_calificaciones': combo.get_desglose_calificaciones(),
        'usuario_compro': usuario_compro,
        'mi_resena': mi_resena,
        'es_favorito': es_favorito,
        'cantidad_en_carrito': cantidad_en_carrito,
    }
    return render(request, 'productos/detalle_combo.html', contexto)


@login_required
def toggle_favorito(request, tipo, item_id):
    """
    Agrega o retira un articulo (producto o combo) de la lista de deseos del usuario.
    Soporta peticiones asincronas JSON (fetch/AJAX) para manipulacion reactiva
    y formularios POST tradicionales con redireccion.
    """
    is_ajax = (
        request.headers.get('x-requested-with') == 'XMLHttpRequest' or
        request.GET.get('format') == 'json' or
        'application/json' in request.headers.get('accept', '')
    )

    agregado = False
    mensaje = ""

    if tipo == 'producto':
        prod = get_object_or_404(Producto, id=item_id)
        deseo = ListaDeseos.objects.filter(usuario=request.user, producto=prod).first()
        if deseo:
            deseo.delete()
            agregado = False
            mensaje = f"'{prod.nombre}' se retiro de tus favoritos."
        else:
            ListaDeseos.objects.create(usuario=request.user, producto=prod)
            agregado = True
            mensaje = f"'{prod.nombre}' se agrego a tus favoritos ❤️"
    elif tipo == 'combo':
        cmb = get_object_or_404(Combo, id=item_id)
        deseo = ListaDeseos.objects.filter(usuario=request.user, combo=cmb).first()
        if deseo:
            deseo.delete()
            agregado = False
            mensaje = f"'{cmb.nombre}' se retiro de tus favoritos."
        else:
            ListaDeseos.objects.create(usuario=request.user, combo=cmb)
            agregado = True
            mensaje = f"'{cmb.nombre}' se agrego a tus favoritos ❤️"
    else:
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': 'Tipo no reconocido.'}, status=400)
        return redirect('inicio')

    total_deseos = ListaDeseos.objects.filter(usuario=request.user).count()

    if is_ajax:
        return JsonResponse({
            'status': 'ok',
            'agregado': agregado,
            'mensaje': mensaje,
            'total_deseos': total_deseos
        })

    messages.success(request, mensaje)
    referer = request.META.get('HTTP_REFERER')
    return redirect(referer if referer else 'ver_lista_deseos')


@login_required
def ver_lista_deseos(request):
    """
    Despliega la vitrina de articulos favoritos guardados por el cliente autenticado.
    Permite visualizar precios actuales, descuentos y transferir articulos al carrito.
    """
    deseos = ListaDeseos.objects.filter(
        usuario=request.user
    ).select_related('producto', 'combo').order_by('-fecha_agregado')

    return render(request, 'fidelizacion/mis_deseos.html', {'deseos': deseos})


@login_required
def quitar_de_deseos(request, deseo_id):
    """
    Elimina un item especifico de la lista de deseos del usuario.
    """
    deseo = get_object_or_404(ListaDeseos, id=deseo_id, usuario=request.user)
    nombre = deseo.producto.nombre if deseo.producto else (deseo.combo.nombre if deseo.combo else 'Articulo')
    deseo.delete()
    messages.info(request, f"Se retiro '{nombre}' de tu lista de deseos.")
    return redirect('ver_lista_deseos')


@login_required
def crear_resena(request, tipo, item_id):
    """
    Registra o actualiza la valoracion y comentario de un usuario sobre un producto o combo.
    Acepta calificacion en estrellas (1 a 5), texto y fotografia opcional.
    Verifica que el usuario posea una orden en estado ENVIADO o ENTREGADO.
    """
    if request.method != 'POST':
        return redirect('inicio')

    try:
        calificacion = int(request.POST.get('calificacion', 5))
    except (ValueError, TypeError):
        calificacion = 5

    calificacion = max(1, min(5, calificacion))
    titulo = request.POST.get('titulo', '').strip()
    comentario = request.POST.get('comentario', '').strip()
    foto = request.FILES.get('foto')

    if not comentario:
        messages.error(request, 'Por favor escribe un comentario para tu reseña.')
        return redirect(request.META.get('HTTP_REFERER', 'inicio'))

    if tipo == 'producto':
        prod = get_object_or_404(Producto, id=item_id)

        # Verificacion de seguridad: solo permitir calificar a clientes cuyos pedidos esten ENVIADOS o ENTREGADOS
        pedidos_enviados = Pedido.objects.filter(
            id_usuario=request.user,
            estado__in=['ENVIADO', 'ENTREGADO']
        )
        ha_comprado = DetallePedido.objects.filter(
            pedido__in=pedidos_enviados, producto=prod
        ).exists() or pedidos_enviados.filter(id_producto_opcional=prod).exists()

        if not ha_comprado and not request.user.is_staff:
            pedidos_prep = Pedido.objects.filter(
                id_usuario=request.user,
                estado='PAGADO'
            )
            en_prep = DetallePedido.objects.filter(
                pedido__in=pedidos_prep, producto=prod
            ).exists() or pedidos_prep.filter(id_producto_opcional=prod).exists()

            if en_prep:
                messages.info(request, 'Tu pedido aún se encuentra en preparación. Podrás calificar este producto una vez que tu orden haya sido enviada 🚚✨')
            else:
                messages.error(request, 'Solo los clientes con una orden enviada o entregada de este producto pueden calificarlo.')
            return redirect('detalle_producto', producto_id=prod.id)

        resena, created = Resena.objects.get_or_create(
            usuario=request.user,
            producto=prod,
            defaults={
                'calificacion': calificacion,
                'titulo': titulo,
                'comentario': comentario,
                'foto': foto,
                'aprobado': True,
            }
        )
        if not created:
            resena.calificacion = calificacion
            resena.titulo = titulo
            resena.comentario = comentario
            if foto:
                resena.foto = foto
            resena.save()
            messages.success(request, '¡Tu reseña fue actualizada correctamente! ✨')
        else:
            messages.success(request, '¡Muchas gracias por tu opinión! Tu reseña fue publicada con éxito ✨')
        return redirect('detalle_producto', producto_id=prod.id)

    elif tipo == 'combo':
        cmb = get_object_or_404(Combo, id=item_id)

        # Verificacion de seguridad: solo permitir calificar a clientes cuyos pedidos esten ENVIADOS o ENTREGADOS
        pedidos_enviados = Pedido.objects.filter(
            id_usuario=request.user,
            estado__in=['ENVIADO', 'ENTREGADO']
        )
        ha_comprado = DetallePedido.objects.filter(
            pedido__in=pedidos_enviados, combo=cmb
        ).exists() or pedidos_enviados.filter(combo_opcional=cmb).exists()

        if not ha_comprado and not request.user.is_staff:
            pedidos_prep = Pedido.objects.filter(
                id_usuario=request.user,
                estado='PAGADO'
            )
            en_prep = DetallePedido.objects.filter(
                pedido__in=pedidos_prep, combo=cmb
            ).exists() or pedidos_prep.filter(combo_opcional=cmb).exists()

            if en_prep:
                messages.info(request, 'Tu pedido aún se encuentra en preparación. Podrás calificar este combo una vez que tu orden haya sido enviada 🚚✨')
            else:
                messages.error(request, 'Solo los clientes con una orden enviada o entregada de este combo pueden calificarlo.')
            return redirect('detalle_combo', combo_id=cmb.id)

        resena, created = Resena.objects.get_or_create(
            usuario=request.user,
            combo=cmb,
            defaults={
                'calificacion': calificacion,
                'titulo': titulo,
                'comentario': comentario,
                'foto': foto,
                'aprobado': True,
            }
        )
        if not created:
            resena.calificacion = calificacion
            resena.titulo = titulo
            resena.comentario = comentario
            if foto:
                resena.foto = foto
            resena.save()
            messages.success(request, '¡Tu reseña de combo fue actualizada! ✨')
        else:
            messages.success(request, '¡Muchas gracias por tu opinión! Tu reseña del combo fue publicada con éxito ✨')
        return redirect('detalle_combo', combo_id=cmb.id)

    return redirect('inicio')
