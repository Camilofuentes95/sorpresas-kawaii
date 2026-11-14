"""
Comando de Gestion Django - Sorpresas Kawaii.

Busca pedidos que hayan cumplido al menos 3 dias (o el parametro especificado)
en estado ENTREGADO y remite un correo electronico de invitacion para calificar
los productos y combos recibidos en la tienda.

Uso:
    python manage.py enviar_recordatorios_calificacion
    python manage.py enviar_recordatorios_calificacion --dias 3
    python manage.py enviar_recordatorios_calificacion --dry-run
"""

from django.core.management.base import BaseCommand
from sorpresas_kawai.emails import enviar_correos_recordatorios_calificacion_pendientes


class Command(BaseCommand):
    help = (
        "Envia correos de invitacion para calificar productos a clientes cuyos pedidos "
        "fueron entregados hace 3 dias o mas."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=3,
            help="Numero de dias transcurridos desde la entrega para enviar la invitacion (por defecto: 3)."
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help="Simula la busqueda y muestra los pedidos candidatos sin enviar correos ni modificar registros."
        )

    def handle(self, *args, **options):
        dias = options['dias']
        dry_run = options['dry_run']

        self.stdout.write(self.style.MIGRATE_HEADING(
            f"=== Recordatorio Automatico de Calificaciones Sorpresas Kawaii (Umbral: {dias} dias) ==="
        ))

        if dry_run:
            self.stdout.write(self.style.WARNING("[MODO SIMULACION / DRY-RUN ACTIVO] No se enviaran correos."))

        resultado = enviar_correos_recordatorios_calificacion_pendientes(dias=dias, dry_run=dry_run)

        total_encontrados = resultado['total_encontrados']
        total_enviados = resultado['total_enviados']
        pedidos = resultado['pedidos_procesados']

        if total_encontrados == 0:
            self.stdout.write(self.style.SUCCESS(
                f"[OK] No hay pedidos pendientes de recordatorio con {dias} o mas dias de entregados."
            ))
            return

        self.stdout.write(f"-> Pedidos identificados: {total_encontrados}")
        for cod in pedidos:
            self.stdout.write(f"   • Pedido {cod}")

        if dry_run:
            self.stdout.write(self.style.SUCCESS(
                f"[OK] Simulacion completada: {total_encontrados} pedido(s) serian notificados."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"[OK] Proceso finalizado: {total_enviados} de {total_encontrados} correo(s) enviados con exito."
            ))

