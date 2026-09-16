# CORPORACIÓN UNIVERSITARIA IBEROAMERICANA
## FACULTAD DE INGENIERÍA Y CIENCIAS BÁSICAS
### PROGRAMA DE INGENIERÍA DE SOFTWARE
### MÓDULO DE PRÁCTICA PROFESIONAL / ESCENARIO DE PRÁCTICAS

---

# PLAN DE TRABAJO DE PRÁCTICA PROFESIONAL
## DISEÑO, DESARROLLO E IMPLEMENTACIÓN DE LA PLATAFORMA DE COMERCIO ELECTRÓNICO Y GESTIÓN DE INVENTARIOS «SORPRESAS KAWAII»

---

**Presentado por:**  
- **Camilo Alberto Fuentes Mahecha** — Código: 100139562  

**Tutor Académico / Asesor de Prácticas:**  
Tatiana Cabrera  

**Escenario de Práctica:**  
Emprendimiento Digital «Sorpresas Kawaii»  

**Bogotá D.C., Colombia**  
**2025**

---

## RESUMEN EJECUTIVO

El presente Plan de Trabajo formula la propuesta de intervención técnica y profesional en el marco del módulo de Práctica Profesional de la Corporación Universitaria Iberoamericana. El proyecto se desarrolla en el escenario real del emprendimiento **«Sorpresas Kawaii»**, un negocio dedicado a la venta de artículos de papelería estética, peluches y cajas sorpresa temáticas (*mystery boxes* y *scoops*), cuya atracción de usuarios se fundamenta en la viralidad de redes sociales (TikTok e Instagram).

A partir de un diagnóstico profundo de la problemática empresarial, se identificó que la comercialización mediante chats y procesos manuales generaba descontrol crítico de existencias (sobreventas), pérdida de información de pedidos, ausencia de métricas de ingresos y riesgos en el tratamiento de datos personales de los compradores. Para solucionar esta necesidad, se plantea el desarrollo de una plataforma web estructurada bajo el patrón Modelo-Vista-Template (MVT) con el framework **Django (Python)**, incorporando módulos de catálogo interactivo, generador dinámico de combos con descuentos, sincronización transaccional de inventario en tiempo real, autenticación segura, notificaciones por correo electrónico y finalización ágil de compras asistida por la API de WhatsApp.

El plan se rige por la metodología ágil **Scrum** y se orienta al cumplimiento del Resultado de Aprendizaje Esperado (RAE), desarrollando competencias de **autogestión, autorregulación y liderazgo ético** en la ingeniería de software (protección de datos bajo la Ley 1581 de 2012, honestidad intelectual y responsabilidad social). Se detallan la especificación formal de Requerimientos Funcionales y No Funcionales (RQF/RQNF), el cronograma por sprints, la matriz de riesgos y la estimación presupuestal bajo normas APA (7.ª edición).

**Palabras clave:** *Plan de trabajo, práctica profesional, comercio electrónico, Django, Scrum, autogestión, liderazgo ético, Sorpresas Kawaii.*

---

## 1. INTRODUCCIÓN

En la actualidad, las microempresas y emprendimientos emergentes encuentran en los canales de video corto (como TikTok e Instagram) un dinamizador comercial sin precedentes para posicionar artículos de nicho. No obstante, este rápido crecimiento en demanda suele colapsar las operaciones cuando no existe una infraestructura tecnológica formal que soporte el catálogo, la verificación de inventario y la trazabilidad de los pedidos.

El presente Plan de Trabajo establece las bases teóricas, metodológicas y prácticas para solucionar este déficit en el emprendimiento «Sorpresas Kawaii». Asimismo, el documento responde de manera estricta al propósito formativo del RAE del módulo de prácticas, consolidando habilidades de liderazgo ético, planeación autónoma del trabajo y desarrollo de software de alta calidad bajo estándares profesionales.

---

## 2. CONTEXTUALIZACIÓN DEL ESCENARIO DE PRÁCTICA Y STAKEHOLDERS

«Sorpresas Kawaii» es una tienda digital especializada en papelería asiática y accesorios de diseño exclusivo de difícil acceso en papelerías tradicionales. La empresa carece de tienda física y centraliza su estrategia comercial en transmisiones y videos de redes sociales, donde las «cajas sorpresa» y «scoops» representan su principal factor diferenciador.

