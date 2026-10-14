"""
Modulo de Modelos de Datos - Sorpresas Kawaii.

Define la estructura relacional de la base de datos, incluyendo:
- Clasificacion y catalogo de inventario (Categoria, Producto, Combo).
- Modelos transaccionales de usuario (UserProfile, CarritoDeCompras, ItemCarrito).
- Gestion de ordenes de compra, estados y logistica (Pedido, DetallePedido).
- Configuracion global de la tienda mediante patron Singleton (ConfiguracionTienda).
- Modelo Proxy para experiencias dinamicas (Sorpresa).
"""

import uuid
import re
import urllib.parse
from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class Categoria(models.Model):
    """
    Representa las categorias o familias de articulos del catalogo (ej. Papeleria, Peluches, Accesorios).
    Permite segmentar y filtrar los productos en la tienda virtual.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador unico universal (UUIDv4) para evitar enumeracion secuencial."
    )
    nombre = models.CharField(
        max_length=255,
        unique=True,
        help_text="Nombre unico de la categoria."
    )

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class UserProfile(models.Model):
    """
    Extension del modelo de autenticacion User de Django (relacion 1:1).
    Almacena informacion complementaria del cliente, principalmente la direccion fisica de despacho.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        help_text="Usuario del sistema al que pertenece este perfil."
    )
    direccion_envio = models.TextField(
        blank=True,
        null=True,
        help_text="Direccion fisica completa de residencia o entrega para despachos nacionales."
    )

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"

    def __str__(self):
        return f"Perfil de {self.user.username}"


