import random
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
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings

from .models import (
    Categoria, Producto, Combo, Pedido,
    DetallePedido, CarritoDeCompras, ItemCarrito,
    ConfiguracionTienda
)
from .metricas_views import (
    metricas_ventas_dashboard,
    exportar_metricas_excel,
    enviar_alerta_stock_email_manual
)

# Etiquetas aleatorias para destacar productos en el inicio
PRODUCT_BADGES = [
    {'icon': 'fa-solid fa-fire', 'text': 'Top Venta'},
    {'icon': 'fa-solid fa-star', 'text': 'Favorito'},
    {'icon': 'fa-solid fa-sparkles', 'text': 'Especial'},
    {'icon': 'fa-solid fa-heart', 'text': 'Más Amado'},
    {'icon': 'fa-solid fa-bolt', 'text': 'Tendencia'},
    {'icon': 'fa-solid fa-crown', 'text': 'Imperdible'},
    {'icon': 'fa-solid fa-wand-magic-sparkles', 'text': 'Destacado'},
]

# Etiquetas aleatorias para destacar combos en el inicio
COMBO_BADGES = [
    {'icon': 'fa-solid fa-wand-magic-sparkles', 'text': 'Top Combo'},
    {'icon': 'fa-solid fa-crown', 'text': 'Combo Estrella'},
    {'icon': 'fa-solid fa-gift', 'text': 'Super Combo'},
    {'icon': 'fa-solid fa-gem', 'text': 'Combo Exclusivo'},
    {'icon': 'fa-solid fa-star', 'text': 'Combo Favorito'},
]


