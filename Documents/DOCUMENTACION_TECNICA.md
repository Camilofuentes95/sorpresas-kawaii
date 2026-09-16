# Documentación Técnica — Sorpresas Kawaii

## 1. Descripción General

**Sorpresas Kawaii** es una plataforma web de comercio electrónico desarrollada con **Django** y diseño visual personalizado con estética pastel y kawaii. Permite a los clientes explorar catálogos de papelería y peluches, combos especiales y scoops/sorpresas, administrar su carrito de compras en tiempo real con contador en la barra de navegación, finalizar y coordinar sus compras directamente por **WhatsApp**, recibir notificaciones automáticas por correo electrónico ante cualquier cambio de estado del pedido (Pagado, Enviado con guía de rastreo, Entregado, Cancelado), consultar su historial de compras en tiempo real y recuperar su contraseña de forma segura.

La aplicación sigue la arquitectura estándar **MVT** (Modelo - Vista - Template) de Django:

```text
Usuario → URL → Vista → Modelo/Base de datos → Plantilla HTML → Usuario
```

- **Modelo:** Define las entidades de datos, relaciones relacionales, disparadores automáticos de correos y métodos auxiliares de WhatsApp.
- **Vista:** Procesa la lógica de negocio, autenticación, transacciones atómicas y respuestas HTTP.
- **Plantilla:** Renderiza la interfaz HTML dinámica y responsive con el sistema de diseño kawaii.

---

## 2. Pila Tecnológica (Tech Stack)

| Área | Tecnología | Versión / Herramienta | Uso en el Proyecto |
| --- | --- | --- | --- |
| **Backend** | Python | 3.12+ | Lenguaje base del servidor y lógica de negocio. |
| **Framework Web** | Django | 6.0 | Enrutamiento, ORM, sesiones, auth, context processors, mensajes y panel de administración. |
| **Base de Datos** | SQLite | 3.x (`db.sqlite3`) | Motor relacional local para usuarios, productos, combos, carritos y pedidos. |
| **Frontend** | HTML5 Semántico | Estándar W3C | Estructura modular de páginas y plantillas reutilizables. |
| **Estilos & Diseño** | CSS3 Nativo | `kawaii_admin.css` | Sistema de diseño Kawaii (paleta de rosas, morados pastel, bordes redondeados, sombras suaves y responsive). |
| **Interactividad** | JavaScript | Vanilla ES6+ | Modales de rastreo de guía, control de contraseñas y transiciones interactivas. |
| **Servicio de Correo** | Gmail SMTP | TLS (Puerto 587) | Envío automático de notificaciones de pedidos y recuperación de contraseñas con plantillas HTML/texto. |
| **Canal de Ventas** | WhatsApp API | Click-to-Chat (`wa.me`) | Enlace directo preformateado con número oficial (+57 322 238 5508), ID de pedido y desglose de artículos. |
| **Iconografía & Fuentes** | Font Awesome 6 + Google Fonts | CDN + Poppins & Quicksand | Tipografía moderna e iconos vectoriales para toda la interfaz. |

---

## 3. Arquitectura y Módulos Clave

### A. Context Processor Global del Carrito (`sorpresas_kawai/context_processors.py`)
- Suministra la variable `carrito_total_items` de forma global a todas las plantillas.
- Muestra dinámicamente la burbuja / badge con el conteo de artículos en el botón del carrito en el encabezado.

### B. Sistema Automatizado de Correos (`sorpresas_kawai/emails.py`)
- **Confirmación de Compra:** Notifica al cliente cuando se genera una nueva orden.
- **Actualización de Estado de Pedidos:** Detecta cambios en el modelo `Pedido` y envía correos personalizados:
  - **PAGADO:** Confirma la verificación del pago y el inicio del empaque.
  - **ENVIADO:** Informa el despacho del paquete e incluye la **Empresa de Envío** y el **Número de Guía**.
  - **ENTREGADO:** Notifica la entrega exitosa del paquete.
  - **CANCELADO:** Notifica la cancelación de la orden con canales de soporte.

### C. Integración de Finalización por WhatsApp (+57 322 238 5508)
- Métodos implementados en `Pedido`:
  - `generar_mensaje_whatsapp()`: Compone el texto con código del pedido, nombre del cliente, lista de artículos y total.
  - `whatsapp_url`: Genera el enlace universal `https://wa.me/573222385508?text=...` codificado para navegador o app móvil.
- Botones destacados en la pantalla de confirmación (`confirmacion.html`) y en el historial de compras (`mis_pedidos.html`).

---

## 4. Diagrama y Modelo de Datos

