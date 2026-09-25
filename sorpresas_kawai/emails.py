import re
from django.core.mail import send_mail
from django.conf import settings


def _obtener_items_pedido_texto(pedido):
    """Obtiene la lista formateada en texto de los ítems del pedido."""
    items_info = []
    for detalle in pedido.detalles.all():
        nombre = detalle.producto.nombre if detalle.producto else (
            detalle.combo.nombre if detalle.combo else 'Ítem'
        )
        items_info.append(f"• {detalle.cantidad}x {nombre} - ${detalle.precio_item:,.0f} COP c/u")

    if not items_info:
        if pedido.combo_opcional:
            items_info.append(f"• 1x {pedido.combo_opcional.nombre}")
        elif pedido.id_producto_opcional:
            items_info.append(f"• 1x {pedido.id_producto_opcional.nombre}")

    return "\n".join(items_info) if items_info else "• Artículos registrados en el sistema"


def _obtener_items_pedido_html(pedido):
    """Genera filas HTML con el listado de productos para correos electrónicos."""
    rows = []
    for detalle in pedido.detalles.all():
        nombre = detalle.producto.nombre if detalle.producto else (
            detalle.combo.nombre if detalle.combo else 'Ítem'
        )
        total_linea = detalle.cantidad * detalle.precio_item
        rows.append(
            f'<tr>'
            f'<td style="padding: 10px 12px; border-bottom: 1px solid #f3e6f0; color: #2d2030; font-size: 14px;"><strong>{nombre}</strong></td>'
            f'<td style="padding: 10px 12px; border-bottom: 1px solid #f3e6f0; text-align: center; color: #6f6273; font-size: 14px;">{detalle.cantidad}</td>'
            f'<td style="padding: 10px 12px; border-bottom: 1px solid #f3e6f0; text-align: right; color: #e94fa3; font-weight: 600; font-size: 14px;">${total_linea:,.0f} COP</td>'
            f'</tr>'
        )
    if not rows:
        rows.append(
            '<tr><td colspan="3" style="padding: 10px 12px; color: #6f6273; font-size: 14px;">Artículos registrados en el sistema</td></tr>'
        )
    return "".join(rows)


