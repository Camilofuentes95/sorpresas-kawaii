from django.urls import path
from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import reverse_lazy
from . import views

urlpatterns = [

    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('', views.inicio, name='inicio'),
    path('sobre-nosotros/', views.sobre_nosotros, name='sobre_nosotros'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('sorpresa/', views.lista_sorpresas, name='lista_sorpresas'),
    path('login/', views.login_view, name='login'),
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
    path('agregar/<uuid:producto_id>/', views.agregar_a_carrito, name='agregar_a_carrito'),
    path('quitar/<uuid:producto_id>/', views.quitar_de_carrito, name='quitar_de_carrito'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/finalizar/', views.finalizar_compra, name='finalizar_compra'),
    path('pedido/confirmacion/<uuid:pedido_id>/', views.pagina_confirmacion, name='pagina_confirmacion'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('combos/', views.lista_combos, name='lista_combos'),
    path('combos/agregar/<uuid:combo_id>/', views.agregar_combo_a_carrito, name='agregar_combo_a_carrito'),
    path('combos/quitar/<uuid:combo_id>/', views.quitar_combo_de_carrito, name='quitar_combo_de_carrito'),
    path('panel-admin/metricas/', views.metricas_ventas_dashboard, name='panel_admin_metricas'),
    path('panel-admin/metricas/exportar-excel/', views.exportar_metricas_excel, name='panel_admin_exportar_excel'),
    path('panel-admin/metricas/enviar-alerta-stock/', views.enviar_alerta_stock_email_manual, name='panel_admin_enviar_alerta_stock'),
]