### 2.1. Mapa de Actores y Stakeholders
- **Jenny López (Fundadora / Product Owner de Catálogo):** Define los productos a comercializar, combinaciones de combos y valida la identidad gráfica kawaii.
- **Andrea Guerrero (Fundadora / Product Owner de Costos y Finanzas):** Supervisa la rentabilidad, los márgenes de descuento y los reportes de ventas.
- **Camilo Alberto Fuentes Mahecha (Practicante / Desarrollador y Gestor del Proyecto):** Responsable del levantamiento de requisitos, arquitectura del sistema, desarrollo full-stack en Django, control de calidad, suite de pruebas automatizadas y despliegue.
- **Clientes Finales:** Usuarios compradores que demandan una experiencia interactiva, rápida, transparente y confiable desde dispositivos móviles y de escritorio.

---

## 3. DIAGNÓSTICO PROFUNDO DE LA SITUACIÓN PROBLEMA

El análisis diagnóstico realizado en la organización demostró que la gestión manual de ventas por mensajes directos (DM) causaba cuellos de botella operacionales severos:
- **Saturación y demoras en atención:** En picos de viralidad, responder manualmente a cada cliente sobre precios y disponibilidad generaba demoras de hasta 24 horas y pérdida de ventas.
- **Desincronización de inventario y sobreventas:** El registro no automatizado permitía vender productos agotados a diferentes usuarios simultáneamente, causando reprocesos y devoluciones.
- **Vulnerabilidad en datos personales:** La recopilación no estandarizada de direcciones y teléfonos por chat contravenía la Ley 1581 de 2012 (Habeas Data).
- **Inexistencia de reportes financieros:** Falta de consolidación de ingresos y rotación de stock para planificar compras a proveedores.
- **Falta de trazabilidad post-venta:** Ausencia de confirmación formal por correo y desconocimiento del número de guía de envío por parte del cliente.

De acuerdo con Pressman y Maxim (2021) y los principios de desarrollo esbelto (Omaña, 2012), la sistematización e integración de estos flujos en una arquitectura web transaccional elimina el desperdicio operativo y maximiza el valor percibido por el cliente.

---

## 4. OBJETIVOS DEL PLAN DE TRABAJO Y ALINEACIÓN

### 4.1. Objetivo General
Diseñar, desarrollar e implementar una plataforma web de comercio electrónico y gestión administrativa para el emprendimiento **«Sorpresas Kawaii»**, automatizando el catálogo digital, la administración de inventario en tiempo real, los combos temáticos, el procesamiento seguro de órdenes y la generación de reportes, fortaleciendo competencias de autogestión y liderazgo ético.

### 4.2. Matriz de Relación entre Objetivos Específicos y Problemática

| Objetivo Específico | Problemática en la Empresa | Solución Técnica de Ingeniería | Impacto Operativo |
| :--- | :--- | :--- | :--- |
| **OE1.** Implementar arquitectura de datos y panel administrativo seguro. | Desorden en información y acceso no controlado a datos de productos y clientes. | Modelos Django ORM (User, Categoria, Producto, Combo, Pedido) con control de acceso y seguridad CSRF/XSS. | Centralización y protección total de los datos del negocio. |
| **OE2.** Desarrollar catálogo interactivo con combos y sorpresas (scoops). | Clientes no conocen stock real ni combinaciones de combos, saturando chats. | Frontend modular responsive con diseño kawaii personalizado y vistas dinámicas en Django. | Autonomía total del cliente para explorar y seleccionar productos 24/7. |
| **OE3.** Integrar carrito de compras con sincronización de stock en tiempo real. | Sobreventas recurrentes de artículos agotados por conteo manual. | Lógica de sesión transaccional con actualización automática de stock al confirmar el pedido. | Eliminación del 100% de errores de sobreventa e inconsistencias. |
| **OE4.** Automatizar checkout con WhatsApp API y notificaciones SMTP. | Falta de formalidad en la orden y demoras en seguimiento de despachos. | Generador de URL Click-to-Chat preformateada y disparador de correos automáticos por estado de pedido. | Reducción del 80% en tiempo de atención y fidelización del comprador. |
| **OE5.** Construir módulo analítico de reportes y control de inventario. | Toma de decisiones empírica sin datos de ventas ni rotación de productos. | Consultas agregadas ORM con filtros por fecha, cálculo de ingresos y alertas de stock bajo. | Planeación financiera y de reposición sustentada en datos reales. |