def _construir_plantilla_base_html(titulo_banner, encabezado, cuerpo_principal, pedido, extras_html=""):
    """Plantilla de correo con estética Kawaii profesional y diseño responsive."""
    items_html = _obtener_items_pedido_html(pedido)
    nombre_cliente = pedido.id_usuario.first_name or pedido.id_usuario.username

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo_banner}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #fcf6fc; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #fcf6fc; padding: 30px 10px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 8px 30px rgba(233, 79, 163, 0.1); border: 1px solid #fae6f2; max-width: 600px; width: 100%;">
                    <!-- Header Kawaii -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #ff70af 0%, #e94fa3 100%); padding: 28px 24px; text-align: center;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 26px; font-weight: 800; letter-spacing: -0.5px;">
                                ✏️ Edukit · <span style="color: #fff0f7;">Sorpresas Kawaii</span>
                            </h1>
                            <p style="color: #ffe6f3; margin: 6px 0 0 0; font-size: 14px; font-weight: 500;">
                                {titulo_banner}
                            </p>
                        </td>
                    </tr>

                    <!-- Contenido Principal -->
                    <tr>
                        <td style="padding: 32px 28px;">
                            <h2 style="color: #2d2030; font-size: 20px; margin: 0 0 12px 0;">{encabezado}</h2>
                            <p style="color: #4a3e4e; font-size: 15px; line-height: 1.6; margin: 0 0 20px 0;">
                                Hola <strong>{nombre_cliente}</strong>,<br>
                                {cuerpo_principal}
                            </p>

                            <!-- Bloque de Estado / Código -->
                            <div style="background-color: #fff0f7; border-left: 4px solid #e94fa3; border-radius: 8px; padding: 14px 18px; margin-bottom: 24px;">
                                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                    <tr>
                                        <td style="font-size: 14px; color: #6f6273;">N° de Pedido:</td>
                                        <td align="right" style="font-size: 15px; font-weight: bold; color: #e94fa3;">{pedido.codigo_pedido}</td>
                                    </tr>
                                    <tr>
                                        <td style="font-size: 14px; color: #6f6273; padding-top: 6px;">Estado actual:</td>
                                        <td align="right" style="font-size: 14px; font-weight: bold; color: #2d2030; padding-top: 6px;">{pedido.get_estado_display()}</td>
                                    </tr>
                                </table>
                            </div>

                            {extras_html}

                            <!-- Tabla de Artículos -->
                            <h3 style="color: #2d2030; font-size: 16px; margin: 24px 0 12px 0; border-bottom: 2px solid #fae6f2; padding-bottom: 8px;">
                                🛍️ Resumen de Artículos
                            </h3>
                            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-collapse: collapse; margin-bottom: 20px;">
                                <thead>
                                    <tr style="background-color: #faf2f8;">
                                        <th align="left" style="padding: 8px 12px; font-size: 12px; color: #6f6273; text-transform: uppercase;">Producto</th>
                                        <th align="center" style="padding: 8px 12px; font-size: 12px; color: #6f6273; text-transform: uppercase;">Cant.</th>
                                        <th align="right" style="padding: 8px 12px; font-size: 12px; color: #6f6273; text-transform: uppercase;">Total</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {items_html}
                                </tbody>
                                <tfoot>
                                    <tr>
                                        <td colspan="2" style="padding: 14px 12px; font-size: 16px; font-weight: bold; color: #2d2030; border-top: 2px solid #e94fa3;">Total a Pagar:</td>
                                        <td align="right" style="padding: 14px 12px; font-size: 18px; font-weight: 800; color: #e94fa3; border-top: 2px solid #e94fa3;">${pedido.valor_pagado:,.0f} COP</td>
                                    </tr>
                                </tfoot>
                            </table>

                            <!-- Botón y contacto -->
                            <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #f3e6f0;">
                                <p style="color: #6f6273; font-size: 13px; margin: 0 0 15px 0;">
                                    Puedes ver el estado en vivo de tu compra en cualquier momento ingresando a tu cuenta en la sección <strong>Mis Pedidos</strong>.
                                </p>
                                <!-- Botón WhatsApp (utiliza settings.WHATSAPP_PHONE_NUMBER) -->
                                <a href="https://wa.me/{re.sub(r'\\D', '', str(getattr(settings, 'WHATSAPP_PHONE_NUMBER', '573222385508')))}" style="display: inline-block; background-color: #25D366; color: #ffffff; text-decoration: none; font-weight: bold; font-size: 14px; padding: 11px 22px; border-radius: 50px; box-shadow: 0 4px 14px rgba(37, 211, 102, 0.3);">
                                    💬 Contactar por WhatsApp
                                </a>
                            </div>
                        </td>
                    </tr>

                    <!-- Footer del Correo -->
                    <tr>
                        <td style="background-color: #faf2f8; padding: 20px; text-align: center; border-top: 1px solid #fae6f2;">
                            <p style="color: #9a8d9f; font-size: 12px; margin: 0;">
                                ¡Gracias por hacer tus días más felices y kawaii! ✨<br>
                                © Edukit · Sorpresas Kawaii - Tienda Online de Detalles y Accesorios
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""


def enviar_correo_confirmacion_compra(pedido):
    """Envía el correo de confirmación inicial tras realizar el pedido."""
    if not pedido.id_usuario or not pedido.id_usuario.email:
        return False

    cliente = pedido.id_usuario.first_name or pedido.id_usuario.username
    items_texto = _obtener_items_pedido_texto(pedido)

    asunto = f"¡Gracias por tu compra en Sorpresas Kawaii! Pedido {pedido.codigo_pedido}"

    mensaje_plano = (
        f"¡Hola {cliente}!\n\n"
        f"Gracias por confiar en nosotros y apoyar a Sorpresas Kawaii. Tu pedido ha sido registrado con éxito.\n\n"
        f"DETALLES DE TU PEDIDO {pedido.codigo_pedido}:\n"
        f"--------------------------------------------------\n"
        f"{items_texto}\n\n"
        f"Total a Pagar: ${pedido.valor_pagado:,.0f} COP\n"
        f"Estado del Pedido: {pedido.get_estado_display()}\n"
        f"--------------------------------------------------\n\n"
        # f"Para coordinar el pago y despacho de tu pedido, puedes escribirnos directamente por WhatsApp al +57 322 238 5508.\n\n"
        f"Para coordinar el pago y despacho de tu pedido, puedes escribirnos directamente por WhatsApp.\n\n"
        f"Puedes consultar el avance de tu paquete en cualquier momento desde 'Mis Pedidos' en nuestra tienda web.\n\n"
        f"¡Que tengas un día muy kawaii!\n"
        f"El equipo de Sorpresas Kawaii ✨"
    )

    cuerpo_html = _construir_plantilla_base_html(
        titulo_banner="¡Pedido Registrado con Éxito! 🛍️",
        encabezado="¡Gracias por tu compra!",
        cuerpo_principal="Hemos recibido tu orden y estamos listos para procesarla. Para confirmar tu pago o enviar tu comprobante, comunícate con nosotros por WhatsApp.",
        pedido=pedido
    )

    try:
        send_mail(
            subject=asunto,
            message=mensaje_plano,
            html_message=cuerpo_html,
            from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@sorpresaskawaii.com',
            recipient_list=[pedido.id_usuario.email],
            fail_silently=True,
        )
        return True
    except Exception:
        return False