class Producto(models.Model):
    """
    Entidad fundamental del catalogo de inventario.
    Contiene la informacion comercial, precio base, porcentaje de descuento,
    control de stock en tiempo real y gestion de archivos multimedia.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador unico universal del producto."
    )
    id_categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        related_name='productos',
        null=True,
        blank=True,
        help_text="Categoria a la que pertenece el producto. Si se elimina la categoria, el producto permanece."
    )
    nombre = models.CharField(
        max_length=255,
        help_text="Nombre descriptivo del producto."
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Descripcion detallada de caracteristicas, dimensiones y materiales."
    )
    valor_unitario = models.FloatField(
        help_text="Precio de venta base en pesos colombianos (COP)."
    )
    descuento_porcentaje = models.FloatField(
        default=0.0,
        help_text="Porcentaje de descuento comercial aplicable (ej. 15.0 para 15% de descuento)."
    )
    stock = models.IntegerField(
        default=0,
        help_text="Cantidad de unidades fisicas disponibles para la venta."
    )
    imagen = models.ImageField(
        upload_to='productos/',
        blank=True,
        null=True,
        help_text="Fotografia cargada directamente al servidor."
    )
    imagen_url = models.URLField(
        max_length=700,
        blank=True,
        null=True,
        help_text="Enlace externo a la imagen en CDN o almacenamiento en la nube."
    )
    es_nuevo = models.BooleanField(
        default=False,
        verbose_name="Es Novedad / Producto Nuevo",
        help_text="Indica si se debe mostrar una etiqueta destacada en el catalogo."
    )
    activo = models.BooleanField(
        default=True,
        help_text="Indica si el producto esta visible y habilitado para la compra."
    )

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    @property
    def get_imagen_url(self):
        """
        Retorna la URL valida para renderizar la imagen, priorizando la imagen local
        y utilizando la URL externa como respaldo.
        """
        if self.imagen:
            return self.imagen.url
        if self.imagen_url:
            return self.imagen_url
        return None

    @property
    def precio_final(self):
        """
        Calcula y retorna el precio unitario neto aplicando el porcentaje de descuento vigente.
        Si no hay descuento, retorna el valor_unitario base.
        """
        if self.descuento_porcentaje and self.descuento_porcentaje > 0:
            return round(self.valor_unitario * (1 - (self.descuento_porcentaje / 100)), 2)
        return self.valor_unitario


class Combo(models.Model):
    """
    Representa paquetes o kits promocionales conformados por uno o mas productos.
    Permite establecer un precio global con descuento para fomentar la venta cruzada.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador unico universal del combo."
    )
    nombre = models.CharField(
        max_length=255,
        default="Combo",
        null=True,
        help_text="Nombre comercial del combo promocional."
    )
    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text="Detalle de los articulos que incluye el combo y su tematica."
    )
    imagen = models.ImageField(
        upload_to='combos/',
        blank=True,
        null=True,
        help_text="Imagen ilustrativa del combo cargada al servidor."
    )
    imagen_url = models.URLField(
        max_length=700,
        blank=True,
        null=True,
        help_text="Enlace externo a la imagen ilustrativa del combo."
    )
    productos = models.ManyToManyField(
        Producto,
        through='CombosProductos',
        related_name='combos',
        blank=True,
        help_text="Coleccion de productos individuales incluidos en este paquete promocional."
    )
    usuario_id = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='combos_creados',
        null=True,
        blank=True,
        help_text="Usuario o administrador que configuro el combo."
    )
    numero_productos = models.IntegerField(
        default=0,
        help_text="Cantidad teorica o promedio de productos dentro del paquete."
    )
    descuento_porcentaje = models.FloatField(
        default=0.0,
        help_text="Porcentaje de descuento global aplicado sobre el valor del combo."
    )
    valor_combo = models.FloatField(
        help_text="Precio total de venta del combo antes del descuento."
    )
    valido_hasta = models.DateField(
        blank=True,
        null=True,
        help_text="Fecha limite de vigencia para combos de temporada o promociones temporales."
    )
    es_nuevo = models.BooleanField(
        default=False,
        verbose_name="Es Combo Nuevo / Novedad",
        help_text="Indica si debe presentarse con etiqueta de novedad en la vitrina."
    )
    activo = models.BooleanField(
        default=True,
        help_text="Indica si el combo se encuentra disponible para su venta en la plataforma."
    )

    class Meta:
        verbose_name = "Combo"
        verbose_name_plural = "Combos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre if self.nombre else f"Combo {self.id}"

    @property
    def get_imagen_url(self):
        """
        Retorna la URL valida para la imagen del combo, con soporte para archivo local o CDN.
        """
        if self.imagen:
            return self.imagen.url
        if self.imagen_url:
            return self.imagen_url
        return None

    @property
    def precio_final(self):
        """
        Calcula el valor liquidado del combo aplicando el porcentaje de descuento si existe.
        """
        if self.descuento_porcentaje and self.descuento_porcentaje > 0:
            return round(self.valor_combo * (1 - (self.descuento_porcentaje / 100)), 2)
        return self.valor_combo


