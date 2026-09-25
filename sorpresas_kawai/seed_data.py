import uuid
from django.db import transaction
from django.contrib.auth.models import User
from .models import Categoria, Producto, Combo, CombosProductos


def seed_database():
    """
    Puebla la base de datos automáticamente con las categorías, productos, combos
    y el superusuario administrador por defecto si la base de datos está vacía.
    """
    try:
        with transaction.atomic():
            # 1. Crear o asegurar superusuario admin
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@sorpresaskawaii.com',
                    password='Admin2026!#Kawaii'
                )
                print("Superusuario admin creado.")

            # 2. Categorías
            cat_boligrafo, _ = Categoria.objects.get_or_create(
                id=uuid.UUID('3e90ea7b-8cd3-4e59-85cf-cb02bdf9b9fc'),
                defaults={'nombre': 'Boligrafo'}
            )
            cat_agenda, _ = Categoria.objects.get_or_create(
                id=uuid.UUID('e7f51c7e-d530-47db-9b8a-8174fdd95cb0'),
                defaults={'nombre': 'Agenda'}
            )
            cat_sticker, _ = Categoria.objects.get_or_create(
                id=uuid.UUID('faec6770-ddc7-4330-8d84-00a53688931c'),
                defaults={'nombre': 'Sticker'}
            )
            cat_sorpresa, _ = Categoria.objects.get_or_create(
                id=uuid.UUID('49bc120b-fb92-4be5-89e7-1e970534ca0c'),
                defaults={'nombre': 'Sorpresa'}
            )
            cat_borradores, _ = Categoria.objects.get_or_create(
                id=uuid.UUID('b1f991cc-f9e2-4723-9345-9a0f5f7214a7'),
                defaults={'nombre': 'Borradores'}
            )

            # 3. Productos (14 productos)
            productos_data = [
                {
                    'id': 'baa18281-ff03-48a6-97ac-d47aebdb6971',
                    'nombre': 'Lapiz',
                    'id_categoria': cat_boligrafo,
                    'valor_unitario': 1000.0,
                    'descuento_porcentaje': 0.0,
                    'stock': 3,
                    'imagen': None,
                    'imagen_url': 'https://static.vecteezy.com/system/resources/previews/011/453/422/non_2x/pencil-school-supply-kawaii-free-vector.jpg',
                    'activo': True,
                },
                {
                    'id': '588da4ac-21d5-466f-9886-23d7b4deb12e',
                    'nombre': 'Cuaderno',
                    'id_categoria': cat_agenda,
                    'valor_unitario': 50000.0,
                    'descuento_porcentaje': 10.0,
                    'stock': 6,
                    'imagen': None,
                    'imagen_url': 'https://us.123rf.com/450wm/djvstock/djvstock1707/djvstock170703197/81624491-kawaii-notebook-icon-over-white-background-vector-illustration.jpg',
                    'activo': True,
                },
                {
                    'id': '81da5f61-d423-44ea-b252-ef99c7d417eb',
                    'nombre': 'Scoop Normal',
                    'descripcion': 'Una cucharada llena de productos sorpresa. Cada scoop contiene figuras y detalles kawaii elegidos al azar.',
                    'id_categoria': cat_sorpresa,
                    'valor_unitario': 30000.0,
                    'descuento_porcentaje': 0.0,
                    'stock': 100,
                    'imagen': None,
                    'imagen_url': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSnPxSs9T7dhxCHyGYf3askmPf5V-xm3zZHALE00u2Xv7cf3br9HS_EfQI_&s=10',
                    'es_nuevo': False,
                    'activo': True,
                },
                {
                    'id': 'a3e891c2-55f1-46bb-b1d9-7b3c4fa0821d',
                    'nombre': 'Lucky Pop',
                    'descripcion': '¡Gira la máquina de bolitas y saca 8 figuritas kawaii sorpresa para armar tu kit con increíbles premios mágicos!',
                    'id_categoria': cat_sorpresa,
                    'valor_unitario': 25000.0,
                    'descuento_porcentaje': 0.0,
                    'stock': 50,
                    'imagen': 'productos/lucky_pop.jpg',
                    'imagen_url': None,
                    'es_nuevo': True,
                    'activo': True,
                },
                {
                    'id': '89099ed0-07bf-42c8-bda1-9d921992a949',
                    'nombre': 'Borrador Chocolate',
                    'id_categoria': cat_borradores,
                    'valor_unitario': 3000.0,
                    'descuento_porcentaje': 0.0,
                    'stock': 6,
                    'imagen': 'productos/WhatsApp_Image_2026-09-05_at_14.19.20.jpeg',
                    'imagen_url': None,
                    'activo': True,
                },
                {
                    'id': 'cde0e3f1-cc88-4d2b-a671-58c7dceb9388',
                    'nombre': 'Borrador Postres',
                    'id_categoria': cat_borradores,
                    'valor_unitario': 5000.0,
                    'descuento_porcentaje': 0.0,
                    'stock': 3,
                    'imagen': 'productos/WhatsApp_Image_2026-09-05_at_14.19.19.jpeg',
                    'imagen_url': None,
                    'activo': True,
                },
                {
                    'id': '3b23fda1-42b2-446a-a280-0353ae681b9a',
                    'nombre': 'Resaltadores gato',
                    'id_categoria': cat_boligrafo,
                    'valor_unitario': 10000.0,
                    'descuento_porcentaje': 0.0,
                    'stock': 2,
                    'imagen': 'productos/WhatsApp_Image_2026-09-05_at_14.20.58.jpeg',
                    'imagen_url': None,
                    'activo': True,
                },
                {
                    'id': 'da9da9dd-0f64-4b0e-b4a3-d3d366e67939',
                    'nombre': 'Borrador Stich',
                    'id_categoria': cat_borradores,
                    'valor_unitario': 3000.0,
                    'descuento_porcentaje': 0.0,
                    'stock': 5,
                    'imagen': 'productos/WhatsApp_Image_2026-09-05_at_14.19.23.jpeg',
                    'imagen_url': None,
                    'activo': True,
                },
                {
                    'id': '516dee63-6386-48f9-a29c-309571ef86c6',
                    'nombre': 'Borrador Aguacate',
                    'id_categoria': cat_borradores,
                    'valor_unitario': 3000.0,
                    'descuento_porcentaje': 0.0,
                    'stock': 3,
                    'imagen': 'productos/WhatsApp_Image_2026-09-05_at_14.20.50.jpeg',
                    'imagen_url': None,
                    'activo': True,
                },
                {
                    'id': 'c5f28615-7e0f-4286-baf3-e441e8cf3f22',
                    'nombre': 'Esfero navidad',
                    'id_categoria': cat_boligrafo,
                    'valor_unitario': 3000.0,
                    'descuento_porcentaje': 0.0,
                    'stock': 6,
                    'imagen': 'productos/WhatsApp_Image_2026-09-05_at_14.20.51.jpeg',
                    'imagen_url': None,
                    'activo': True,
                },
                {
                    'id': 'd1008a81-3d08-4ad0-bfa3-4c95de2b3929',
                    'nombre': 'MultiEsfero Hello Kity',
                    'id_categoria': cat_boligrafo,
                    'valor_unitario': 7000.0,
                    'descuento_porcentaje': 0.0,
                    'stock': 8,
                    'imagen': 'productos/WhatsApp_Image_2026-09-05_at_14.20.52.jpeg',
                    'imagen_url': None,
                    'activo': True,
                },
                {
                    'id': '96cf2dda-dd90-479c-8607-4b0ab7aafc6c',
                    'nombre': 'Agenda Capibara',
                    'id_categoria': cat_agenda,
                    'valor_unitario': 6000.0,
                    'descuento_porcentaje': 0.0,
                    'stock': 3,
                    'imagen': 'productos/WhatsApp_Image_2026-09-05_at_14.20.55.jpeg',
                    'imagen_url': None,
                    'activo': True,
                },
                {
                    'id': '5042d8b3-d0d5-470e-96a2-de637a6ef4c1',
                    'nombre': 'Agenda Harry Kitty',
                    'id_categoria': cat_agenda,
                    'valor_unitario': 5000.0,
                    'descuento_porcentaje': 0.0,
                    'stock': 3,
                    'imagen': 'productos/WhatsApp_Image_2026-09-05_at_14.20.573.jpeg',
                    'imagen_url': None,
                    'activo': True,
                },
                {
                    'id': '5bf2b084-d6da-489b-89b2-11c8a43c59ad',
                    'nombre': 'Agenda Story Zoo',
                    'id_categoria': cat_agenda,
                    'valor_unitario': 5000.0,
                    'descuento_porcentaje': 0.0,
                    'stock': 5,
                    'imagen': 'productos/WhatsApp_Image_2026-09-05_at_14.20.571.jpeg',
                    'imagen_url': None,
                    'activo': True,
                },
                {
                    'id': '0a63172f-5606-4195-9f49-6d432fb0e9a9',
                    'nombre': 'Agenda alcolchada',
                    'id_categoria': cat_agenda,
                    'valor_unitario': 7000.0,
                    'descuento_porcentaje': 0.0,
                    'stock': 2,
                    'imagen': 'productos/WhatsApp_Image_2026-09-05_at_14.21.00.jpeg',
                    'imagen_url': None,
                    'activo': True,
                },
            ]

            for p_info in productos_data:
                prod_id = uuid.UUID(p_info['id'])
                defaults = {
                    'nombre': p_info['nombre'],
                    'id_categoria': p_info['id_categoria'],
                    'valor_unitario': p_info['valor_unitario'],
                    'descuento_porcentaje': p_info['descuento_porcentaje'],
                    'stock': p_info['stock'],
                    'imagen': p_info['imagen'],
                    'imagen_url': p_info['imagen_url'],
                    'activo': p_info['activo'],
                }
                Producto.objects.update_or_create(id=prod_id, defaults=defaults)

            # 4. Combo
            combo, _ = Combo.objects.get_or_create(
                nombre='Super combo Kawaii',
                defaults={
                    'descripcion': 'Combo exclusivo con productos kawaii',
                    'valor_combo': 25000.0,
                    'descuento_porcentaje': 0.0,
                    'numero_productos': 4,
                    'activo': True,
                    'imagen': 'combos/WhatsApp_Image_2026-09-05_at_14.23.00.jpeg'
                }
            )

            print("Base de datos poblada exitosamente con 14 productos y categorías.")
            return True
    except Exception as err:
        print(f"Error al sembrar base de datos: {err}")
        return False