def enviar_correo_actualizacion_pedido(pedido, estado_anterior=None, info_rastreo_actualizada=False):
    """
    Envía una notificación por correo electrónico cuando cambia el estado del pedido
    (PAGADO, ENVIADO, ENTREGADO, CANCELADO) o cuando se actualiza la información de guía.
    """
    if not pedido.id_usuario or not pedido.id_usuario.email:
        return False

    cliente = pedido.id_usuario.first_name or pedido.id_usuario.username
    items_texto = _obtener_items_pedido_texto(pedido)
    estado = pedido.estado

    extras_html = ""

    if estado == 'ENVIADO' or info_rastreo_actualizada:
        empresa = pedido.empresa_envio or "Por confirmar"
        guia = pedido.numero_guia or "Por asignar"
        asunto = f"🚚 ¡Tu pedido {pedido.codigo_pedido} ha sido enviado! | Sorpresas Kawaii"
        titulo_banner = "¡Tu Pedido está en Camino! 🚚✨"
        encabezado = "¡Buenas noticias! Tu paquete fue despachado"
        cuerpo_principal = (
            "Tu paquete ha sido entregado a la transportadora y va rumbo a tu dirección. "
            "A continuación encuentras los datos de envío y número de guía para que puedas realizar el seguimiento."
        )
        extras_html = f"""
        <div style="background-color: #f6f0ff; border: 1.5px dashed #8c52ff; border-radius: 10px; padding: 16px 20px; margin-bottom: 24px;">
            <h4 style="color: #7a3ee6; margin: 0 0 10px 0; font-size: 15px;">📦 Información de Rastreo:</h4>
            <p style="margin: 4px 0; font-size: 14px; color: #2d2030;"><strong>Empresa de Envío:</strong> {empresa}</p>
            <p style="margin: 4px 0; font-size: 14px; color: #2d2030;"><strong>Número de Guía:</strong> <span style="color: #e94fa3; font-weight: bold; font-size: 15px;">{guia}</span></p>
        </div>
        """
        mensaje_plano = (
            f"¡Hola {cliente}!\n\n"
            f"¡Tu pedido {pedido.codigo_pedido} ya ha sido enviado y está en camino! 🚚✨\n\n"
            f"DATOS DE RASTREO:\n"
            f"--------------------------------------------------\n"
            f"Empresa de Envío: {empresa}\n"
            f"Número de Guía: {guia}\n"
            f"--------------------------------------------------\n\n"
            f"ARTÍCULOS ENVIADOS:\n"
            f"{items_texto}\n\n"
            f"Total: ${pedido.valor_pagado:,.0f} COP\n\n"
            f"Puedes ver la información en tiempo real en la sección 'Mis Pedidos' de nuestra web.\n\n"
            f"¡El equipo de Sorpresas Kawaii ✨!"
        )

    elif estado == 'ENTREGADO':
        asunto = f"🎁 ¡Tu pedido {pedido.codigo_pedido} ha sido entregado! | Sorpresas Kawaii"
        titulo_banner = "¡Pedido Entregado! 🎁💖"
        encabezado = "¡Esperamos que te encante tu sorpresa!"
        cuerpo_principal = (
            "Tu paquete ha sido marcado como entregado con éxito. "
            "Esperamos de todo corazón que disfrutes mucho de cada uno de tus productos. "
            "¡Muchísimas gracias por apoyar a Sorpresas Kawaii!"
        )
        mensaje_plano = (
            f"¡Hola {cliente}!\n\n"
            f"Nos alegra contarte que tu pedido {pedido.codigo_pedido} ha sido entregado con éxito. 🎁💖\n\n"
            f"RESUMEN DE ARTÍCULOS:\n"
            f"{items_texto}\n\n"
            f"Total: ${pedido.valor_pagado:,.0f} COP\n\n"
            f"Esperamos que disfrutes mucho tu compra. Si tienes cualquier consulta o inquietud, "
            # f"puedes escribirnos por WhatsApp al +57 322 238 5508.\n\n"
            f"puedes escribirnos directamente a nuestra línea de WhatsApp.\n\n"
            f"¡El equipo de Sorpresas Kawaii ✨!"
        )

    elif estado == 'CANCELADO':
        asunto = f"❌ Actualización: Pedido {pedido.codigo_pedido} Cancelado | Sorpresas Kawaii"
        titulo_banner = "Actualización de Pedido ❌"
        encabezado = "Tu pedido ha sido cancelado"
        cuerpo_principal = (
            "Te informamos que tu pedido ha sido cancelado en el sistema. "
            "Si tienes alguna duda o crees que se trata de un error, por favor escríbenos a nuestra línea de WhatsApp."
        )
        mensaje_plano = (
            f"¡Hola {cliente}!\n\n"
            f"Te informamos que tu pedido {pedido.codigo_pedido} en Sorpresas Kawaii ha sido cancelado.\n\n"
            f"DETALLES:\n"
            f"Pedido: {pedido.codigo_pedido}\n"
            f"Estado: Cancelado ❌\n"
            f"Total: ${pedido.valor_pagado:,.0f} COP\n\n"
            # f"Si requieres asistencia, contáctanos a nuestro WhatsApp oficial: +57 322 238 5508.\n\n"
            f"Si requieres asistencia, contáctanos directamente a nuestra línea de atención en WhatsApp.\n\n"
            f"El equipo de Sorpresas Kawaii ✨"
        )

    elif estado == 'PAGADO':
        asunto = f"✅ Pago Confirmado - Pedido {pedido.codigo_pedido} | Sorpresas Kawaii"
        titulo_banner = "¡Pago Confirmado con Éxito! ✅"
        encabezado = "Hemos verificado tu pago"
        cuerpo_principal = (
            "Tu pago ha sido validado correctamente. Ya estamos preparando tu paquete con mucho amor y cuidado "
            "para despacharlo lo antes posible."
        )
        mensaje_plano = (
            f"¡Hola {cliente}!\n\n"
            f"¡Hemos verificado y confirmado el pago de tu pedido {pedido.codigo_pedido}! ✅🎉\n\n"
            f"Tu paquete ya se encuentra en proceso de alistamiento.\n\n"
            f"RESUMEN:\n"
            f"{items_texto}\n\n"
            f"Total: ${pedido.valor_pagado:,.0f} COP\n"
            f"Estado: Pagado ✅\n\n"
            f"Te enviaremos otro correo con la guía cuando el paquete sea despachado.\n\n"
            f"El equipo de Sorpresas Kawaii ✨"
        )

    else:
        asunto = f"📦 Actualización de tu pedido {pedido.codigo_pedido} | Sorpresas Kawaii"
        titulo_banner = "Actualización de tu Pedido 📦"
        encabezado = f"Estado actualizado: {pedido.get_estado_display()}"
        cuerpo_principal = (
            f"Tu pedido ha cambiado de estado a: <strong>{pedido.get_estado_display()}</strong>."
        )
        mensaje_plano = (
            f"¡Hola {cliente}!\n\n"
            f"El estado de tu pedido {pedido.codigo_pedido} ha sido actualizado a: {pedido.get_estado_display()}.\n\n"
            f"Total: ${pedido.valor_pagado:,.0f} COP\n\n"
            f"El equipo de Sorpresas Kawaii ✨"
        )

    cuerpo_html = _construir_plantilla_base_html(
        titulo_banner=titulo_banner,
        encabezado=encabezado,
        cuerpo_principal=cuerpo_principal,
        pedido=pedido,
        extras_html=extras_html
    )

    try:
        send_mail(
            subject=asunto,
            message=mensaje_plano,
            html_message=cuerpo_html,
            from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@sorpresaskawaii.com',
            recipient_list=[pedido.id_usuario.email],
            fail_silently=True,
        )
        return True
    except Exception:
        return False