---

## 5. ESPECIFICACIÓN DE REQUERIMIENTOS DEL SISTEMA (RQF Y RQNF)

### 5.1. Requerimientos Funcionales (RQF)

| ID | Nombre del Requerimiento | Descripción Funcional Detallada | Actor / Rol |
| :--- | :--- | :--- | :--- |
| **RQF01** | Registrar productos | Permitir al administrador registrar, editar y listar productos con nombre, valor, categoría, descripción, stock e imágenes. | PO de Catálogo / Admin |
| **RQF02** | Registrar combos | Permitir generar combos o cajas sorpresa de hasta 5 productos con cálculo de descuento porcentual y precio final. | PO de Catálogo / Admin |
| **RQF03** | Carrito de compras | Proveer al usuario un carrito reactivo donde visualice ítems, cantidades, subtotales y pueda confirmar el pedido. | Cliente / PO de Costos |
| **RQF04** | Actualización de inventario | Actualización automática de existencias tras cada compra confirmada y gestión de stock desde el panel de control. | PO de Catálogo / Sistema |
| **RQF05** | Reportes de ventas | Generación de resúmenes de ingresos totales, ventas por rango de fechas y reporte de stock vendido por producto. | PO de Costos / Admin |
| **RQF06** | Autenticación y Login | Permitir inicio de sesión, registro de clientes y recuperación segura de contraseñas por correo electrónico. | Todos los usuarios |

### 5.2. Requerimientos No Funcionales (RQNF)

| ID | Nombre / Dimensión | Tipo | Especificación Técnica |
| :--- | :--- | :--- | :--- |
| **RQNF01** | GCP / Servidor en la Nube | Infraestructura | Google Cloud Platform / VPS como proveedor de infraestructura escalable y despliegue en la nube. |
| **RQNF02** | Django como CRM y Backend | Framework Web | Django 6.0 como arquitectura MVT, gestión de modelos, autenticación, context processors y panel administrativo. |
| **RQNF03** | Base de Datos Relacional | Base de Datos | Motor PostgreSQL / SQLite estructurado con integridad referencial, transacciones atómicas y backups periódicos. |
| **RQNF04** | JavaScript Nativo (ES6+) | Frontend | JavaScript Vanilla para modales interactivos de seguimiento de guías, dinamismo del carrito y transiciones. |
| **RQNF05** | Python 3.12+ | Lenguaje Backend | Python como lenguaje base para la lógica de negocio, integración SMTP de correos y generación de enlaces WhatsApp. |

---

## 6. MARCO DE AUTOGESTIÓN, LIDERAZGO ÉTICO Y PARÁMETROS SOCIALES (RAE)

El Resultado de Aprendizaje Esperado (RAE) del módulo de práctica establece la exigencia de formar ingenieros de software éticos, reflexivos y autónomos. En concordancia, este plan de trabajo integra formalmente las siguientes dimensiones:

### 6.1. Autogestión y Autorregulación en el Ámbito Laboral
- **Planificación y compromiso autónomo:** Estimación técnica rigurosa mediante puntos de historia, cumplimiento de timeboxes quincenales y autoevaluación continua del rendimiento técnico.
- **Aseguramiento proactivo de calidad:** Ejecución sistemática de una suite de 13 pruebas unitarias y de integración en Django, garantizando que ninguna funcionalidad se libere sin verificación previa.
- **Gestión de la incertidumbre y resolución de problemas:** Monitoreo preventivo de dependencias tecnológicas y mitigación ágil de impedimentos sin requerir supervisión invasiva.