class CombosProductos(models.Model):
    """
    Tabla intermedia para la relacion Muchos a Muchos (M2M) entre Combo y Producto.
    Permite registrar la cantidad exacta de unidades de un producto incluidas en un combo especifico.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    combo = models.ForeignKey(
        Combo,
        on_delete=models.CASCADE,
        help_text="Combo al que pertenece el articulo."
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        help_text="Producto individual asignado al combo."
    )
    cantidad = models.PositiveSmallIntegerField(
        default=1,
        help_text="Numero de unidades del producto contenidas en el combo."
    )

    class Meta:
        unique_together = ('combo', 'producto')
        verbose_name = "Producto en Combo"
        verbose_name_plural = "Productos en Combos"

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} en {self.combo.nombre}"


class Pedido(models.Model):
    """
    Representa una orden de compra generada por un cliente registrado.
    Controla el ciclo de vida del pedido (estados comerciales), los datos de envio,
    el numero de guia logistica y la generacion de comunicados automaticos.
    """
    ESTADOS = [
        ('PENDIENTE', 'Pendiente de Pago'),
        ('PAGADO', 'Pagado'),
        ('ENVIADO', 'Enviado'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    ]

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador unico de la orden en el sistema."
    )
    id_usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='pedidos',
        help_text="Cliente que origino la compra."
    )
    fecha_pedido = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha y hora exacta de creacion de la orden."
    )
    valor_pagado = models.FloatField(
        help_text="Monto total liquidado de la orden en pesos colombianos (incluye flete si aplica)."
    )
    estado = models.CharField(
        max_length=50,
        choices=ESTADOS,
        default='PENDIENTE',
        help_text="Estado actual dentro del flujo de procesamiento logistico y financiero."
    )
    metodo_pago = models.CharField(
        max_length=100,
        help_text="Canal de pago seleccionado (ej. Transferencia Nequi, Daviplata, Efectivo)."
    )
    detalle_pago = models.TextField(
        blank=True,
        null=True,
        help_text="Notas adicionales o referencias del comprobante de transferencia bancaria."
    )
    comprobante_pago = models.ImageField(
        upload_to='comprobantes/',
        blank=True,
        null=True,
        verbose_name="Comprobante de Pago",
        help_text="Archivo de imagen del recibo o captura de pantalla de la transaccion."
    )
    empresa_envio = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Empresa de Envio",
        help_text="Nombre de la transportadora responsable de la entrega (ej. Servientrega, Interrapidisimo)."
    )
    numero_guia = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Numero de Guia",
        help_text="Codigo alfanumerico de seguimiento emitido por la empresa de mensajeria."
    )
    is_combo = models.BooleanField(
        default=False,
        help_text="Campo auxiliar para identificar ordenes originadas desde un combo unico."
    )
    combo_opcional = models.ForeignKey(
        Combo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedidos_combo'
    )
    id_producto_opcional = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedidos_producto'
    )

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-fecha_pedido']

    @property
    def codigo_pedido(self):
        """
        Genera un identificador abreviado y profesional para atencion al cliente (ej. #SK-A1B2C3),
        extrayendo los primeros 6 caracteres del UUID del pedido en mayusculas.
        """
        clean_hex = str(self.id).replace('-', '').upper()
        return f"#SK-{clean_hex[:6]}"

    def generar_mensaje_whatsapp(self):
        """
        Construye el texto formateado para transmitir los datos de la orden a la linea de WhatsApp
        oficial del negocio. Incluye codigo, cliente, total, estado y desglose de items.
        """
        nombre_cliente = self.id_usuario.first_name or self.id_usuario.username
        items_lista = []

        for d in self.detalles.all():
            nombre_item = d.producto.nombre if d.producto else (
                d.combo.nombre if d.combo else 'Item'
            )
            items_lista.append(f"- {d.cantidad}x {nombre_item} (${d.precio_item:,.0f} COP c/u)")

        if not items_lista:
            if self.combo_opcional:
                items_lista.append(f"- 1x {self.combo_opcional.nombre}")
            elif self.id_producto_opcional:
                items_lista.append(f"- 1x {self.id_producto_opcional.nombre}")

        items_str = "\n".join(items_lista) if items_lista else "- Articulos registrados en el sistema"

        lineas = [
            "Hola, acabo de realizar una compra en Sorpresas Kawaii.",
            "",
            f"*Pedido:* {self.codigo_pedido}",
            f"*Cliente:* {nombre_cliente}",
            f"*Total a pagar:* ${self.valor_pagado:,.0f} COP",
            f"*Estado:* {self.get_estado_display()}",
            "",
            "*Articulos incluidos:*",
            items_str,
            "",
            "Quedo a la espera de las indicaciones para coordinar el pago y despacho. Muchas gracias."
        ]
        return "\n".join(lineas)

    @property
    def whatsapp_url(self):
        """
        Retorna la URL Click-to-Chat de WhatsApp codificada bajo el estandar RFC 3986,
        apuntando al numero oficial configurado en el sistema.
        """
        phone = getattr(settings, 'WHATSAPP_PHONE_NUMBER', '573222385508')
        phone_clean = re.sub(r'\D', '', str(phone))
        mensaje = self.generar_mensaje_whatsapp()
        return f"https://wa.me/{phone_clean}?text={urllib.parse.quote(mensaje)}"

    def save(self, *args, **kwargs):
        """
        Metodo save interceptado para detectar transiciones de estado o actualizaciones
        en la guia de transporte y emitir notificaciones por correo electronico de forma automatica.
        """
        is_new = self.pk is None
        old_estado = None
        old_empresa = None
        old_guia = None

        if not is_new:
            prev = Pedido.objects.filter(pk=self.pk).values('estado', 'empresa_envio', 'numero_guia').first()
            if prev:
                old_estado = prev.get('estado')
                old_empresa = prev.get('empresa_envio')
                old_guia = prev.get('numero_guia')

        super().save(*args, **kwargs)

        # Disparar notificacion si hubo cambio relevante en un pedido existente
        if not is_new and old_estado is not None:
            estado_cambio = old_estado != self.estado
            guia_cambio = (self.estado in ('ENVIADO', 'ENTREGADO')) and (
                (bool(self.numero_guia) and self.numero_guia != old_guia) or
                (bool(self.empresa_envio) and self.empresa_envio != old_empresa)
            )

            if estado_cambio or guia_cambio:
                try:
                    from .emails import enviar_correo_actualizacion_pedido
                    enviar_correo_actualizacion_pedido(
                        self,
                        estado_anterior=old_estado,
                        info_rastreo_actualizada=guia_cambio and not estado_cambio
                    )
                except Exception:
                    # Se captura para evitar que una falla externa en el servicio SMTP interrumpa la persistencia
                    pass

    def __str__(self):
        return f"Pedido {self.codigo_pedido} - {self.id_usuario.username}"


class DetallePedido(models.Model):
    """
    Almacena los items individuales que integran una orden de compra (Pedido).
    Guarda una copia fija del precio al momento de la venta para garantizar la integridad
    historica ante futuras variaciones en el catalogo general.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='detalles',
        help_text="Orden de compra a la que pertenece esta linea de detalle."
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Producto individual asociado si aplica."
    )
    combo = models.ForeignKey(
        Combo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Combo promocional asociado si aplica."
    )
    cantidad = models.PositiveIntegerField(
        default=1,
        help_text="Numero de unidades facturadas de este item."
    )
    precio_item = models.FloatField(
        help_text="Precio unitario liquidado al momento de formalizar la compra."
    )

    class Meta:
        verbose_name = "Detalle de Pedido"
        verbose_name_plural = "Detalles de Pedidos"

    def __str__(self):
        item_nombre = self.producto.nombre if self.producto else (
            self.combo.nombre if (self.combo and self.combo.nombre) else (
                f"Combo {self.combo.id}" if self.combo else "Item Desconocido"
            )
        )
        return f"{self.cantidad} x {item_nombre} en Pedido {self.pedido.codigo_pedido}"


