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

    def test_finalizar_compra_envia_correo_a_cliente_y_admin(self):
        """Valida que al finalizar una compra se despachen correos tanto al cliente como al administrador."""
        from django.test import override_settings

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