### 6.2. Liderazgo Ético, Parámetros Sociales y Responsabilidad Profesional
- **Protección y Privacidad de Datos (Habeas Data):** En estricto cumplimiento de la Ley 1581 de 2012, el sistema no expone información sensible de clientes. Las contraseñas se almacenan mediante algoritmos criptográficos seguros (PBKDF2/SHA-256) y las direcciones de despacho se gestionan con confidencialidad.
- **Transparencia Comercial:** Presentación exacta de precios, desglose de artículos y condiciones de entrega sin costos ocultos, protegiendo los derechos del consumidor digital.
- **Propiedad Intelectual y Autoría:** Todo el desarrollo, código fuente y documentación es de autoría propia del estudiante, haciendo uso exclusivo de herramientas de código abierto con licenciamiento compatible, erradicando cualquier práctica de plagio.
- **Impacto Social en el Emprendimiento Local:** La transferencia tecnológica fortalece la sostenibilidad de una microempresa familiar, fomentando el comercio formal y la reactivación económica mediante software nacional.

---

## 7. METODOLOGÍA ÁGIL SCRUM, EDT Y CRONOGRAMA DE EJECUCIÓN

El desarrollo se rige por el marco ágil **Scrum**, estructurado en sprints de 2 semanas y soportado en tableros Kanban para el seguimiento de estados (*To Do, In Progress, QA/Test, Done*).

### 7.1. Cronograma de Sprints y Entregables

| Sprint / Fase | Semanas | Actividades de Ingeniería | Entregable Tangible |
| :--- | :---: | :--- | :--- |
| **Fase 1: Diagnóstico** | Sem 1 - 2 | Entrevistas con POs, especificación RQF/RQNF, diseño E-R y configuración de repositorio. | Plan de Trabajo, Diccionario de Datos y Repositorio Git inicializado. |
| **Sprint 1: Core & Catálogo** | Sem 3 - 4 | Modelos base (User, Categoria, Producto), vistas públicas de catálogo, filtros por categoría. | Módulo de Catálogo interactivo y panel administrativo base operativo. |
| **Sprint 2: Combos & Stock** | Sem 5 - 6 | Entidades Combo y CombosProductos (M2M), cálculo de descuentos y control de inventario. | Módulo de Combos y Sorpresas (scoops) con control de stock. |
| **Sprint 3: Carrito & WhatsApp** | Sem 7 - 8 | Carrito transaccional en sesión, context processor global, checkout y generador de URL WhatsApp. | Flujo completo de compra asistida con enlace directo a WhatsApp. |
| **Sprint 4: Correos & Tracking** | Sem 9 - 10 | Servicio SMTP Gmail, plantillas HTML, disparadores por estado (PAGADO, ENVIADO con guía). | Sistema de notificaciones automáticas y módulo Mis Pedidos con rastreo. |
| **Sprint 5: QA & Analítica** | Sem 11 - 12 | Desarrollo de suite de 13 pruebas automatizadas, dashboard analítico de ventas y reportes. | Suite de pruebas aprobada (100% OK) y módulo de métricas gerenciales. |
| **Fase 4: Cierre & Deploy** | Sem 13 - 14 | Pruebas en red local/túnel seguro, manual de usuario, manual técnico y capacitación a POs. | Manuales técnicos y de usuario entregados; sistema en producción. |

---

## 8. MATRIZ DE GESTIÓN DE RIESGOS Y PLAN DE CONTINGENCIA

| Riesgo Identificado | Prob. | Impacto | Plan de Mitigación / Acción de Contingencia |
| :--- | :---: | :---: | :--- |
| **R1. Inconsistencia o sobreventa de stock en pedidos simultáneos.** | Media | Alto | Transacciones atómicas (`atomic()`) y validación obligatoria de stock antes de crear `DetallePedido`. |
| **R2. Retraso en fechas de entrega de sprints.** | Media | Alto | Ajuste del backlog priorizando requerimientos Must-Have (MoSCoW) y sincronizaciones bisemanales. |
| **R3. Interrupción temporal del servicio SMTP de correos.** | Baja | Medio | Manejo de excepciones `try-except` con logging local para que el checkout nunca se bloquee. |
| **R4. Resistencia al cambio de clientes habituados al chat.** | Media | Alto | Integración del botón directo de WhatsApp con mensaje listo para enviar, combinando web y calidez humana. |
| **R5. Pérdida de datos por fallo en servidor local o nube.** | Baja | Crítico | Copias de respaldo diarias automatizadas y fixtures de datos iniciales (`datos_iniciales.json`). |