```text
┌──────────────┐         ┌──────────────┐         ┌─────────────────┐
│  Categoria   │ 1 ─── N │   Producto   │ 1 ─── N │  DetallePedido  │
└──────────────┘         └──────────────┘         └────────┬────────┘
                                │                          │
                                │ N                        │ N
                         ┌──────┴───────┐                  │
                         │ CombosProd.  │                  │
                         └──────┬───────┘                  │
                                │ N                        │
                                │                          │
┌──────────────┐         ┌──────┴───────┐                  │
│     User     │ 1 ─── N │    Combo     │ 1 ───────────────┤
└──────┬───────┘         └──────────────┘                  │
       │                                                   │
       ├───────── 1 ─── 1 ── UserProfile                   │
       │                                                   │
       ├───────── 1 ─── 1 ── CarritoDeCompras ── 1 ─── N ──┤ ItemCarrito
       │                                                   │
       └───────── 1 ─── N ── Pedido ─────────── 1 ─── N ───┘
```

### Modelos Principales:
1. **`User` / `UserProfile`**: Gestión de usuarios autenticados y dirección de entrega.
2. **`Categoria`**: Clasificación de productos del catálogo.
3. **`Producto`**: Inventario de artículos individuales con cálculo de descuento (`precio_final`).
4. **`Combo` / `CombosProductos`**: Packs armados compuestos por uno o más productos.
5. **`CarritoDeCompras` / `ItemCarrito`**: Carrito de compras persistente por usuario.
6. **`Pedido` / `DetallePedido`**: Órdenes creadas con código `#SK-XXXXXX`, estado (`PENDIENTE`, `PAGADO`, `ENVIADO`, `ENTREGADO`, `CANCELADO`), empresa de envío, número de guía y disparador automático de notificaciones.

---

## 5. Estructura de Directorios

```text
kawaii/
├── manage.py                          # CLI de Django
├── db.sqlite3                         # Base de datos SQLite
├── DOCUMENTACION_TECNICA.md           # Documentación técnica completa
├── settings/
│   ├── settings.py                    # Configuración global, apps, context processors, SMTP y WhatsApp
│   ├── urls.py                        # Enrutador raíz
│   ├── wsgi.py                        # Punto de entrada WSGI
│   └── asgi.py                        # Punto de entrada ASGI
├── sorpresas_kawai/
│   ├── admin.py                       # Panel administrativo personalizado (PedidoAdmin, etc.)
│   ├── context_processors.py          # Contador global de artículos del carrito
│   ├── emails.py                      # Plantillas y envío de correos automáticos
│   ├── models.py                      # Modelos relacionales y lógica de WhatsApp
│   ├── views.py                       # Vistas y lógica de negocio
│   ├── urls.py                        # Rutas de la tienda web
│   ├── tests.py                       # Suite de pruebas unitarias y de seguridad (13 tests)
│   └── migrations/                    # Migraciones del esquema de BD
├── templates/
│   ├── base.html                      # Layout maestro con navbar y footer
│   ├── Inicio.html                    # Página principal con novedades y destacados
│   ├── sobre_nosotros.html            # Información institucional y redes
│   ├── partials/
│   │   ├── navbar.html                # Barra de navegación con badge de carrito
│   │   └── footer.html                # Pie de página
│   ├── admin/
│   │   ├── logintest.html             # Inicio de sesión
│   │   └── register.html              # Registro seguro de usuarios
│   ├── productos/
│   │   ├── lista.html                 # Catálogo de productos con filtros
│   │   ├── combos.html                # Catálogo de combos
│   │   └── sorpresas.html             # Sección de scoops y sorpresas
│   ├── carrito/
│   │   └── detalle.html               # Resumen del carrito y checkout
│   ├── pedido/
│   │   ├── confirmacion.html          # Pantalla de confirmación con botón de WhatsApp
│   │   └── mis_pedidos.html           # Historial y seguimiento de pedidos con guía
│   └── registration/                  # Plantillas de recuperación de contraseña
└── static/
    ├── css/
    │   └── kawaii_admin.css           # Hoja de estilos y diseño visual Kawaii
    └── img/                           # Assets gráficos y favicon
```

---

## 6. Endpoints y Mapa de Rutas

