# Sorpresas Kawaii — Plataforma de Comercio Electronico y Control de Gestion

Plataforma web integral de comercio electronico, control transaccional de inventario y gestion administrativa desarrollada bajo el patron arquitectonico Modelo-Vista-Template (MVT) con el framework Django (Python).

El sistema sistematiza el catalogo de productos de papeleria y regalos, automatiza la sincronizacion de existencias en tiempo real, agiliza la adquisicion de combos y experiencias sorpresa, facilita la finalizacion de compras asistida por WhatsApp y provee un panel gerencial con analitica de ventas y generacion de reportes en Excel.

---

## 1. Caracteristicas Principales

- **Catalogo Dinamico:** Visualizacion estructurada de productos por categorias, filtros avanzados, paginacion y visualizacion de descuentos comerciales.
- **Modulo de Combos y Sorpresas:** Soporte para venta empaquetada con relaciones Muchos a Muchos (M2M) y experiencias aleatorias (*mystery boxes* y *scoops*).
- **Carrito de Compras Transaccional:** Persistencia por usuario, conteo reactivo de articulos mediante procesador de contexto global (`context_processors.py`) y evaluacion de politicas de envio gratuito.
- **Control Concurrente de Inventario:** Descuento automatico de existencias bajo transacciones atomicas (`transaction.atomic()`), impidiendo sobreventas (*overselling*).
- **Finalizacion Asistida por WhatsApp:** Generacion automatica de enlaces Click-to-Chat con codificacion RFC 3986, resumiendo el codigo unico de pedido (#SK-XXXXXX), datos del cliente y desglose de items.
- **Sistema de Notificaciones Transaccionales (SMTP):** Emision automatica de correos electronicos multipart (HTML y texto) ante transiciones de estado de pedido (Pendiente, Pagado, Despachado con transportadora y numero de guia, Entregado) y alertas de inventario critico (stock <= 5 unidades).
- **Seguridad en Capas:**
  - Cifrado de contrasenas mediante PBKDF2 con algoritmo SHA-256.
  - Proteccion nativa contra vulnerabilidades CSRF, XSS, Clickjacking e inyeccion SQL.
  - Middleware de seguridad de sesion contra suplantacion (*Session Hijacking*) basado en validacion de IP y User-Agent.
  - Control de acceso basado en roles (clientes vs. administradores `is_staff`).
- **Dashboard Analitico y Reportes:** Cuadro de mandos con calculo de ingresos confirmados, ticket promedio y exportacion de reportes consolidados en formato Microsoft Excel (.xlsx) generados con OpenPyXL en 5 hojas de trabajo.
- **Configuracion Global Singleton:** Control administrativo para activar o suspender selectivamente modulos de compra, catalogo o promociones con mensajes informativos personalizados.

---

## 2. Pila Tecnologica

- **Lenguaje de Programacion:** Python 3.12+
- **Framework Web:** Django 6.0
- **Base de Datos:** SQLite3 (entorno de desarrollo / pruebas locales)
- **Frontend:** HTML5 Semantico, CSS3 Nativo (`kawaii_admin.css`), JavaScript Vanilla (ES6+)
- **Bibliotecas Clave:** OpenPyXL (hojas de calculo), Pillow (procesamiento de imagenes), Whitenoise (archivos estaticos), Gunicorn (servidor WSGI)
- **Servicios Externos:** Google Gmail SMTP (notificaciones por correo), WhatsApp Click-to-Chat API

---

## 3. Requisitos Previos

Antes de ejecutar el proyecto, asegurese de contar con las siguientes herramientas instaladas en su entorno:

- Python 3.12 o superior ([python.org](https://www.python.org/downloads/))
- Gestor de paquetes `pip` (incluido habitualmente con Python)
- Git ([git-scm.com](https://git-scm.com/))

---

## 4. Instalacion y Puesta en Marcha

Siga estos pasos para clonar, configurar y ejecutar la aplicacion localmente:

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/Camilofuentes95/sorpresas-kawaii.git
cd sorpresas-kawaii
```

### Paso 2: Crear y activar un entorno virtual

En Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

En Linux o macOS (Bash):
```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 4: Aplicar migraciones a la base de datos

```bash
python manage.py migrate
```

### Paso 5: Cargar el catalogo de datos iniciales (Opcional)

Para cargar las 14 referencias de productos base, categorias predeterminadas y combos:

```bash
python manage.py loaddata datos_iniciales.json
```

### Paso 6: Crear el usuario administrador

Puede ejecutar el script automatico provisto en el proyecto:

```bash
python crear_admin.py
```

O generar credenciales personalizadas de superusuario mediante el comando estandar de Django:

```bash
python manage.py createsuperuser
```

### Paso 7: Iniciar el servidor de desarrollo

```bash
python manage.py runserver
```

La aplicacion estara accesible en su navegador web en la direccion:
`http://127.0.0.1:8000/`

---

## 5. Variables de Entorno (Opcional para servicio de correo)

El sistema opera con valores seguros por defecto. Para habilitar el despacho real de correos mediante Gmail SMTP, defina las siguientes variables de entorno en su sistema o archivo de configuracion local:

| Variable | Descripcion | Ejemplo |
| :--- | :--- | :--- |
| `DJANGO_SECRET_KEY` | Clave criptografica de la aplicacion Django. | `tu_clave_secreta_de_produccion` |
| `DJANGO_DEBUG` | Control de depuracion (`True` en desarrollo, `False` en produccion). | `True` |
| `DJANGO_ALLOWED_HOSTS` | Hosts o dominios permitidos separados por comas. | `localhost,127.0.0.1` |
| `GMAIL_USER` | Direccion de correo electronico emisor de Gmail. | `notificaciones@ejemplo.com` |
| `GMAIL_APP_PASSWORD` | Contrasena de aplicacion de 16 caracteres generada en Google Account. | `abcd efgh ijkl mnop` |
| `ADMIN_EMAIL` | Correo destinatario para alertas de stock bajo y nuevos pedidos. | `gerencia@ejemplo.com` |
| `WHATSAPP_PHONE_NUMBER`| Numero de telefono oficial con prefijo de pais para recibir ordenes. | `573222385508` |

---

## 6. Estructura del Proyecto

```text
sorpresas-kawaii/
├── manage.py                          # Interfaz de linea de comandos de Django
├── requirements.txt                   # Declaracion de dependencias del proyecto
├── datos_iniciales.json               # Fixture con el catalogo base de productos
├── crear_admin.py                     # Script utilitario para crear el superusuario
├── settings/
│   ├── settings.py                    # Configuracion global, middleware, BD y SMTP
│   ├── urls.py                        # Enrutador principal de la aplicacion
│   ├── wsgi.py                        # Punto de entrada para despliegues WSGI
│   └── asgi.py                        # Punto de entrada para despliegues ASGI
├── sorpresas_kawai/
│   ├── models.py                      # Modelos de datos relacionales y logica de ordenes
│   ├── views.py                       # Controladores de navegacion, autenticacion y checkout
│   ├── urls.py                        # Mapeo semantico de rutas de la tienda
│   ├── admin.py                       # Personalizacion del panel de administracion
│   ├── context_processors.py          # Contador global de articulos en carrito
│   ├── middleware.py                  # Proteccion de integridad de sesiones (Session Hijacking)
│   ├── emails.py                      # Plantillas y despacho de notificaciones SMTP
│   ├── exportar_excel.py              # Generador binario de reportes de ventas (.xlsx)
│   ├── metricas_views.py              # Dashboard de metricas financieras para administracion
│   └── seed_data.py                   # Script auxiliar para inicializar catalogo si esta vacio
├── templates/
│   ├── base.html                      # Plantilla maestra (Layout)
│   ├── inicio.html                    # Pagina principal con productos destacados
│   ├── sobre_nosotros.html            # Informacion institucional
│   ├── partials/                      # Componentes reutilizables (navbar, footer)
│   ├── admin/                         # Plantillas de inicio de sesion, registro y metricas
│   ├── productos/                     # Vistas de productos, combos y sorpresas
│   ├── carrito/                       # Detalle de compra y resumen de totales
│   ├── pedido/                        # Pantallas de confirmacion y seguimiento de pedidos
│   └── registration/                  # Flujo de recuperacion de contrasenas
└── static/
    ├── css/
    │   └── kawaii_admin.css           # Hoja de estilos principal de la interfaz
    └── img/                           # Logotipos, favicon y recursos graficos
```

---

## 7. Mapa de Rutas Principales

| Ruta | Metodo | Descripcion | Nivel de Acceso |
| :--- | :---: | :--- | :--- |
| `/` | GET | Pagina de inicio con vitrina destacada. | Publico |
| `/productos/` | GET | Catalogo completo con filtros por categoria y paginacion. | Publico |
| `/combos/` | GET | Catalogo de paquetes y combos promocionales. | Publico |
| `/sorpresa/` | GET | Seccion de cajas sorpresa y experiencias interactivas. | Publico |
| `/login/` | GET / POST | Inicio de sesion de usuarios y administradores. | Publico |
| `/register/` | GET / POST | Registro seguro de clientes con validacion de contrasenas. | Publico |
| `/recuperar-contrasena/` | GET / POST | Solicitud de restablecimiento de clave via correo SMTP. | Publico |
| `/carrito/` | GET | Resumen de articulos, calculo de flete y pre-checkout. | Autenticado |
| `/carrito/finalizar/` | POST | Procesamiento transaccional de la orden y descuento de stock. | Autenticado |
| `/pedido/confirmacion/<uuid>/` | GET | Pantalla de orden generada con enlace directo a WhatsApp. | Autenticado |
| `/mis-pedidos/` | GET | Historial de compras del cliente y tracking de guias. | Autenticado |
| `/admin/` | GET / POST | Panel de control nativo de Django. | Rol Staff / Superuser |
| `/panel-admin/metricas/` | GET | Cuadro de mandos gerencial de ventas e ingresos. | Rol Staff / Superuser |
| `/panel-admin/metricas/exportar-excel/` | GET | Descarga de informe financiero consolidado (.xlsx). | Rol Staff / Superuser |

---

## 8. Autor y Creditos

- **Desarrollador y Responsable del Proyecto:** Camilo Alberto Fuentes Mahecha
- **Programa:** Ingenieria de Software — Practica Profesional
- **Institucion:** Corporacion Universitaria Iberoamericana
- **Escenario Empresarial:** Emprendimiento Digital «Sorpresas Kawaii» (Edukit Mosquera)
- **Ano:** 2025 – 2026
