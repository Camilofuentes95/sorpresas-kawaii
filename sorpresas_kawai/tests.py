import uuid
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Pedido, Producto, Categoria, CarritoDeCompras, ItemCarrito


class SecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='cliente_test@ejemplo.com',
            email='cliente_test@ejemplo.com',
            password='PasswordRobusto123!#'
        )
        self.otro_usuario = User.objects.create_user(
            username='otro_cliente@ejemplo.com',
            email='otro_cliente@ejemplo.com',
            password='OtroPassword123!#'
        )
        self.pedido_user = Pedido.objects.create(
            id_usuario=self.user,
            valor_pagado=50000,
            estado='PENDIENTE',
            metodo_pago='Efectivo/Prueba'
        )

    def test_register_exitoso_con_contrasena_robusta(self):
        """Valida que un usuario se registre correctamente con contraseña segura."""
        response = self.client.post(reverse('register'), {
            'email': 'nuevo_usuario@ejemplo.com',
            'password1': 'MiClaveSegura2026!#',
            'password2': 'MiClaveSegura2026!#'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(email='nuevo_usuario@ejemplo.com').exists())

    def test_register_rechaza_contrasena_debil_o_corta(self):
        """Valida que se rechace una contraseña corta o puramente numérica (AUTH_PASSWORD_VALIDATORS)."""
        response = self.client.post(reverse('register'), {
            'email': 'usuario_debil@ejemplo.com',
            'password1': '123',
            'password2': '123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='usuario_debil@ejemplo.com').exists())

    def test_register_rechaza_contrasenas_no_coincidentes(self):
        """Valida que se rechace si las contraseñas no coinciden."""
        response = self.client.post(reverse('register'), {
            'email': 'mismatch@ejemplo.com',
            'password1': 'ClaveSegura123!#',
            'password2': 'ClaveDiferente123!#'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='mismatch@ejemplo.com').exists())

    def test_register_rechaza_email_invalido(self):
        """Valida que se rechace un formato de correo incorrecto."""
        response = self.client.post(reverse('register'), {
            'email': 'correo-no-valido',
            'password1': 'ClaveSegura123!#',
            'password2': 'ClaveSegura123!#'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='correo-no-valido').exists())

    def test_register_rechaza_correo_duplicado(self):
        """Valida que no se permita registrar una cuenta con un correo ya existente."""
        response = self.client.post(reverse('register'), {
            'email': 'cliente_test@ejemplo.com',
            'password1': 'ClaveSegura123!#',
            'password2': 'ClaveSegura123!#'
        })
        self.assertEqual(response.status_code, 200)

    def test_rutas_protegidas_redirigen_a_login_para_anonimos(self):
        """Valida que las rutas privadas requieran inicio de sesión."""
        rutas_privadas = [
            reverse('ver_carrito'),
            reverse('mis_pedidos'),
            reverse('pagina_confirmacion', kwargs={'pedido_id': self.pedido_user.id})
        ]
        for ruta in rutas_privadas:
            response = self.client.get(ruta)
            self.assertEqual(response.status_code, 302)
            self.assertIn('/login/', response.url)

    def test_proteccion_idor_en_confirmacion_pedido(self):
        """Valida que un usuario no pueda ver el pedido de otro usuario (404/Insecure Direct Object Reference)."""
        self.client.force_login(self.otro_usuario)
        response = self.client.get(reverse('pagina_confirmacion', kwargs={'pedido_id': self.pedido_user.id}))
        self.assertEqual(response.status_code, 404)

        # El usuario dueño sí debe poder verlo
        self.client.force_login(self.user)
        response_owner = self.client.get(reverse('pagina_confirmacion', kwargs={'pedido_id': self.pedido_user.id}))
        self.assertEqual(response_owner.status_code, 200)


class OrderNotificationAndWhatsAppTests(TestCase):
    def setUp(self):
        from django.core import mail
        from .models import DetallePedido, Combo
        self.mail = mail
        self.mail.outbox = []

        self.user = User.objects.create_user(
            username='kawaii_buyer@ejemplo.com',
            email='kawaii_buyer@ejemplo.com',
            first_name='Miku',
            password='TestPassword123!#'
        )
        self.categoria = Categoria.objects.create(nombre='Peluches')
        self.producto = Producto.objects.create(
            nombre='Peluche Kuromi',
            id_categoria=self.categoria,
            valor_unitario=35000,
            stock=10,
            activo=True
        )
        self.combo = Combo.objects.create(
            nombre='Combo Pastel',
            valor_combo=50000,
            activo=True
        )

        self.pedido = Pedido.objects.create(
            id_usuario=self.user,
            valor_pagado=85000,
            estado='PENDIENTE',
            metodo_pago='WhatsApp / Efectivo'
        )
        DetallePedido.objects.create(
            pedido=self.pedido,
            producto=self.producto,
            cantidad=1,
            precio_item=35000
        )
        DetallePedido.objects.create(
            pedido=self.pedido,
            combo=self.combo,
            cantidad=1,
            precio_item=50000
        )

    def test_generar_mensaje_y_url_whatsapp(self):
        """Valida que el enlace de WhatsApp contenga el número +573222385508 y los artículos."""
        url = self.pedido.whatsapp_url
        mensaje = self.pedido.generar_mensaje_whatsapp()

        self.assertIn("https://wa.me/573222385508", url)
        self.assertIn(self.pedido.codigo_pedido, mensaje)
        self.assertIn("Peluche Kuromi", mensaje)
        self.assertIn("Combo Pastel", mensaje)
        self.assertIn("85,000", mensaje)

    def test_notificacion_correo_al_cambiar_a_pagado(self):
        """Valida que se envíe un correo al cambiar el estado del pedido a PAGADO."""
        self.mail.outbox = []
        self.pedido.estado = 'PAGADO'
        self.pedido.save()

        self.assertEqual(len(self.mail.outbox), 1)
        email = self.mail.outbox[0]
        self.assertEqual(email.to, ['kawaii_buyer@ejemplo.com'])
        self.assertIn("Pago Confirmado", email.subject)
        self.assertIn(self.pedido.codigo_pedido, email.body)
        self.assertIn("Peluche Kuromi", email.body)

    def test_notificacion_correo_al_cambiar_a_enviado_con_guia(self):
        """Valida que se envíe un correo con la guía y transportadora al cambiar a ENVIADO."""
        self.mail.outbox = []
        self.pedido.estado = 'ENVIADO'
        self.pedido.empresa_envio = 'Servientrega'
        self.pedido.numero_guia = 'GUIA-998877'
        self.pedido.save()

        self.assertEqual(len(self.mail.outbox), 1)
        email = self.mail.outbox[0]
        self.assertEqual(email.to, ['kawaii_buyer@ejemplo.com'])
        self.assertIn("enviado", email.subject.lower())
        self.assertIn("Servientrega", email.body)
        self.assertIn("GUIA-998877", email.body)

    def test_notificacion_correo_al_cambiar_a_entregado(self):
        """Valida que se envíe un correo de felicitación al entregar el pedido."""
        self.mail.outbox = []
        self.pedido.estado = 'ENTREGADO'
        self.pedido.save()

        self.assertEqual(len(self.mail.outbox), 1)
        email = self.mail.outbox[0]
        self.assertEqual(email.to, ['kawaii_buyer@ejemplo.com'])
        self.assertIn("entregado", email.subject.lower())

    def test_notificacion_correo_al_cambiar_a_cancelado(self):
        """Valida que se envíe un correo de notificación al cancelar el pedido."""
        self.mail.outbox = []
        self.pedido.estado = 'CANCELADO'
        self.pedido.save()

        self.assertEqual(len(self.mail.outbox), 1)
        email = self.mail.outbox[0]
        self.assertEqual(email.to, ['kawaii_buyer@ejemplo.com'])
        self.assertIn("cancelado", email.subject.lower())

    def test_context_processor_carrito_total_items(self):
        """Valida que el context processor sume correctamente los artículos del carrito."""
        from django.test.client import RequestFactory
        from .context_processors import carrito_context

        factory = RequestFactory()
        request = factory.get('/')
        request.user = self.user

        carrito, _ = CarritoDeCompras.objects.get_or_create(usuario=self.user)
        ItemCarrito.objects.create(carrito=carrito, producto=self.producto, cantidad=3)
        ItemCarrito.objects.create(carrito=carrito, combo=self.combo, cantidad=2)

        data = carrito_context(request)
        self.assertEqual(data.get('carrito_total_items'), 5)

    def test_notificacion_correo_nuevo_pedido_administrador(self):
        """Valida que la función enviar_correo_nuevo_pedido_administrador envíe los datos del pedido al admin."""
        from .emails import enviar_correo_nuevo_pedido_administrador
        from django.test import override_settings

        self.mail.outbox = []
        with override_settings(ADMIN_EMAIL='admin_tienda@ejemplo.com'):
            resultado = enviar_correo_nuevo_pedido_administrador(self.pedido)

        self.assertTrue(resultado)
        self.assertEqual(len(self.mail.outbox), 1)
        email_admin = self.mail.outbox[0]
        self.assertEqual(email_admin.to, ['admin_tienda@ejemplo.com'])
        self.assertIn("Nuevo Pedido", email_admin.subject)
        self.assertIn(self.pedido.codigo_pedido, email_admin.subject)
        self.assertIn("kawaii_buyer@ejemplo.com", email_admin.body)
        self.assertIn("Peluche Kuromi", email_admin.body)
        self.assertIn("Combo Pastel", email_admin.body)
        self.assertIn("85,000", email_admin.body)

    def test_finalizar_compra_deshabilitada_bloquea_pedido(self):
        """Valida que si compras_habilitadas es False no se procese la compra y se redirija al carrito."""
        from .models import ConfiguracionTienda
        config = ConfiguracionTienda.get_solo()
        config.compras_habilitadas = False
        config.save()

        client = Client()
        client.force_login(self.user)

        carrito, _ = CarritoDeCompras.objects.get_or_create(usuario=self.user)
        ItemCarrito.objects.create(carrito=carrito, producto=self.producto, cantidad=1)

        response = client.post(reverse('finalizar_compra'))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('ver_carrito'))
        # El carrito aún conserva el ítem y no se creó pedido
        self.assertTrue(ItemCarrito.objects.filter(carrito=carrito).exists())

    def test_finalizar_compra_envia_correo_a_cliente_y_admin(self):
        """Valida que al finalizar una compra (cuando está habilitada) se despachen correos tanto al cliente como al administrador."""
        from django.test import override_settings
        from .models import ConfiguracionTienda
        config = ConfiguracionTienda.get_solo()
        config.compras_habilitadas = True
        config.save()

        client = Client()
        client.force_login(self.user)

        carrito, _ = CarritoDeCompras.objects.get_or_create(usuario=self.user)
        ItemCarrito.objects.create(carrito=carrito, producto=self.producto, cantidad=1)

        self.mail.outbox = []
        with override_settings(ADMIN_EMAIL='admin_alertas@ejemplo.com'):
            response = client.post(reverse('finalizar_compra'))

        self.assertEqual(response.status_code, 302)
        # Debe haber enviado 2 correos: 1 al cliente y 1 al administrador
        self.assertEqual(len(self.mail.outbox), 2)
        destinatarios_enviados = [msg.to[0] for msg in self.mail.outbox]
        self.assertIn('kawaii_buyer@ejemplo.com', destinatarios_enviados)
        self.assertIn('admin_alertas@ejemplo.com', destinatarios_enviados)

    def test_modulo_sorpresas_mantenimiento(self):
        """Valida que desactivar el módulo de sorpresas muestre el aviso de mantenimiento en la plantilla."""
        from .models import ConfiguracionTienda
        config = ConfiguracionTienda.get_solo()
        config.modulo_sorpresas_habilitado = False
        config.mensaje_mantenimiento_sorpresas = "Mantenimiento Sorpresa de Prueba"
        config.save()

        client = Client()
        response = client.get(reverse('lista_sorpresas'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sección Sorpresas en Mantenimiento")
        self.assertContains(response, "Mantenimiento Sorpresa de Prueba")

    def test_modulo_combos_mantenimiento(self):
        """Valida que desactivar el módulo de combos muestre el aviso de mantenimiento en la plantilla."""
        from .models import ConfiguracionTienda
        config = ConfiguracionTienda.get_solo()
        config.modulo_combos_habilitado = False
        config.mensaje_mantenimiento_combos = "Mantenimiento Combos de Prueba"
        config.save()

        client = Client()
        response = client.get(reverse('lista_combos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sección Combos en Mantenimiento")
        self.assertContains(response, "Mantenimiento Combos de Prueba")

    def test_modulo_productos_mantenimiento(self):
        """Valida que desactivar el catálogo de productos muestre el aviso de mantenimiento en la plantilla."""
        from .models import ConfiguracionTienda
        config = ConfiguracionTienda.get_solo()
        config.modulo_productos_habilitado = False
        config.mensaje_mantenimiento_productos = "Mantenimiento Productos de Prueba"
        config.save()

        client = Client()
        response = client.get(reverse('lista_productos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Catálogo de Productos en Mantenimiento")
        self.assertContains(response, "Mantenimiento Productos de Prueba")

    def test_configuracion_envios_dinamica(self):
        """Valida que los cambios en ConfiguracionTienda alteren el cálculo del flete en el carrito."""
        from .models import ConfiguracionTienda
        config = ConfiguracionTienda.get_solo()
        config.monto_minimo_envio_gratis = 100000.0
        config.costo_envio_estandar = 8500.0
        config.save()

        # Usuario autenticado con carrito
        client = Client()
        client.force_login(self.user)
        response = client.get(reverse('ver_carrito'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['monto_minimo_envio_gratis'], 100000.0)
        self.assertEqual(response.context['costo_envio'], 8500.0)

    def test_producto_es_nuevo_badge(self):
        """Valida que un producto marcado con es_nuevo muestre la insignia de 'Nuevo' en el catálogo."""
        self.producto.es_nuevo = True
        self.producto.save()

        client = Client()
        response = client.get(reverse('lista_productos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "badge-nuevo")
        self.assertContains(response, "Nuevo")

    def test_sorpresas_dinamicas_y_lucky_pop(self):
        """Valida que las sorpresas en BD (incluyendo Lucky Pop) se carguen dinámicamente."""
        from .models import Categoria, Producto, Sorpresa
        cat_sorpresa, _ = Categoria.objects.get_or_create(nombre='Sorpresa')

        lucky_pop, _ = Producto.objects.update_or_create(
            nombre='Lucky Pop',
            defaults={
                'id_categoria': cat_sorpresa,
                'descripcion': '¡Gira la máquina de bolitas y saca 8 figuras!',
                'valor_unitario': 25000.0,
                'stock': 50,
                'es_nuevo': True,
                'activo': True,
            }
        )

        client = Client()
        response = client.get(reverse('lista_sorpresas'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Lucky Pop")
        self.assertContains(response, "25000")
        self.assertContains(response, "¡Gira la máquina de bolitas")
        self.assertIn(lucky_pop, response.context['sorpresas'])


class MetricasVentasExcelTests(TestCase):
    def setUp(self):
        import io
        import openpyxl
        self.openpyxl = openpyxl
        self.io = io

        self.client = Client()
        
        # Superusuario / Staff (PO de Costos / Admin)
        self.admin_user = User.objects.create_superuser(
            username='admin_finanzas@sorpresaskawaii.com',
            email='admin_finanzas@sorpresaskawaii.com',
            password='AdminPassword123!#'
        )

        # Usuario cliente regular (no staff)
        self.customer_user = User.objects.create_user(
            username='cliente_regular@ejemplo.com',
            email='cliente_regular@ejemplo.com',
            password='CustomerPassword123!#'
        )

        # Datos de prueba: Categorías y Productos
        from .models import Categoria, Producto, Combo, Pedido, DetallePedido
        self.cat_papeleria = Categoria.objects.create(nombre='Papelería Kawaii')
        self.cat_peluches = Categoria.objects.create(nombre='Peluches y Figuras')

        self.prod_cuaderno = Producto.objects.create(
            nombre='Cuaderno Cinnamoroll',
            id_categoria=self.cat_papeleria,
            valor_unitario=18000,
            stock=2,  # Stock bajo (< 5) -> debe disparar alerta
            activo=True
        )

        self.prod_peluche = Producto.objects.create(
            nombre='Peluche My Melody',
            id_categoria=self.cat_peluches,
            valor_unitario=45000,
            stock=20,
            activo=True
        )

        self.combo_especial = Combo.objects.create(
            nombre='Super Combo Sanrio',
            valor_combo=60000,
            activo=True
        )

        # Pedido 1: PAGADO (35.000 + 45.000)
        self.pedido_pagado = Pedido.objects.create(
            id_usuario=self.customer_user,
            valor_pagado=63000,
            estado='PAGADO',
            metodo_pago='Nequi',
            empresa_envio='Interrapidísimo',
            numero_guia='IR-100200300'
        )
        DetallePedido.objects.create(
            pedido=self.pedido_pagado,
            producto=self.prod_cuaderno,
            cantidad=1,
            precio_item=18000
        )
        DetallePedido.objects.create(
            pedido=self.pedido_pagado,
            producto=self.prod_peluche,
            cantidad=1,
            precio_item=45000
        )

        # Pedido 2: ENTREGADO (Combo)
        self.pedido_entregado = Pedido.objects.create(
            id_usuario=self.customer_user,
            valor_pagado=60000,
            estado='ENTREGADO',
            metodo_pago='Daviplata',
            empresa_envio='Servientrega',
            numero_guia='SE-998877'
        )
        DetallePedido.objects.create(
            pedido=self.pedido_entregado,
            combo=self.combo_especial,
            cantidad=1,
            precio_item=60000
        )

        # Pedido 3: PENDIENTE
        self.pedido_pendiente = Pedido.objects.create(
            id_usuario=self.customer_user,
            valor_pagado=18000,
            estado='PENDIENTE',
            metodo_pago='Efectivo'
        )
        DetallePedido.objects.create(
            pedido=self.pedido_pendiente,
            producto=self.prod_cuaderno,
            cantidad=1,
            precio_item=18000
        )

    def test_usuario_anonimo_no_puede_acceder_a_dashboard_ni_excel(self):
        """Valida que un usuario sin sesión sea redirigido a login al intentar ver métricas o descargar Excel."""
        resp_dashboard = self.client.get(reverse('admin_metricas_ventas'))
        self.assertEqual(resp_dashboard.status_code, 302)
        self.assertIn('/login/', resp_dashboard.url)

        resp_excel = self.client.get(reverse('admin_exportar_excel'))
        self.assertEqual(resp_excel.status_code, 302)
        self.assertIn('/login/', resp_excel.url)

    def test_usuario_cliente_no_staff_no_puede_acceder(self):
        """Valida que un cliente regular autenticado no pueda acceder a las métricas del panel de admin."""
        self.client.force_login(self.customer_user)
        resp_dashboard = self.client.get(reverse('admin_metricas_ventas'))
        self.assertEqual(resp_dashboard.status_code, 302)
        self.assertIn('/login/', resp_dashboard.url)

        resp_excel = self.client.get(reverse('admin_exportar_excel'))
        self.assertEqual(resp_excel.status_code, 302)

    def test_staff_accede_exitosamente_a_dashboard_con_kpis_correctos(self):
        """Valida que un usuario staff / admin acceda al dashboard y visualice los KPIs calculados."""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('admin_metricas_ventas') + '?rango=todo&estado=CONFIRMADOS')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Métricas y Reportes de Ventas")
        self.assertContains(response, "Descargar en Excel")

        # Ingresos confirmados: 63000 (PAGADO) + 60000 (ENTREGADO) = 123000
        self.assertEqual(response.context['resumen']['ingresos_confirmados'], 123000.0)
        self.assertEqual(response.context['resumen']['pedidos_pagados'], 2)
        self.assertEqual(response.context['resumen']['pedidos_pendientes'], 1)
        self.assertEqual(response.context['resumen']['ticket_promedio'], 61500.0)

        # Alerta de stock bajo (Cuaderno tiene stock=2)
        self.assertGreaterEqual(response.context['resumen']['productos_alerta_stock'], 1)
        self.assertContains(response, "Cuaderno Cinnamoroll")

    def test_exportacion_excel_genera_archivo_xlsx_valido_con_todas_las_hojas(self):
        """Valida que la descarga de Excel retorne un .xlsx bien estructurado con openpyxl y todas sus hojas."""
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse('admin_exportar_excel') + '?rango=todo&estado=TODOS')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertIn('attachment; filename="Reporte_Ventas_Sorpresas_Kawaii_', response['Content-Disposition'])

        # Cargar el archivo generado con openpyxl y verificar las hojas
        wb = self.openpyxl.load_workbook(self.io.BytesIO(response.content))
        sheet_names = wb.sheetnames

        self.assertIn('Resumen Ejecutivo', sheet_names)
        self.assertIn('Detalle de Pedidos', sheet_names)
        self.assertIn('Ventas por Producto', sheet_names)
        self.assertIn('Ventas por Combo', sheet_names)
        self.assertIn('Alertas de Stock', sheet_names)

        # Verificar contenido de hoja Resumen Ejecutivo
        ws_resumen = wb['Resumen Ejecutivo']
        self.assertIn('SORPRESAS KAWAII', ws_resumen['A1'].value)

        # Verificar hoja Detalle de Pedidos
        ws_pedidos = wb['Detalle de Pedidos']
        pedidos_en_excel = [ws_pedidos.cell(row=i, column=1).value for i in range(2, ws_pedidos.max_row + 1)]
        self.assertIn(self.pedido_pagado.codigo_pedido, pedidos_en_excel)
        self.assertIn(self.pedido_entregado.codigo_pedido, pedidos_en_excel)

        # Verificar hoja Alertas de Stock
        ws_alertas = wb['Alertas de Stock']
        productos_en_alerta = [ws_alertas.cell(row=i, column=1).value for i in range(2, ws_alertas.max_row + 1)]
        self.assertIn('Cuaderno Cinnamoroll', productos_en_alerta)

    def test_filtros_metricas_por_fecha_personalizada(self):
        """Valida que los filtros por rango de fecha y estado se apliquen con precisión."""
        self.client.force_login(self.admin_user)
        from datetime import date
        hoy_str = date.today().strftime('%Y-%m-%d')

        response = self.client.get(
            reverse('admin_metricas_ventas') + f'?rango=personalizado&fecha_inicio={hoy_str}&fecha_fin={hoy_str}&estado=TODOS'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['resumen']['total_pedidos'], 3)

    def test_admin_action_exportar_pedidos_seleccionados(self):
        """Valida que la acción de exportar seleccionados en PedidoAdmin retorne un archivo Excel válido."""
        from django.test.client import RequestFactory
        from .admin import PedidoAdmin
        from .models import Pedido
        from django.contrib.admin.sites import AdminSite

        factory = RequestFactory()
        request = factory.get('/admin/sorpresas_kawai/pedido/')
        request.user = self.admin_user

        site = AdminSite()
        pedido_admin = PedidoAdmin(Pedido, site)
        
        queryset = Pedido.objects.filter(id__in=[self.pedido_pagado.id, self.pedido_entregado.id])
        excel_response = pedido_admin.exportar_pedidos_seleccionados_excel(request, queryset)

        self.assertEqual(excel_response.status_code, 200)
        self.assertEqual(excel_response['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        
        wb = self.openpyxl.load_workbook(self.io.BytesIO(excel_response.content))
        ws_pedidos = wb['Detalle de Pedidos']
        self.assertEqual(ws_pedidos.max_row, 3) # Encabezado + 2 filas

    def test_enviar_correo_alerta_stock_bajo_directo(self):
        """Valida que enviar_correo_alerta_stock_bajo envíe un correo formateado con los productos críticos."""
        from django.core import mail
        from django.test import override_settings
        from .emails import enviar_correo_alerta_stock_bajo

        mail.outbox = []
        with override_settings(ADMIN_EMAIL='admin_stock@sorpresaskawaii.com'):
            resultado = enviar_correo_alerta_stock_bajo([self.prod_cuaderno], motivo="Prueba Directa")

        self.assertTrue(resultado)
        self.assertEqual(len(mail.outbox), 1)
        email_enviado = mail.outbox[0]
        self.assertEqual(email_enviado.to, ['admin_stock@sorpresaskawaii.com'])
        self.assertIn("ALERTA DE STOCK", email_enviado.subject)
        self.assertIn("Cuaderno Cinnamoroll", email_enviado.body)
        self.assertIn("CRÍTICO", email_enviado.body)

    def test_compra_que_deja_stock_bajo_dispara_correo_automatico_de_alerta(self):
        """Valida que una compra reduzca stock y despache correo de alerta si el stock cae a <= 5."""
        from django.core import mail
        from django.test import override_settings
        from .models import ConfiguracionTienda, CarritoDeCompras, ItemCarrito
        
        config = ConfiguracionTienda.get_solo()
        config.compras_habilitadas = True
        config.save()

        # Peluche tiene stock=20, compramos 17 para que quede en stock=3 (<= 5)
        client = Client()
        client.force_login(self.customer_user)
        carrito, _ = CarritoDeCompras.objects.get_or_create(usuario=self.customer_user)
        ItemCarrito.objects.create(carrito=carrito, producto=self.prod_peluche, cantidad=17)

        mail.outbox = []
        with override_settings(ADMIN_EMAIL='admin_alertas@sorpresaskawaii.com'):
            response = client.post(reverse('finalizar_compra'))

        self.assertEqual(response.status_code, 302)
        self.prod_peluche.refresh_from_db()
        self.assertEqual(self.prod_peluche.stock, 3)

        # Se deben haber enviado 3 correos: confirmación al cliente, nuevo pedido al admin, y alerta de stock bajo
        self.assertEqual(len(mail.outbox), 3)
        asuntos = [msg.subject for msg in mail.outbox]
        self.assertTrue(any("ALERTA DE STOCK" in a or "CRÍTICO" in a for a in asuntos))

    def test_enviar_alerta_stock_email_manual_desde_dashboard(self):
        """Valida que el botón manual del dashboard despache el correo de alerta de inventario a ADMIN_EMAIL."""
        from django.core import mail
        from django.test import override_settings
        
        self.client.force_login(self.admin_user)
        mail.outbox = []

        with override_settings(ADMIN_EMAIL='admin_manual@sorpresaskawaii.com'):
            response = self.client.get(reverse('admin_enviar_alerta_stock'), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ['admin_manual@sorpresaskawaii.com'])
        self.assertIn("Cuaderno Cinnamoroll", email.body)

    def test_admin_action_enviar_alerta_stock_en_productoadmin(self):
        """Valida la acción de Django Admin para enviar alerta de stock por correo de los productos seleccionados."""
        from django.test.client import RequestFactory
        from django.core import mail
        from django.test import override_settings
        from .admin import ProductoAdmin
        from .models import Producto
        from django.contrib.admin.sites import AdminSite

        factory = RequestFactory()
        request = factory.get('/admin/sorpresas_kawai/producto/')
        request.user = self.admin_user
        from django.contrib.messages.storage.fallback import FallbackStorage
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)

        site = AdminSite()
        prod_admin = ProductoAdmin(Producto, site)
        
        mail.outbox = []
        with override_settings(ADMIN_EMAIL='admin_action@sorpresaskawaii.com'):
            queryset = Producto.objects.filter(id=self.prod_cuaderno.id)
            prod_admin.enviar_alerta_stock_email_action(request, queryset)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ['admin_action@sorpresaskawaii.com'])
        self.assertIn("Cuaderno Cinnamoroll", mail.outbox[0].body)