| URL | Nombre de Ruta | Descripción | Acceso |
| --- | --- | --- | --- |
| `/` | `inicio` | Página de inicio | Público |
| `/productos/` | `lista_productos` | Catálogo de productos con filtros | Público |
| `/combos/` | `lista_combos` | Catálogo de combos | Público |
| `/sorpresa/` | `lista_sorpresas` | Sección de sorpresas y scoops | Público |
| `/sobre-nosotros/` | `sobre_nosotros` | Información de la tienda | Público |
| `/register/` | `register` | Formulario de registro de clientes | Público |
| `/login/` | `login` | Inicio de sesión | Público |
| `/logout/` | `logout` | Cierre de sesión | Autenticado |
| `/carrito/` | `ver_carrito` | Vista del carrito de compras | Autenticado |
| `/agregar/<uuid>/` | `agregar_a_carrito` | Añadir producto al carrito | Autenticado |
| `/quitar/<uuid>/` | `quitar_de_carrito` | Disminuir/remover producto | Autenticado |
| `/combos/agregar/<uuid>/` | `agregar_combo_a_carrito` | Añadir combo al carrito | Autenticado |
| `/combos/quitar/<uuid>/` | `quitar_combo_de_carrito` | Disminuir/remover combo | Autenticado |
| `/carrito/finalizar/` | `finalizar_compra` | Procesar orden y vaciar carrito | Autenticado |
| `/pedido/confirmacion/<uuid>/`| `pagina_confirmacion` | Confirmación de compra y botón WhatsApp | Autenticado |
| `/mis-pedidos/` | `mis_pedidos` | Historial y rastreo de envíos del cliente | Autenticado |
| `/recuperar-contrasena/` | `password_reset` | Formulario para solicitar reseteo | Público |
| `/recuperar-contrasena/enviada/` | `password_reset_done` | Confirmación de correo enviado | Público |
| `/restablecer-contrasena/<uid>/<token>/` | `password_reset_confirm` | Formulario para ingresar nueva clave | Público |
| `/restablecer-contrasena/listo/` | `password_reset_complete` | Clave actualizada correctamente | Público |

---

## 7. Variables de Entorno

```bash
# Variables del sistema / producción
DJANGO_SECRET_KEY="tu_clave_secreta_unica_y_segura"
DJANGO_DEBUG="True"                        # "True" en desarrollo local, "False" en producción
DJANGO_ALLOWED_HOSTS="*"                   # Hosts permitidos separados por comas

# Contacto oficial de WhatsApp
WHATSAPP_PHONE_NUMBER="573222385508"

# Servicio de Correo SMTP (Gmail)
GMAIL_USER="tucorreo@gmail.com"
GMAIL_APP_PASSWORD="tu_password_de_aplicacion_16_caracteres"
```

---

## 8. Cómo Usar tu PC como Servidor para Pruebas

Puedes usar tu propio computador como servidor para realizar pruebas tanto desde otros dispositivos en tu casa (como tu celular) como a través de Internet:

### Opción A: Pruebas en Red Local (Celular u otro PC en la misma red Wi-Fi)

1. **Obtener la dirección IP local de tu computador:**
   Abre una terminal PowerShell y ejecuta:
   ```powershell
   ipconfig
   ```
   Busca la línea que dice **Dirección IPv4** (por ejemplo: `192.168.1.15`).

2. **Iniciar Django escuchando en todas las interfaces de red:**
   ```powershell
   python manage.py runserver 0.0.0.0:8000
   ```

3. **Abrir la tienda desde tu celular:**
   Conéctate a la misma red Wi-Fi de tu casa y entra desde el navegador del celular a:
   ```text
   http://192.168.1.15:8000/
   ```
   *(Reemplaza `192.168.1.15` por la IP que te arrojó `ipconfig`).*

> **Nota:** Si no carga en el celular, asegúrate de que el Firewall de Windows permita el acceso a Python o al puerto 8000 en redes privadas.

---

### Opción B: Pruebas por Internet con Enlace Público Temporal (Túnel Seguro)

Si quieres compartir la tienda con alguien que no esté en tu misma red Wi-Fi:

1. Inicia tu servidor local de Django en una terminal:
   ```powershell
   python manage.py runserver 8000
   ```

2. En otra terminal, crea un túnel temporal gratuito con **localtunnel** o **ngrok**:
   - Con **localtunnel** (requiere Node.js):
     ```powershell
     npx localtunnel --port 8000
     ```
   - O con **ngrok**:
     ```powershell
     ngrok http 8000
     ```

3. Obtendrás un enlace público seguro `https://xxxx.loca.lt` o `https://xxxx.ngrok-free.app` que puedes abrir desde cualquier teléfono o computador en el mundo para realizar pruebas en vivo.

---

## 9. Pruebas Automatizadas

Para validar la integridad de todas las funcionalidades, modelos, seguridad, correos y enlaces de WhatsApp:

```powershell
python manage.py test
```

Resultado actual:
```text
Ran 13 tests in 17.089s - OK
```