---

## 9. ESTIMACIÓN DE RECURSOS Y PRESUPUESTO ECONÓMICO

El presupuesto del proyecto se calculó con base en 129 horas de ingeniería estimadas (43 días a razón de 3 horas diarias de desarrollo) valoradas a una tarifa profesional de mercado de $80.000 COP/hora, sumando costos de infraestructura y contingencia:

| Rubro / Concepto | Categoría | Cantidad / Unidad | Costo Unitario (COP) | Subtotal (COP) |
| :--- | :--- | :---: | :---: | :---: |
| **Honorarios de Ingeniería de Software** | Esfuerzo Humano | 129 horas | $80.000 / h | **$10.320.000** |
| **Servidor en la Nube / VPS Hosting (GCP)** | Infraestructura | 1 Instancia Anual | $180.000 / año | $180.000 |
| **Certificados SSL/TLS y Dominio Web** | Seguridad | 1 Licencia Anual | $100.000 | $100.000 |
| **Conectividad a Internet de Alta Velocidad** | Indirecto | 4 meses | $80.000 / mes | $320.000 |
| **Energía Eléctrica y Servicios Públicos** | Indirecto | 4 meses | $25.000 / mes | $100.000 |
| **SUBTOTAL DIRECTO E INDIRECTO** | — | — | — | **$11.020.000** |
| **Margen de Contingencias e Imprevistos (20%)** | Contingencia | Reserva | 20% Subtotal | $2.204.000 |
| **TOTAL GENERAL DEL PROYECTO** | **Presupuesto** | **Total** | — | **$13.224.000** |

---

## 10. CONCLUSIONES Y RESULTADOS ESPERADOS

1. **Transformación Operativa del Emprendimiento:** La puesta en marcha de la tienda web «Sorpresas Kawaii» elimina la dependencia de canales informales, automatizando el catálogo, la verificación de inventario y el seguimiento de despachos con guías en tiempo real, lo que consolida la formalización del negocio y su capacidad de escalar ventas.
2. **Cumplimiento Integral del RAE:** El plan de trabajo permite evidenciar el dominio de competencias profesionales de alto nivel: autogestión en la planificación de sprints, disciplina técnica en la suite de pruebas unitarias y liderazgo ético en la protección rigurosa de datos personales y transparencia comercial frente a la comunidad.
3. **Mantenibilidad y Robustez Tecnológica:** La adopción de Django y una arquitectura modular MVT asegura que la plataforma pueda seguir expandiéndose a futuro (incorporación de pasarelas de pago adicionales o facturación electrónica) de manera ágil y con bajo costo de mantenimiento.

---

## 11. REFERENCIAS BIBLIOGRÁFICAS (NORMAS APA 7.ª EDICIÓN)

- Beck, K., Beedle, M., van Bennekum, A., Cockburn, A., Cunningham, W., Fowler, M., Grenning, J., Highsmith, J., Hunt, A., Jeffries, R., Kern, J., Marick, B., Martin, R. C., Mellor, S., Schwaber, K., Sutherland, J., & Thomas, D. (2001). *Manifesto for Agile Software Development*. Agile Alliance. https://agilemanifesto.org/
- Congreso de la República de Colombia. (2012, 17 de octubre). *Ley Estatutaria 1581 de 2012: Por la cual se dictan disposiciones generales para la protección de datos personales*. Diario Oficial No. 48.587.
- Django Software Foundation. (2025). *Django documentation (Version 6.0)*. https://docs.djangoproject.com/
- Omaña, M. (2012). Manufactura esbelta: una contribución para el desarrollo de software con calidad. *Red Enlace*, (5), 14–18.
- Pressman, R. S., & Maxim, B. R. (2021). *Ingeniería de software: Un enfoque práctico* (9.ª ed.). McGraw-Hill Interamericana.
- Schwaber, K., & Sutherland, J. (2020). *La Guía de Scrum: Las Reglas del Juego*. Scrum.org. https://scrumguides.org/
- Sommerville, I. (2011). *Ingeniería del software* (9.ª ed.). Pearson Educación.