def _obtener_destinatarios_admin():
    """Obtiene la lista de correos electrónicos de administradores configurados."""
    destinatarios = []
    admin_email_conf = getattr(settings, 'ADMIN_EMAIL', None)
    
    if admin_email_conf:
        if isinstance(admin_email_conf, (list, tuple)):
            destinatarios.extend([e.strip() for e in admin_email_conf if e and e.strip()])
        elif isinstance(admin_email_conf, str):
            destinatarios.extend([e.strip() for e in admin_email_conf.split(',') if e.strip()])

    if not destinatarios:
        try:
            from django.contrib.auth.models import User
            staff_emails = list(
                User.objects.filter(is_staff=True)
                .exclude(email__isnull=True)
                .exclude(email='')
                .values_list('email', flat=True)
            )
            destinatarios.extend(staff_emails)
        except Exception:
            pass

    if not destinatarios and getattr(settings, 'DEFAULT_FROM_EMAIL', None):
        destinatarios.append(settings.DEFAULT_FROM_EMAIL)

    # Eliminar duplicados preservando orden
    return list(dict.fromkeys([d for d in destinatarios if d]))


def enviar_correo_nuevo_pedido_administrador(pedido):
    """
    Envía una notificación detallada por correo al administrador de la tienda
    cuando un cliente realiza un nuevo pedido para su revisión y confirmación.
    """
    destinatarios = _obtener_destinatarios_admin()
    if not destinatarios:
        return False

    cliente = pedido.id_usuario
    fecha_pedido_str = pedido.fecha_pedido.strftime("%d/%m/%Y %I:%M %p") if hasattr(pedido, 'fecha_pedido') and pedido.fecha_pedido else "Reciente"
    
    items_texto = _obtener_items_pedido_texto(pedido)
    items_html = _obtener_items_pedido_html(pedido)

    asunto = f"🔔 [Nuevo Pedido {pedido.codigo_pedido}] {cliente.username} - ${pedido.valor_pagado:,.0f} COP"

    mensaje_plano = (
        f"¡Hola Administrador!\n\n"
        f"Se ha registrado un nuevo pedido en Sorpresas Kawaii y requiere tu atención:\n\n"
        f"DATOS DEL PEDIDO:\n"
        f"--------------------------------------------------\n"
        f"Código: {pedido.codigo_pedido}\n"
        f"Fecha: {fecha_pedido_str}\n"
        f"Estado actual: {pedido.get_estado_display()}\n"
        f"Método de pago: {pedido.metodo_pago or 'No especificado'}\n"
        f"Total: ${pedido.valor_pagado:,.0f} COP\n"
        f"--------------------------------------------------\n\n"
        f"DATOS DEL CLIENTE:\n"
        f"--------------------------------------------------\n"
        f"Usuario: {cliente.username}\n"
        f"--------------------------------------------------\n\n"
        f"ARTÍCULOS SOLICITADOS:\n"
        f"{items_texto}\n\n"
        f"Para gestionar este pedido, ingresa al panel de administración de Django:\n"
        f"/admin/sorpresas_kawai/pedido/{pedido.id}/change/\n\n"
        f"Sorpresas Kawaii - Sistema de Notificaciones"
    )

    cuerpo_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nuevo Pedido Recibido</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f6f2f9; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f6f2f9; padding: 30px 10px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 8px 30px rgba(140, 82, 255, 0.12); border: 1px solid #ebd9f7; max-width: 600px; width: 100%;">
                    <!-- Header Notificación Admin -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #8c52ff 0%, #e94fa3 100%); padding: 28px 24px; text-align: center;">
                            <span style="display: inline-block; background-color: rgba(255,255,255,0.2); color: #ffffff; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; padding: 4px 12px; border-radius: 20px; margin-bottom: 8px;">
                                👑 Alerta de Administración
                            </span>
                            <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 800; letter-spacing: -0.5px;">
                                ¡Nuevo Pedido Recibido! 🛍️
                            </h1>
                            <p style="color: #f7e8ff; margin: 6px 0 0 0; font-size: 14px; font-weight: 500;">
                                Código de Pedido: <strong>{pedido.codigo_pedido}</strong>
                            </p>
                        </td>
                    </tr>

                    <!-- Contenido Principal -->
                    <tr>
                        <td style="padding: 32px 28px;">
                            <p style="color: #4a3e4e; font-size: 15px; line-height: 1.6; margin: 0 0 20px 0;">
                                Se ha generado un nuevo pedido en la tienda web. A continuación tienes los detalles completos para su revisión y confirmación:
                            </p>

                            <!-- Ficha de Datos del Cliente -->
                            <div style="background-color: #fcf8ff; border: 1px solid #ebd9f7; border-left: 4px solid #8c52ff; border-radius: 10px; padding: 16px 20px; margin-bottom: 24px;">
                                <h3 style="color: #6a2ec8; margin: 0 0 12px 0; font-size: 15px; font-weight: 700;">
                                    👤 Datos del Cliente
                                </h3>
                                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="font-size: 14px; color: #3a2e3f;">
                                    <tr>
                                        <td style="padding: 4px 0; color: #7f6e86; width: 35%;">Usuario:</td>
                                        <td style="padding: 4px 0; font-weight: 600;">{cliente.username}</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 4px 0; color: #7f6e86;">Fecha:</td>
                                        <td style="padding: 4px 0;">{fecha_pedido_str}</td>
                                    </tr>
                                    <tr>
                                        <td style="padding: 4px 0; color: #7f6e86;">Método de Pago:</td>
                                        <td style="padding: 4px 0; font-weight: 600; color: #2d2030;">{pedido.metodo_pago or 'No especificado'}</td>
                                    </tr>
                                </table>
                            </div>

                            <!-- Tabla de Artículos -->
                            <h3 style="color: #2d2030; font-size: 16px; margin: 24px 0 12px 0; border-bottom: 2px solid #ebd9f7; padding-bottom: 8px;">
                                📦 Artículos del Pedido
                            </h3>
                            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-collapse: collapse; margin-bottom: 20px;">
                                <thead>
                                    <tr style="background-color: #f7effd;">
                                        <th align="left" style="padding: 8px 12px; font-size: 12px; color: #6f5880; text-transform: uppercase;">Producto</th>
                                        <th align="center" style="padding: 8px 12px; font-size: 12px; color: #6f5880; text-transform: uppercase;">Cant.</th>
                                        <th align="right" style="padding: 8px 12px; font-size: 12px; color: #6f5880; text-transform: uppercase;">Total</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {items_html}
                                </tbody>
                                <tfoot>
                                    <tr>
                                        <td colspan="2" style="padding: 14px 12px; font-size: 16px; font-weight: bold; color: #2d2030; border-top: 2px solid #8c52ff;">Total del Pedido:</td>
                                        <td align="right" style="padding: 14px 12px; font-size: 18px; font-weight: 800; color: #8c52ff; border-top: 2px solid #8c52ff;">${pedido.valor_pagado:,.0f} COP</td>
                                    </tr>
                                </tfoot>
                            </table>

                            <!-- Botón de Gestión en Django Admin -->
                            <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ebd9f7;">
                                <p style="color: #6f5880; font-size: 13px; margin: 0 0 15px 0;">
                                    Haz clic a continuación para revisar el pedido, confirmar el pago o asignar la guía de despacho:
                                </p>
                                <a href="/admin/sorpresas_kawai/pedido/{pedido.id}/change/" style="display: inline-block; background: linear-gradient(135deg, #8c52ff 0%, #e94fa3 100%); color: #ffffff; text-decoration: none; font-weight: bold; font-size: 14px; padding: 12px 26px; border-radius: 50px; box-shadow: 0 4px 14px rgba(140, 82, 255, 0.35);">
                                    ⚙️ Gestionar Pedido en el Panel Admin
                                </a>
                            </div>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f7effd; padding: 18px; text-align: center; border-top: 1px solid #ebd9f7;">
                            <p style="color: #9a88a8; font-size: 12px; margin: 0;">
                                Panel de Control de Sorpresas Kawaii • Notificación Interna Automática
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

    try:
        send_mail(
            subject=asunto,
            message=mensaje_plano,
            html_message=cuerpo_html,
            from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@sorpresaskawaii.com',
            recipient_list=destinatarios,
            fail_silently=True,
        )
        return True
    except Exception:
        return False


