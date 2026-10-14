"""
Enrutamiento de URLs - Sorpresas Kawaii.

Estructura de rutas de la aplicacion organizadas por modulos funcionales:
1. Autenticacion y cuentas de usuario.
2. Flujo de recuperacion de contrasenas (Django auth views).
3. Navegacion publica y vitrinas comerciales.
4. Operaciones transaccionales del carrito de compras.
5. Gestion y confirmacion de ordenes de pedido.
6. Panel administrativo y metricas gerenciales de ventas.
"""

from django.urls import path, reverse_lazy
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from . import views

urlpatterns = [
    # ---------------------------------------------------------
    # 1. Modulo de Autenticacion y Registro de Usuarios
    # ---------------------------------------------------------
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # ---------------------------------------------------------
    # 2. Flujo de Recuperacion de Contrasenas (SMTP)
    # ---------------------------------------------------------
    path(
        'recuperar-contrasena/',
        PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.html',
            subject_template_name='registration/password_reset_subject.txt',
        ),
        name='password_reset',
    ),
    path(
        'recuperar-contrasena/enviada/',
        PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
        name='password_reset_done',
    ),
    path(
        'restablecer-contrasena/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
            form_class=views.NuevaContrasenaForm,
            success_url=reverse_lazy('password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'restablecer-contrasena/listo/',
        PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
        name='password_reset_complete',
    ),

    # ---------------------------------------------------------
    # 3. Navegacion Publica y Catalogos
    # ---------------------------------------------------------
    path('', views.inicio, name='inicio'),
    path('sobre-nosotros/', views.sobre_nosotros, name='sobre_nosotros'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('combos/', views.lista_combos, name='lista_combos'),
    path('sorpresa/', views.lista_sorpresas, name='lista_sorpresas'),

    # ---------------------------------------------------------
    # 4. Carrito de Compras (Productos y Combos)
    # ---------------------------------------------------------
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('agregar/<uuid:producto_id>/', views.agregar_a_carrito, name='agregar_a_carrito'),
    path('quitar/<uuid:producto_id>/', views.quitar_de_carrito, name='quitar_de_carrito'),
    path('combos/agregar/<uuid:combo_id>/', views.agregar_combo_a_carrito, name='agregar_combo_a_carrito'),
    path('combos/quitar/<uuid:combo_id>/', views.quitar_combo_de_carrito, name='quitar_combo_de_carrito'),

    # ---------------------------------------------------------
    # 5. Checkout, Pedidos y WhatsApp
    # ---------------------------------------------------------
    path('carrito/finalizar/', views.finalizar_compra, name='finalizar_compra'),
    path('pedido/confirmacion/<uuid:pedido_id>/', views.pagina_confirmacion, name='pagina_confirmacion'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),

    # ---------------------------------------------------------
    # 6. Panel Analitico Administrativo (Exclusivo Staff)
    # ---------------------------------------------------------
    path('panel-admin/metricas/', views.metricas_ventas_dashboard, name='panel_admin_metricas'),
    path('panel-admin/metricas/exportar-excel/', views.exportar_metricas_excel, name='panel_admin_exportar_excel'),
    path('panel-admin/metricas/enviar-alerta-stock/', views.enviar_alerta_stock_email_manual, name='panel_admin_enviar_alerta_stock'),
]
