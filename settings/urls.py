from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from sorpresas_kawai.metricas_views import (
    metricas_ventas_dashboard,
    exportar_metricas_excel,
    enviar_alerta_stock_email_manual
)

urlpatterns = [
    path('admin/metricas-ventas/', metricas_ventas_dashboard, name='admin_metricas_ventas'),
    path('admin/metricas-ventas/exportar-excel/', exportar_metricas_excel, name='admin_exportar_excel'),
    path('admin/metricas-ventas/enviar-alerta-stock/', enviar_alerta_stock_email_manual, name='admin_enviar_alerta_stock'),
    path('admin/', admin.site.urls),
    path('', include('sorpresas_kawai.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')