class CarritoDeCompras(models.Model):
    """
    Representa el contenedor persistente de compras de un usuario registrado.
    Existe una unica instancia de carrito por cada cuenta de usuario.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='carrito',
        help_text="Usuario propietario del carrito."
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de inicializacion del carrito en el sistema."
    )

    class Meta:
        verbose_name = "Carrito de Compras"
        verbose_name_plural = "Carritos de Compras"

    def __str__(self):
        return f"Carrito de {self.usuario.username}"


class ItemCarrito(models.Model):
    """
    Linea de articulo dentro del carrito de compras de un usuario.
    Permite vincular referencias a productos o combos con sus respectivas cantidades deseadas.
    """
    carrito = models.ForeignKey(
        CarritoDeCompras,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Carrito al que pertenece el articulo."
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Producto individual seleccionado."
    )
    combo = models.ForeignKey(
        Combo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Combo promocional seleccionado."
    )
    cantidad = models.IntegerField(
        default=1,
        help_text="Cantidad seleccionada para adquirir."
    )
    fecha_agregado = models.DateTimeField(
        auto_now_add=True,
        help_text="Marca temporal en la que se incorporo el articulo."
    )

    class Meta:
        verbose_name = "Articulo en Carrito"
        verbose_name_plural = "Articulos en Carritos"

    def __str__(self):
        nombre = self.producto.nombre if self.producto else (
            self.combo.nombre if (self.combo and self.combo.nombre) else (
                f"Combo {self.combo.id}" if self.combo else "Item"
            )
        )
        return f"{self.cantidad} x {nombre}"


class ConfiguracionTienda(models.Model):
    """
    Modelo estructurado bajo patron Singleton para la parametrizacion global de la tienda.
    Permite a la administracion habilitar o inhabilitar modulos comerciales especificos,
    personalizar mensajes de mantenimiento y fijar politicas de costos de transporte.
    """
    compras_habilitadas = models.BooleanField(
        default=False,
        verbose_name="Finalizacion de compras habilitada",
        help_text="Permite activar o suspender el checkout en linea. Si se desmarca, se muestra el aviso de mantenimiento."
    )
    modulo_productos_habilitado = models.BooleanField(
        default=True,
        verbose_name="Catalogo de Productos habilitado",
        help_text="Controla la visibilidad y disponibilidad del catalogo general de productos."
    )
    modulo_sorpresas_habilitado = models.BooleanField(
        default=True,
        verbose_name="Seccion de Sorpresas habilitada",
        help_text="Controla la disponibilidad del modulo de sorpresas o scoops."
    )
    modulo_combos_habilitado = models.BooleanField(
        default=True,
        verbose_name="Seccion de Combos habilitada",
        help_text="Controla la disponibilidad del catalogo de combos promocionales."
    )
    mensaje_mantenimiento_compras = models.TextField(
        default="El proceso de compra en linea se encuentra temporalmente en mantenimiento. Pronto estara habilitado nuevamente.",
        blank=True,
        verbose_name="Mensaje de aviso en compras"
    )
    mensaje_mantenimiento_productos = models.TextField(
        default="Estamos actualizando nuestro catalogo con nuevos articulos. Esta seccion estara disponible muy pronto.",
        blank=True,
        verbose_name="Mensaje de aviso en productos"
    )
    mensaje_mantenimiento_sorpresas = models.TextField(
        default="Estamos preparando nuevas experiencias y sorpresas. Esta seccion estara disponible muy pronto.",
        blank=True,
        verbose_name="Mensaje de aviso en sorpresas"
    )
    mensaje_mantenimiento_combos = models.TextField(
        default="Estamos renovando nuestras combinaciones y combos especiales. Vuelve a consultarlos pronto.",
        blank=True,
        verbose_name="Mensaje de aviso en combos"
    )
    monto_minimo_envio_gratis = models.FloatField(
        default=60000.0,
        verbose_name="Monto minimo para Envio Gratis (COP)",
        help_text="Compras con subtotal igual o superior a este monto obtienen flete gratuito."
    )
    costo_envio_estandar = models.FloatField(
        default=5000.0,
        verbose_name="Costo de envio estandar (COP)",
        help_text="Tarifa fija aplicada a ordenes que no alcanzan el umbral de envio gratis."
    )

    class Meta:
        verbose_name = "Configuracion de la Tienda"
        verbose_name_plural = "Configuracion de la Tienda"

    def __str__(self):
        return "Ajustes Globales de la Tienda"

    @classmethod
    def get_solo(cls):
        """
        Retorna la unica instancia global de configuracion existente, instanciandola
        con identificador id=1 en caso de que no exista previamente.
        """
        obj, _ = cls.objects.get_or_create(id=1)
        return obj

    def save(self, *args, **kwargs):
        """
        Fuerza la persistencia sobre la clave primaria id=1 para asegurar que nunca
        se creen registros duplicados de configuracion.
        """
        self.id = 1
        super().save(*args, **kwargs)


class SorpresaManager(models.Manager):
    """
    Manager personalizado para filtrar automaticamente aquellos articulos del modelo
    Producto asociados a la categoria 'Sorpresa'.
    """
    def get_queryset(self):
        return super().get_queryset().filter(id_categoria__nombre__iexact='Sorpresa')


class Sorpresa(Producto):
    """
    Modelo Proxy derivado de Producto.
    Permite administrar de forma independiente en Django Admin las cajas tematicas y scoops
    sin duplicar tablas relacionales ni alterar el esquema subyacente.
    """
    objects = SorpresaManager()

    class Meta:
        proxy = True
        verbose_name = "Sorpresa y Experiencia"
        verbose_name_plural = "Sorpresas y Experiencias"