def enviar_correo_alerta_stock_bajo(productos, motivo="Actualización de Inventario", pedido=None):
    """
    Envía un correo de alerta de inventario crítico al administrador / PO de Costos
    cuando uno o más artículos alcanzan existencias mínimas (<= 5 unidades o agotado).
    """
    if not productos:
        return False

    if not isinstance(productos, (list, tuple, set)) and hasattr(productos, 'nombre'):
        productos = [productos]

    destinatario = getattr(settings, 'ADMIN_EMAIL', None) or settings.DEFAULT_FROM_EMAIL
    if not destinatario:
        return False

    destinatarios = [d.strip() for d in str(destinatario).split(',') if d.strip()]
    if not destinatarios:
        return False

    total_alertas = len(productos)
    agotados_count = sum(1 for p in productos if p.stock <= 0)

    if agotados_count > 0:
        asunto = f"🚨 URGENTE: {agotados_count} producto(s) AGOTADO(S) en Sorpresas Kawaii"
    else:
        asunto = f"⚠️ ALERTA DE STOCK: {total_alertas} producto(s) con inventario bajo en Sorpresas Kawaii"

    filas_html = []
    lineas_texto = []

    for p in productos:
        cat_nombre = p.id_categoria.nombre if p.id_categoria else "Sin Categoría"
        if p.stock <= 0:
            badge_color = "#fee2e2"
            badge_text_color = "#b91c1c"
            estado_texto = "🚨 AGOTADO (0 un.)"
            accion_sugerida = "Reabastecer de inmediato con el proveedor."
        elif p.stock <= 3:
            badge_color = "#fee2e2"
            badge_text_color = "#b91c1c"
            estado_texto = f"⚠️ CRÍTICO ({p.stock} un.)"
            accion_sugerida = "Ordenar reposición urgente a distribuidor."
        else:
            badge_color = "#fef9c3"
            badge_text_color = "#854d0e"
            estado_texto = f"⚡ BAJO ({p.stock} un.)"
            accion_sugerida = "Monitorear rotación y programar compra."

        filas_html.append(f"""
        <tr style="border-bottom: 1px solid #fed7e2;">
            <td style="padding: 12px 10px; font-size: 14px; color: #1e293b;">
                <strong>{p.nombre}</strong><br>
                <span style="font-size: 12px; color: #64748b;">{cat_nombre}</span>
            </td>
            <td align="center" style="padding: 12px 10px;">
                <span style="background-color: {badge_color}; color: {badge_text_color}; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: bold; display: inline-block;">
                    {estado_texto}
                </span>
            </td>
            <td align="right" style="padding: 12px 10px; font-size: 14px; color: #047857; font-weight: 600;">
                ${p.valor_unitario:,.0f} COP
            </td>
            <td style="padding: 12px 10px; font-size: 12px; color: #475569;">
                {accion_sugerida}
            </td>
        </tr>
        """)

        lineas_texto.append(f"- {p.nombre} ({cat_nombre}): {estado_texto} | Precio: ${p.valor_unitario:,.0f} COP | {accion_sugerida}")

    filas_html_str = "".join(filas_html)
    lineas_texto_str = "\n".join(lineas_texto)

    info_origen_html = ""
    info_origen_txt = ""
    if pedido:
        info_origen_html = f"""
        <div style="background-color: #fff5f8; border: 1px solid #fbcfe8; border-radius: 8px; padding: 12px 16px; margin-bottom: 20px;">
            <p style="margin: 0; font-size: 13px; color: #831843;">
                🛒 <strong>Disparado por orden de compra:</strong> Pedido <strong>{pedido.codigo_pedido}</strong> ({pedido.id_usuario.username}).
            </p>
        </div>
        """
        info_origen_txt = f"\nDisparado tras el pedido {pedido.codigo_pedido} ({pedido.id_usuario.username}).\n"

    cuerpo_html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{asunto}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f8fafc; padding: 30px 10px;">
        <tr>
            <td align="center">
                <table width="640" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08); border: 1px solid #e2e8f0; max-width: 640px; width: 100%;">
                    <!-- Header Alerta -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #be185d 0%, #dc2626 100%); padding: 26px 24px; text-align: center;">
                            <h1 style="color: #ffffff; margin: 0; font-size: 24px; font-weight: 800; letter-spacing: -0.5px;">
                                ⚠️ ALERTA DE INVENTARIO
                            </h1>
                            <p style="color: #fef2f2; margin: 6px 0 0 0; font-size: 14px; font-weight: 500;">
                                Sorpresas Kawaii · Notificación de Stock Crítico
                            </p>
                        </td>
                    </tr>

                    <!-- Contenido Principal -->
                    <tr>
                        <td style="padding: 28px 24px;">
                            <h2 style="color: #1e293b; font-size: 18px; margin: 0 0 10px 0;">
                                Atención Equipo de Administración y Costos,
                            </h2>
                            <p style="color: #475569; font-size: 14px; line-height: 1.6; margin: 0 0 18px 0;">
                                Se ha detectado que <strong>{total_alertas} producto(s)</strong> han alcanzado o superado el umbral de existencias mínimas (&le; 5 unidades o agotado). Te recomendamos gestionar la reposición con los proveedores para evitar pérdidas de ventas.
                            </p>

                            {info_origen_html}

                            <!-- Tabla de Productos Afectados -->
                            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="border-collapse: collapse; margin-bottom: 24px; border: 1px solid #fed7e2; border-radius: 8px; overflow: hidden;">
                                <thead>
                                    <tr style="background-color: #fff1f2;">
                                        <th align="left" style="padding: 10px 10px; font-size: 11px; color: #9f1239; text-transform: uppercase;">Producto</th>
                                        <th align="center" style="padding: 10px 10px; font-size: 11px; color: #9f1239; text-transform: uppercase;">Estado Stock</th>
                                        <th align="right" style="padding: 10px 10px; font-size: 11px; color: #9f1239; text-transform: uppercase;">Precio</th>
                                        <th align="left" style="padding: 10px 10px; font-size: 11px; color: #9f1239; text-transform: uppercase;">Acción Sugerida</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filas_html_str}
                                </tbody>
                            </table>

                            <!-- Botones de Acción en Admin -->
                            <div style="text-align: center; margin-top: 24px; padding-top: 18px; border-top: 1px solid #f1f5f9;">
                                <a href="/admin/metricas-ventas/" style="display: inline-block; background: linear-gradient(135deg, #be185d 0%, #831843 100%); color: #ffffff; text-decoration: none; font-weight: bold; font-size: 14px; padding: 12px 24px; border-radius: 10px; margin-right: 8px; box-shadow: 0 4px 12px rgba(190, 24, 93, 0.3);">
                                    📊 Ver Métricas y Reportes
                                </a>
                                <a href="/admin/sorpresas_kawai/producto/" style="display: inline-block; background: #ffffff; color: #334155; text-decoration: none; font-weight: bold; font-size: 14px; padding: 12px 20px; border-radius: 10px; border: 1px solid #cbd5e1;">
                                    📦 Gestionar Productos en Admin
                                </a>
                            </div>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8fafc; padding: 16px; text-align: center; border-top: 1px solid #e2e8f0;">
                            <p style="color: #94a3b8; font-size: 12px; margin: 0;">
                                Sorpresas Kawaii • Sistema Automático de Control de Inventarios
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>"""

    mensaje_plano = f"""ALERTA DE INVENTARIO Y STOCK BAJO - SORPRESAS KAWAII
=====================================================
Se ha detectado inventario crítico en los siguientes productos:
{info_origen_txt}
{lineas_texto_str}

Por favor ingresa al panel de administración para gestionar la reposición de existencias:
/admin/metricas-ventas/
"""

    try:
        send_mail(
            subject=asunto,
            message=mensaje_plano,
            html_message=cuerpo_html,
            from_email=settings.DEFAULT_FROM_EMAIL or 'noreply@sorpresaskawaii.com',
            recipient_list=destinatarios,
            fail_silently=True,
        )
        return True
    except Exception:
        return False