class NuevaContrasenaForm(SetPasswordForm):
    """Personaliza los campos del restablecimiento de contraseña."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'placeholder': 'Nueva contraseña',
            'id': 'new_password1',
        })
        self.fields['new_password2'].widget.attrs.update({
            'placeholder': 'Repetir contraseña',
            'id': 'new_password2',
        })


def logout_view(request):
    logout(request)
    return redirect('/login/')


def login_view(request):
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
            error = 'Usuario o contraseña incorrectos.'

    return render(request, 'admin/logintest.html', {'error': error})


def lista_productos(request):
    config = ConfiguracionTienda.get_solo()
    if not config.modulo_productos_habilitado:
        return render(
            request,
            "productos/lista.html",
            {
                "modulo_habilitado": False,
                "mensaje_mantenimiento": config.mensaje_mantenimiento_productos,
                "titulo": "Catálogo en Mantenimiento",
            }
        )

    if not Producto.objects.exists():
        from .seed_data import seed_database
        seed_database()

    categoria_slug = request.GET.get('categoria')

    # Obtener productos activos
    productos_query = Producto.objects.filter(
        activo=True
    ).exclude(
        id_categoria__nombre__iexact='Sorpresa'
    ).order_by("nombre")

    # Filtrar por categoría si se seleccionó alguna
    if categoria_slug:
        productos_query = productos_query.filter(
            id_categoria__nombre__iexact=categoria_slug
        )

    # Paginación (12 productos por página)
    paginator = Paginator(productos_query, 12)
    page_number = request.GET.get('page', 1)
    try:
        productos_paginados = paginator.page(page_number)
    except PageNotAnInteger:
        productos_paginados = paginator.page(1)
    except EmptyPage:
        productos_paginados = paginator.page(paginator.num_pages)

    # Obtener categorías que tengan productos activos
    categorias = Categoria.objects.filter(
        productos__activo=True
    ).exclude(
        nombre__iexact='Sorpresa'
    ).annotate(
        num_productos=Count('productos')
    ).order_by('nombre')

    # Diccionario de productos que están en el carrito
    productos_en_carrito = {}

    # Solo consultar el carrito si el usuario inició sesión
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
        "titulo": "Nuestra Colección de Productos",
        "productos_en_carrito": productos_en_carrito,
    }

    return render(
        request,
        "productos/lista.html",
        contexto
    )


def lista_sorpresas(request):
    """Muestra las experiencias sorpresa (Lucky Pop, Scoops, etc.) disponibles."""
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


@login_required
def agregar_a_carrito(request, producto_id):
    if request.method == 'POST':
        producto = get_object_or_404(Producto, id=producto_id)
        carrito, creado = CarritoDeCompras.objects.get_or_create(usuario=request.user)
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

        except CarritoDeCompras.DoesNotExist:
            pass
        except ItemCarrito.DoesNotExist:
            pass

        return redirect(request.META.get('HTTP_REFERER', 'lista_productos'))

    return redirect('lista_productos')


@login_required
def ver_carrito(request):
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


def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not email or not password1 or not password2:
            messages.error(request, "Todos los campos son obligatorios.")
            return render(request, 'admin/register.html')

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Por favor ingresa un correo electrónico válido.")
            return render(request, 'admin/register.html')

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, 'admin/register.html')

        # Validar fortaleza de la contraseña según AUTH_PASSWORD_VALIDATORS configurados
        try:
            validate_password(password1)
        except ValidationError as error:
            for msg in error.messages:
                messages.error(request, msg)
            return render(request, 'admin/register.html')

        if User.objects.filter(username=email).exists() or User.objects.filter(email=email).exists():
            messages.error(request, "Ya existe un usuario registrado con este correo electrónico.")
            return render(request, 'admin/register.html')

        # Crear usuario
        user = User.objects.create_user(username=email, email=email, password=password1)
        user.save()

        # Renderizamos la misma página con la modal activada
        return render(request, 'admin/register.html', {'messages_success': True})

    return render(request, 'admin/register.html')


def inicio(request):
    if not Producto.objects.exists():
        from .seed_data import seed_database
        seed_database()

    # Obtener 3 productos activos al azar (excluyendo categoría Sorpresa si existe)
    productos_query = Producto.objects.filter(activo=True).exclude(
        id_categoria__nombre__iexact='Sorpresa'
    )
    if productos_query.count() < 3:
        productos_query = Producto.objects.filter(activo=True)

    productos_destacados = list(productos_query.order_by('?')[:3])

    # Asignar etiquetas a los productos destacados (priorizando si es nuevo)
    badges_disponibles = PRODUCT_BADGES.copy()
    random.shuffle(badges_disponibles)
    for idx, prod in enumerate(productos_destacados):
        if prod.es_nuevo:
            prod.badge_icon = 'fa-solid fa-sparkles'
            prod.badge_text = '✨ Novedad'
        else:
            badge = badges_disponibles[idx % len(badges_disponibles)]
            prod.badge_icon = badge['icon']
            prod.badge_text = badge['text']

    # Obtener 1 combo activo al azar
    combos_destacados = list(Combo.objects.filter(activo=True).order_by('?')[:1])
    if combos_destacados:
        if combos_destacados[0].es_nuevo:
            combos_destacados[0].badge_icon = 'fa-solid fa-wand-magic-sparkles'
            combos_destacados[0].badge_text = '✨ Nuevo Combo'
        else:
            combo_tag = random.choice(COMBO_BADGES)
            combos_destacados[0].badge_icon = combo_tag['icon']
            combos_destacados[0].badge_text = combo_tag['text']

    # Diccionarios para el carrito
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
    return render(request, 'sobre_nosotros.html')


@login_required
def finalizar_compra(request):
    config = ConfiguracionTienda.get_solo()
    if not config.compras_habilitadas:
        messages.warning(
            request,
            config.mensaje_mantenimiento_compras or "La opción de finalizar compras no se encuentra disponible temporalmente."
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
                items_comprados_info = []
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
                    nombre_item = item.producto.nombre if item.producto else (item.combo.nombre if item.combo else 'Ítem')
                    items_comprados_info.append(f"• {item.cantidad}x {nombre_item} - ${precio_unitario:,.0f} COP c/u")

                    # Actualización de inventario en tiempo real
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

                # Enviar correos: confirmación al cliente, notificación al administrador y alertas de stock bajo
                try:
                    from .emails import (
                        enviar_correo_confirmacion_compra,
                        enviar_correo_nuevo_pedido_administrador,
                        enviar_correo_alerta_stock_bajo
                    )
                    enviar_correo_confirmacion_compra(nuevo_pedido)
                    enviar_correo_nuevo_pedido_administrador(nuevo_pedido)
                    if productos_alerta_stock:
                        enviar_correo_alerta_stock_bajo(productos_alerta_stock, motivo="Compra Realizada", pedido=nuevo_pedido)
                except Exception:
                    pass

                return redirect('pagina_confirmacion', pedido_id=nuevo_pedido.id)

        except CarritoDeCompras.DoesNotExist:
            return redirect('lista_productos')
        except IntegrityError:
            return render(request, 'error_transaccion.html', {'mensaje': 'Ocurrió un error al procesar el pedido.'})

    return redirect('ver_carrito')


@login_required
def mis_pedidos(request):
    """Muestra el historial de compras del usuario autenticado."""
    pedidos = Pedido.objects.filter(
        id_usuario=request.user
    ).order_by('-fecha_pedido').prefetch_related('detalles__producto', 'detalles__combo')

    return render(request, 'pedido/mis_pedidos.html', {'pedidos': pedidos})


@login_required
def pagina_confirmacion(request, pedido_id):
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



def lista_combos(request):
    """Muestra el catálogo de combos disponibles."""
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
        if productos_lista:
            combo.descripcion_productos = ", ".join(productos_lista)
        else:
            combo.descripcion_productos = None

    # Paginación (12 combos por página)
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
        "titulo": "Nuestra Colección de Combos",
        "combos_en_carrito": combos_en_carrito,
    }

    return render(
        request,
        "productos/combos.html",
        contexto
    )


def _manejar_item_carrito(request, combo_id, action='add'):
    if request.method != 'POST':
        return redirect('lista_combos')

    combo = get_object_or_404(Combo, id=combo_id)
    carrito, creado = CarritoDeCompras.objects.get_or_create(usuario=request.user)

    item_carrito, item_creado = ItemCarrito.objects.get_or_create(
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
    return _manejar_item_carrito(request, combo_id, action='add')


@login_required
def quitar_combo_de_carrito(request, combo_id):
    return _manejar_item_carrito(request, combo_id, action='remove')
