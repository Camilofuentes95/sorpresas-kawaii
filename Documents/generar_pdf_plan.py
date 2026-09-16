import os
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Canvas de ReportLab de 2 pasadas para calcular dinámicamente el total de páginas
    y añadir encabezados y números de página formales en formato APA 7.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        if self._pageNumber > 1:
            self.saveState()
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#4A5568"))
            
            # Encabezado formal (Running Head)
            header_text = "CORPORACIÓN UNIVERSITARIA IBEROAMERICANA | PLAN DE TRABAJO DE PRÁCTICA PROFESIONAL"
            self.drawString(54, 11 * inch - 36, header_text)
            self.setStrokeColor(colors.HexColor("#CBD5E0"))
            self.setLineWidth(0.5)
            self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)
            
            # Pie de página formal
            footer_text = f"Página {self._pageNumber} de {page_count}"
            author_text = "Camilo Alberto Fuentes Mahecha — Código: 100139562"
            self.line(54, 46, 8.5 * inch - 54, 46)
            self.drawString(54, 34, author_text)
            self.drawRightString(8.5 * inch - 54, 34, footer_text)
            self.restoreState()


def build_pdf(filename="Plan_de_Trabajo_Practicas_Camilo_Fuentes.pdf"):
    pdf_path = os.path.abspath(filename)
    
    # Márgenes (54 pt = 0.75 in para balance visual y elegancia)
    margin = 54
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=margin,
        bottomMargin=margin
    )
    
    styles = getSampleStyleSheet()
    
    # Paleta cromática formal e institucional
    primary_color = colors.HexColor("#1A365D")   # Azul marino institucional
    secondary_color = colors.HexColor("#2B6CB0") # Azul intermedio
    dark_neutral = colors.HexColor("#2D3748")    # Texto principal carbón
    light_bg = colors.HexColor("#F7FAFC")        # Fondo gris claro para tablas
    
    # Estilos tipográficos
    style_cover_uni = ParagraphStyle(
        'CoverUni',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        alignment=1,
        textColor=primary_color
    )
    
    style_cover_faculty = ParagraphStyle(
        'CoverFaculty',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        alignment=1,
        textColor=colors.HexColor("#4A5568")
    )
    
    style_cover_title = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        alignment=1,
        textColor=primary_color
    )
    
    style_cover_subtitle = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=12,
        leading=16,
        alignment=1,
        textColor=secondary_color
    )
    
    style_cover_body = ParagraphStyle(
        'CoverBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        alignment=1,
        textColor=dark_neutral
    )
    
    style_h1 = ParagraphStyle(
        'CustomH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=16.5,
        textColor=primary_color,
        spaceBefore=11,
        spaceAfter=5,
        keepWithNext=True
    )
    
    style_h2 = ParagraphStyle(
        'CustomH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14.5,
        textColor=secondary_color,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )
    
    style_body = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=dark_neutral,
        spaceAfter=5.5,
        alignment=4 # Justificado
    )
    
    style_bullet = ParagraphStyle(
        'CustomBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=dark_neutral,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3,
        alignment=4
    )
    
    style_table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        alignment=1,
        textColor=colors.white
    )
    
    style_table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=dark_neutral,
        alignment=0
    )
    
    style_table_cell_center = ParagraphStyle(
        'TableCellCenter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=dark_neutral,
        alignment=1
    )

    style_table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=dark_neutral,
        alignment=0
    )
    
    style_note = ParagraphStyle(
        'TableNote',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#718096"),
        spaceAfter=6
    )

    story = []
    
    # -------------------------------------------------------------
    # PORTADA INSTITUCIONAL FORMAL
    # -------------------------------------------------------------
    story.append(Spacer(1, 25))
    story.append(Paragraph("CORPORACIÓN UNIVERSITARIA IBEROAMERICANA", style_cover_uni))
    story.append(Paragraph("FACULTAD DE INGENIERÍA Y CIENCIAS BÁSICAS", style_cover_faculty))
    story.append(Paragraph("PROGRAMA DE INGENIERÍA DE SOFTWARE", style_cover_faculty))
    story.append(Paragraph("MÓDULO DE PRÁCTICA PROFESIONAL / ESCENARIO DE PRÁCTICAS", style_cover_faculty))
    
    story.append(Spacer(1, 40))
    story.append(HRFlowable(width="65%", thickness=2, color=primary_color, spaceAfter=25, spaceBefore=10))
    story.append(Paragraph("PLAN DE TRABAJO DE PRÁCTICA PROFESIONAL", style_cover_title))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Diseño, Desarrollo e Implementación de la Plataforma de Comercio Electrónico y Gestión de Inventarios «Sorpresas Kawaii»", style_cover_subtitle))
    story.append(HRFlowable(width="65%", thickness=2, color=primary_color, spaceAfter=45, spaceBefore=25))
    
    story.append(Spacer(1, 25))
    story.append(Paragraph("<b>AUTOR / PRACTICANTE:</b><br/>CAMILO ALBERTO FUENTES MAHECHA<br/>Código Estudiantil: 100139562", style_cover_body))
    story.append(Spacer(1, 25))
    story.append(Paragraph("<b>TUTOR ACADÉMICO / ASESOR DE PRÁCTICAS:</b><br/>TATIANA CABRERA", style_cover_body))
    story.append(Spacer(1, 25))
    story.append(Paragraph("<b>ESCENARIO DE PRÁCTICA:</b><br/>Emprendimiento Digital «Sorpresas Kawaii»", style_cover_body))
    
    story.append(Spacer(1, 40))
    story.append(Paragraph("Bogotá D.C., Colombia<br/>2025", style_cover_body))
    story.append(PageBreak())
    
    # -------------------------------------------------------------
    # RESUMEN EJECUTIVO
    # -------------------------------------------------------------
    story.append(Paragraph("RESUMEN EJECUTIVO", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=secondary_color, spaceAfter=8, spaceBefore=2))
    
    resumen_text = (
        "El presente Plan de Trabajo formula la propuesta de intervención técnica y profesional en el marco del módulo de "
        "Práctica Profesional de la Corporación Universitaria Iberoamericana. El proyecto se desarrolla en el escenario real del "
        "emprendimiento <b>«Sorpresas Kawaii»</b>, un negocio dedicado a la venta de artículos de papelería estética, peluches y cajas "
        "sorpresa temáticas (*mystery boxes* y *scoops*), cuya atracción de usuarios se fundamenta en la viralidad de redes sociales (TikTok e Instagram)."
    )
    story.append(Paragraph(resumen_text, style_body))
    
    resumen_text_2 = (
        "A partir de un diagnóstico profundo de la problemática empresarial, se identificó que la comercialización mediante chats y procesos "
        "manuales generaba descontrol crítico de existencias (sobreventas), pérdida de información de pedidos, ausencia de métricas de ingresos "
        "y riesgos en el tratamiento de datos personales de los compradores. Para solucionar esta necesidad, se plantea el desarrollo de una plataforma "
        "web estructurada bajo el patrón Modelo-Vista-Template (MVT) con el framework <b>Django (Python)</b>, incorporando módulos de catálogo interactivo, "
        "generador dinámico de combos con descuentos, sincronización transaccional de inventario en tiempo real, autenticación segura, notificaciones "
        "por correo electrónico y finalización ágil de compras asistida por la API de WhatsApp."
    )
    story.append(Paragraph(resumen_text_2, style_body))
    
    resumen_text_3 = (
        "El plan se rige por la metodología ágil <b>Scrum</b> y se orienta al cumplimiento del Resultado de Aprendizaje Esperado (RAE), desarrollando "
        "competencias de <b>autogestión, autorregulación y liderazgo ético</b> en la ingeniería de software (protección de datos bajo la Ley 1581 de 2012, "
        "honestidad intelectual y responsabilidad social). Se detallan la especificación formal de Requerimientos Funcionales y No Funcionales (RQF/RQNF), "
        "el cronograma por sprints, la matriz de riesgos y la estimación presupuestal bajo normas APA (7.ª edición)."
    )
    story.append(Paragraph(resumen_text_3, style_body))
    story.append(Paragraph("<b>Palabras clave:</b> <i>Plan de trabajo, práctica profesional, comercio electrónico, Django, Scrum, autogestión, liderazgo ético, Sorpresas Kawaii.</i>", style_body))
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------
    # 1. INTRODUCCIÓN
    # -------------------------------------------------------------
    story.append(Paragraph("1. INTRODUCCIÓN", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=secondary_color, spaceAfter=8, spaceBefore=2))
    
    intro_1 = (
        "En la actualidad, las microempresas y emprendimientos emergentes encuentran en los canales de video corto (como TikTok e Instagram) "
        "un dinamizador comercial sin precedentes para posicionar artículos de nicho. No obstante, este rápido crecimiento en demanda suele "
        "colapsar las operaciones cuando no existe una infraestructura tecnológica formal que soporte el catálogo, la verificación de inventario "
        "y la trazabilidad de los pedidos."
    )
    story.append(Paragraph(intro_1, style_body))
    
    intro_2 = (
        "El presente Plan de Trabajo establece las bases teóricas, metodológicas y prácticas para solucionar este déficit en el emprendimiento "
        "«Sorpresas Kawaii». Asimismo, el documento responde de manera estricta al propósito formativo del RAE del módulo de prácticas, consolidando "
        "habilidades de liderazgo ético, planeación autónoma del trabajo y desarrollo de software de alta calidad bajo estándares profesionales."
    )
    story.append(Paragraph(intro_2, style_body))

    # -------------------------------------------------------------
    # 2. CONTEXTUALIZACIÓN Y STAKEHOLDERS
    # -------------------------------------------------------------
    story.append(Paragraph("2. CONTEXTUALIZACIÓN DEL ESCENARIO DE PRÁCTICA Y STAKEHOLDERS", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=secondary_color, spaceAfter=8, spaceBefore=2))
    
    ctx_1 = (
        "<b>«Sorpresas Kawaii»</b> es una tienda digital especializada en papelería asiática y accesorios de diseño exclusivo de difícil acceso "
        "en papelerías tradicionales. La empresa carece de tienda física y centraliza su estrategia comercial en transmisiones y videos de redes sociales, "
        "donde las «cajas sorpresa» y «scoops» representan su principal factor diferenciador."
    )
    story.append(Paragraph(ctx_1, style_body))
    
    story.append(Paragraph("2.1. Mapa de Actores y Stakeholders", style_h2))
    story.append(Paragraph("• <b>Jenny López (Fundadora / Product Owner de Catálogo):</b> Define los productos a comercializar, combinaciones de combos y valida la identidad gráfica kawaii.", style_bullet))
    story.append(Paragraph("• <b>Andrea Guerrero (Fundadora / Product Owner de Costos y Finanzas):</b> Supervisa la rentabilidad, los márgenes de descuento y los reportes de ventas.", style_bullet))
    story.append(Paragraph("• <b>Camilo Alberto Fuentes Mahecha (Practicante / Desarrollador y Gestor del Proyecto):</b> Responsable del levantamiento de requisitos, arquitectura del sistema, desarrollo full-stack en Django, control de calidad, suite de pruebas automatizadas y despliegue.", style_bullet))
    story.append(Paragraph("• <b>Clientes Finales:</b> Usuarios compradores que demandan una experiencia interactiva, rápida, transparente y confiable desde dispositivos móviles y de escritorio.", style_bullet))

    # -------------------------------------------------------------
    # 3. DIAGNÓSTICO PROFUNDO DE LA SITUACIÓN PROBLEMA
    # -------------------------------------------------------------
    story.append(Paragraph("3. DIAGNÓSTICO PROFUNDO DE LA SITUACIÓN PROBLEMA", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=secondary_color, spaceAfter=8, spaceBefore=2))
    
    prob_1 = (
        "El análisis diagnóstico realizado en la organización demostró que la gestión manual de ventas por mensajes directos (DM) causaba "
        "cuellos de botella operacionales severos:"
    )
    story.append(Paragraph(prob_1, style_body))
    
    story.append(Paragraph("• <b>Saturación y demoras en atención:</b> En picos de viralidad, responder manualmente a cada cliente sobre precios y disponibilidad generaba demoras de hasta 24 horas y pérdida de ventas.", style_bullet))
    story.append(Paragraph("• <b>Desincronización de inventario y sobreventas:</b> El registro no automatizado permitía vender productos agotados a diferentes usuarios simultáneamente, causando reprocesos y devoluciones.", style_bullet))
    story.append(Paragraph("• <b>Vulnerabilidad en datos personales:</b> La recopilación no estandarizada de direcciones y teléfonos por chat contravenía la Ley 1581 de 2012 (Habeas Data).", style_bullet))
    story.append(Paragraph("• <b>Inexistencia de reportes financieros:</b> Falta de consolidación de ingresos y rotación de stock para planificar compras a proveedores.", style_bullet))
    story.append(Paragraph("• <b>Falta de trazabilidad post-venta:</b> Ausencia de confirmación formal por correo y desconocimiento del número de guía de envío por parte del cliente.", style_bullet))
    
    prob_2 = (
        "De acuerdo con Pressman y Maxim (2021) y los principios de desarrollo esbelto (Omaña, 2012), la sistematización e integración de estos flujos "
        "en una arquitectura web transaccional elimina el desperdicio operativo y maximiza el valor percibido por el cliente."
    )
    story.append(Paragraph(prob_2, style_body))

    # -------------------------------------------------------------
    # 4. OBJETIVOS Y MATRIZ DE ALINEACIÓN
    # -------------------------------------------------------------
    story.append(Paragraph("4. OBJETIVOS DEL PLAN DE TRABAJO Y ALINEACIÓN", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=secondary_color, spaceAfter=8, spaceBefore=2))
    
    story.append(Paragraph("4.1. Objetivo General", style_h2))
    obj_gen = (
        "Diseñar, desarrollar e implementar una plataforma web de comercio electrónico y gestión administrativa para el emprendimiento "
        "<b>«Sorpresas Kawaii»</b>, automatizando el catálogo digital, la administración de inventario en tiempo real, los combos temáticos, "
        "el procesamiento seguro de órdenes y la generación de reportes, fortaleciendo competencias de autogestión y liderazgo ético."
    )
    story.append(Paragraph(obj_gen, style_body))
    
    story.append(Paragraph("4.2. Matriz de Relación entre Objetivos Específicos y Problemática", style_h2))
    
    table_obj_data = [
        [
            Paragraph("Objetivo Específico", style_table_header),
            Paragraph("Problemática en la Empresa", style_table_header),
            Paragraph("Solución Técnica de Ingeniería", style_table_header),
            Paragraph("Impacto Operativo", style_table_header)
        ],
        [
            Paragraph("<b>OE1.</b> Implementar arquitectura de datos y panel administrativo seguro.", style_table_cell),
            Paragraph("Desorden en información y acceso no controlado a datos de productos y clientes.", style_table_cell),
            Paragraph("Modelos Django ORM (User, Categoria, Producto, Combo, Pedido) con control de acceso y seguridad CSRF/XSS.", style_table_cell),
            Paragraph("Centralización y protección total de los datos del negocio.", style_table_cell)
        ],
        [
            Paragraph("<b>OE2.</b> Desarrollar catálogo interactivo con combos y sorpresas (scoops).", style_table_cell),
            Paragraph("Clientes no conocen stock real ni combinaciones de combos, saturando chats.", style_table_cell),
            Paragraph("Frontend modular responsive con diseño kawaii personalizado y vistas dinámicas en Django.", style_table_cell),
            Paragraph("Autonomía total del cliente para explorar y seleccionar productos 24/7.", style_table_cell)
        ],
        [
            Paragraph("<b>OE3.</b> Integrar carrito de compras con sincronización de stock en tiempo real.", style_table_cell),
            Paragraph("Sobreventas recurrentes de artículos agotados por conteo manual.", style_table_cell),
            Paragraph("Lógica de sesión transaccional con actualización automática de stock al confirmar el pedido.", style_table_cell),
            Paragraph("Eliminación del 100% de errores de sobreventa e inconsistencias.", style_table_cell)
        ],
        [
            Paragraph("<b>OE4.</b> Automatizar checkout con WhatsApp API y notificaciones SMTP.", style_table_cell),
            Paragraph("Falta de formalidad en la orden y demoras en seguimiento de despachos.", style_table_cell),
            Paragraph("Generador de URL Click-to-Chat preformateada y disparador de correos automáticos por estado de pedido.", style_table_cell),
            Paragraph("Reducción del 80% en tiempo de atención y fidelización del comprador.", style_table_cell)
        ],
        [
            Paragraph("<b>OE5.</b> Construir módulo analítico de reportes y control de inventario.", style_table_cell),
            Paragraph("Toma de decisiones empírica sin datos de ventas ni rotación de productos.", style_table_cell),
            Paragraph("Consultas agregadas ORM con filtros por fecha, cálculo de ingresos y alertas de stock bajo.", style_table_cell),
            Paragraph("Planeación financiera y de reposición sustentada en datos reales.", style_table_cell)
        ]
    ]
    
    col_widths_1 = [110, 120, 140, 134]
    t1 = Table(table_obj_data, colWidths=col_widths_1, repeatRows=1)
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, light_bg]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t1)
    story.append(Paragraph("<i>Tabla 1. Matriz de alineación de objetivos específicos frente a la problemática empresarial. Fuente: Elaboración propia (2025).</i>", style_note))
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------
    # 5. ESPECIFICACIÓN DE REQUERIMIENTOS (RQF Y RQNF)
    # -------------------------------------------------------------
    story.append(Paragraph("5. ESPECIFICACIÓN DE REQUERIMIENTOS DEL SISTEMA (RQF Y RQNF)", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=secondary_color, spaceAfter=8, spaceBefore=2))
    
    story.append(Paragraph("5.1. Requerimientos Funcionales (RQF)", style_h2))
    
    table_rqf_data = [
        [
            Paragraph("ID", style_table_header),
            Paragraph("Nombre del Requerimiento", style_table_header),
            Paragraph("Descripción Funcional Detallada", style_table_header),
            Paragraph("Actor / Rol", style_table_header)
        ],
        [
            Paragraph("<b>RQF01</b>", style_table_cell_center),
            Paragraph("Registrar productos", style_table_cell_bold),
            Paragraph("Permitir al administrador registrar, editar y listar productos con nombre, valor, categoría, descripción, stock e imágenes.", style_table_cell),
            Paragraph("PO de Catálogo / Admin", style_table_cell)
        ],
        [
            Paragraph("<b>RQF02</b>", style_table_cell_center),
            Paragraph("Registrar combos", style_table_cell_bold),
            Paragraph("Permitir generar combos o cajas sorpresa de hasta 5 productos con cálculo de descuento porcentual y precio final.", style_table_cell),
            Paragraph("PO de Catálogo / Admin", style_table_cell)
        ],
        [
            Paragraph("<b>RQF03</b>", style_table_cell_center),
            Paragraph("Carrito de compras", style_table_cell_bold),
            Paragraph("Proveer al usuario un carrito reactivo donde visualice ítems, cantidades, subtotales y pueda confirmar el pedido.", style_table_cell),
            Paragraph("Cliente / PO de Costos", style_table_cell)
        ],
        [
            Paragraph("<b>RQF04</b>", style_table_cell_center),
            Paragraph("Actualización de inventario", style_table_cell_bold),
            Paragraph("Actualización automática de existencias tras cada compra confirmada y gestión de stock desde el panel de control.", style_table_cell),
            Paragraph("PO de Catálogo / Sistema", style_table_cell)
        ],
        [
            Paragraph("<b>RQF05</b>", style_table_cell_center),
            Paragraph("Reportes de ventas", style_table_cell_bold),
            Paragraph("Generación de resúmenes de ingresos totales, ventas por rango de fechas y reporte de stock vendido por producto.", style_table_cell),
            Paragraph("PO de Costos / Admin", style_table_cell)
        ],
        [
            Paragraph("<b>RQF06</b>", style_table_cell_center),
            Paragraph("Autenticación y Login", style_table_cell_bold),
            Paragraph("Permitir inicio de sesión, registro de clientes y recuperación segura de contraseñas por correo electrónico.", style_table_cell),
            Paragraph("Todos los usuarios", style_table_cell)
        ]
    ]
    
    col_widths_rqf = [55, 120, 209, 120]
    t_rqf = Table(table_rqf_data, colWidths=col_widths_rqf, repeatRows=1)
    t_rqf.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, light_bg]),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    story.append(t_rqf)
    story.append(Paragraph("<i>Tabla 2. Requerimientos funcionales del sistema. Fuente: Elaboración propia (2025).</i>", style_note))
    story.append(Spacer(1, 6))

    story.append(Paragraph("5.2. Requerimientos No Funcionales (RQNF)", style_h2))
    
    table_rqnf_data = [
        [
            Paragraph("ID", style_table_header),
            Paragraph("Nombre / Dimensión", style_table_header),
            Paragraph("Tipo", style_table_header),
            Paragraph("Especificación Técnica", style_table_header)
        ],
        [
            Paragraph("<b>RQNF01</b>", style_table_cell_center),
            Paragraph("GCP / Servidor en la Nube", style_table_cell_bold),
            Paragraph("Infraestructura", style_table_cell),
            Paragraph("Google Cloud Platform / VPS como proveedor de infraestructura escalable y despliegue en la nube.", style_table_cell)
        ],
        [
            Paragraph("<b>RQNF02</b>", style_table_cell_center),
            Paragraph("Django como CRM y Backend", style_table_cell_bold),
            Paragraph("Framework Web", style_table_cell),
            Paragraph("Django 6.0 como arquitectura MVT, gestión de modelos, autenticación, context processors y panel administrativo.", style_table_cell)
        ],
        [
            Paragraph("<b>RQNF03</b>", style_table_cell_center),
            Paragraph("Base de Datos Relacional", style_table_cell_bold),
            Paragraph("Base de Datos", style_table_cell),
            Paragraph("Motor PostgreSQL / SQLite estructurado con integridad referencial, transacciones atómicas y backups periódicos.", style_table_cell)
        ],
        [
            Paragraph("<b>RQNF04</b>", style_table_cell_center),
            Paragraph("JavaScript Nativo (ES6+)", style_table_cell_bold),
            Paragraph("Frontend", style_table_cell),
            Paragraph("JavaScript Vanilla para modales interactivos de seguimiento de guías, dinamismo del carrito y transiciones.", style_table_cell)
        ],
        [
            Paragraph("<b>RQNF05</b>", style_table_cell_center),
            Paragraph("Python 3.12+", style_table_cell_bold),
            Paragraph("Lenguaje Backend", style_table_cell),
            Paragraph("Python como lenguaje base para la lógica de negocio, integración SMTP de correos y generación de enlaces WhatsApp.", style_table_cell)
        ]
    ]
    
    col_widths_rqnf = [55, 130, 95, 224]
    t_rqnf = Table(table_rqnf_data, colWidths=col_widths_rqnf, repeatRows=1)
    t_rqnf.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, light_bg]),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    story.append(t_rqnf)
    story.append(Paragraph("<i>Tabla 3. Requerimientos no funcionales del sistema. Fuente: Elaboración propia (2025).</i>", style_note))
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------
    # 6. MARCO DE AUTOGESTIÓN Y LIDERAZGO ÉTICO (RAE)
    # -------------------------------------------------------------
    story.append(Paragraph("6. MARCO DE AUTOGESTIÓN, LIDERAZGO ÉTICO Y PARÁMETROS SOCIALES (RAE)", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=secondary_color, spaceAfter=8, spaceBefore=2))
    
    rae_intro = (
        "El Resultado de Aprendizaje Esperado (RAE) del módulo de práctica establece la exigencia de formar ingenieros de software "
        "éticos, reflexivos y autónomos. En concordancia, este plan de trabajo integra formalmente las siguientes dimensiones:"
    )
    story.append(Paragraph(rae_intro, style_body))
    
    story.append(Paragraph("6.1. Autogestión y Autorregulación en el Ámbito Laboral", style_h2))
    story.append(Paragraph("• <b>Planificación y compromiso autónomo:</b> Estimación técnica rigurosa mediante puntos de historia, cumplimiento de timeboxes quincenales y autoevaluación continua del rendimiento técnico.", style_bullet))
    story.append(Paragraph("• <b>Aseguramiento proactivo de calidad:</b> Ejecución sistemática de una suite de 13 pruebas unitarias y de integración en Django, garantizando que ninguna funcionalidad se libere sin verificación previa.", style_bullet))
    story.append(Paragraph("• <b>Gestión de la incertidumbre y resolución de problemas:</b> Monitoreo preventivo de dependencias tecnológicas y mitigación ágil de impedimentos sin requerir supervisión invasiva.", style_bullet))
    
    story.append(Paragraph("6.2. Liderazgo Ético, Parámetros Sociales y Responsabilidad Profesional", style_h2))
    story.append(Paragraph("• <b>Protección y Privacidad de Datos (Habeas Data):</b> En estricto cumplimiento de la Ley 1581 de 2012, el sistema no expone información sensible de clientes. Las contraseñas se almacenan mediante algoritmos criptográficos seguros (PBKDF2/SHA-256) y las direcciones de despacho se gestionan con confidencialidad.", style_bullet))
    story.append(Paragraph("• <b>Transparencia Comercial:</b> Presentación exacta de precios, desglose de artículos y condiciones de entrega sin costos ocultos, protegiendo los derechos del consumidor digital.", style_bullet))
    story.append(Paragraph("• <b>Propiedad Intelectual y Autoría:</b> Todo el desarrollo, código fuente y documentación es de autoría propia del estudiante, haciendo uso exclusivo de herramientas de código abierto con licenciamiento compatible, erradicando cualquier práctica de plagio.", style_bullet))
    story.append(Paragraph("• <b>Impacto Social en el Emprendimiento Local:</b> La transferencia tecnológica fortalece la sostenibilidad de una microempresa familiar, fomentando el comercio formal y la reactivación económica mediante software nacional.", style_bullet))

    # -------------------------------------------------------------
    # 7. METODOLOGÍA ÁGIL SCRUM Y CRONOGRAMA
    # -------------------------------------------------------------
    story.append(Paragraph("7. METODOLOGÍA ÁGIL SCRUM, EDT Y CRONOGRAMA DE EJECUCIÓN", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=secondary_color, spaceAfter=8, spaceBefore=2))
    
    scrum_text = (
        "El desarrollo se rige por el marco ágil <b>Scrum</b>, estructurado en sprints de 2 semanas y soportado en tableros Kanban "
        "para el seguimiento de estados (<i>To Do, In Progress, QA/Test, Done</i>). A continuación, se detalla el cronograma de sprints:"
    )
    story.append(Paragraph(scrum_text, style_body))
    
    table_sprint_data = [
        [
            Paragraph("Sprint / Fase", style_table_header),
            Paragraph("Semanas", style_table_header),
            Paragraph("Actividades de Ingeniería", style_table_header),
            Paragraph("Entregable Tangible", style_table_header)
        ],
        [
            Paragraph("<b>Fase 1: Diagnóstico</b>", style_table_cell),
            Paragraph("Sem 1 - 2", style_table_cell_center),
            Paragraph("Entrevistas con POs, especificación RQF/RQNF, diseño E-R y configuración de repositorio.", style_table_cell),
            Paragraph("Plan de Trabajo, Diccionario de Datos y Repositorio Git inicializado.", style_table_cell)
        ],
        [
            Paragraph("<b>Sprint 1: Core & Catálogo</b>", style_table_cell),
            Paragraph("Sem 3 - 4", style_table_cell_center),
            Paragraph("Modelos base (User, Categoria, Producto), vistas públicas de catálogo, filtros por categoría.", style_table_cell),
            Paragraph("Módulo de Catálogo interactivo y panel administrativo base operativo.", style_table_cell)
        ],
        [
            Paragraph("<b>Sprint 2: Combos & Stock</b>", style_table_cell),
            Paragraph("Sem 5 - 6", style_table_cell_center),
            Paragraph("Entidades Combo y CombosProductos (M2M), cálculo de descuentos y control de inventario.", style_table_cell),
            Paragraph("Módulo de Combos y Sorpresas (scoops) con control de stock.", style_table_cell)
        ],
        [
            Paragraph("<b>Sprint 3: Carrito & WhatsApp</b>", style_table_cell),
            Paragraph("Sem 7 - 8", style_table_cell_center),
            Paragraph("Carrito transaccional en sesión, context processor global, checkout y generador de URL WhatsApp.", style_table_cell),
            Paragraph("Flujo completo de compra asistida con enlace directo a WhatsApp.", style_table_cell)
        ],
        [
            Paragraph("<b>Sprint 4: Correos & Tracking</b>", style_table_cell),
            Paragraph("Sem 9 - 10", style_table_cell_center),
            Paragraph("Servicio SMTP Gmail, plantillas HTML, disparadores por estado (PAGADO, ENVIADO con guía).", style_table_cell),
            Paragraph("Sistema de notificaciones automáticas y módulo Mis Pedidos con rastreo.", style_table_cell)
        ],
        [
            Paragraph("<b>Sprint 5: QA & Analítica</b>", style_table_cell),
            Paragraph("Sem 11 - 12", style_table_cell_center),
            Paragraph("Desarrollo de suite de 13 pruebas automatizadas, dashboard analítico de ventas y reportes.", style_table_cell),
            Paragraph("Suite de pruebas aprobada (100% OK) y módulo de métricas gerenciales.", style_table_cell)
        ],
        [
            Paragraph("<b>Fase 4: Cierre & Deploy</b>", style_table_cell),
            Paragraph("Sem 13 - 14", style_table_cell_center),
            Paragraph("Pruebas en red local/túnel seguro, manual de usuario, manual técnico y capacitación a POs.", style_table_cell),
            Paragraph("Manuales técnicos y de usuario entregados; sistema en producción.", style_table_cell)
        ]
    ]
    
    col_widths_2 = [110, 55, 185, 154]
    t2 = Table(table_sprint_data, colWidths=col_widths_2, repeatRows=1)
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, light_bg]),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    story.append(t2)
    story.append(Paragraph("<i>Tabla 4. Cronograma de actividades y entregables por sprints Scrum. Fuente: Elaboración propia (2025).</i>", style_note))
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------
    # 8. MATRIZ DE RIESGOS
    # -------------------------------------------------------------
    story.append(Paragraph("8. MATRIZ DE GESTIÓN DE RIESGOS Y PLAN DE CONTINGENCIA", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=secondary_color, spaceAfter=8, spaceBefore=2))
    
    table_risk_data = [
        [
            Paragraph("Riesgo Identificado", style_table_header),
            Paragraph("Prob.", style_table_header),
            Paragraph("Impacto", style_table_header),
            Paragraph("Plan de Mitigación / Acción de Contingencia", style_table_header)
        ],
        [
            Paragraph("<b>R1.</b> Inconsistencia o sobreventa de stock en pedidos simultáneos.", style_table_cell),
            Paragraph("Media", style_table_cell_center),
            Paragraph("Alto", style_table_cell_center),
            Paragraph("Transacciones atómicas (`atomic()`) y validación obligatoria de stock antes de crear `DetallePedido`.", style_table_cell)
        ],
        [
            Paragraph("<b>R2.</b> Retraso en fechas de entrega de sprints.", style_table_cell),
            Paragraph("Media", style_table_cell_center),
            Paragraph("Alto", style_table_cell_center),
            Paragraph("Ajuste del backlog priorizando requerimientos Must-Have (MoSCoW) y sincronizaciones bisemanales.", style_table_cell)
        ],
        [
            Paragraph("<b>R3.</b> Interrupción temporal del servicio SMTP de correos.", style_table_cell),
            Paragraph("Baja", style_table_cell_center),
            Paragraph("Medio", style_table_cell_center),
            Paragraph("Manejo de excepciones `try-except` con logging local para que el checkout nunca se bloquee.", style_table_cell)
        ],
        [
            Paragraph("<b>R4.</b> Resistencia al cambio de clientes habituados al chat de Instagram/TikTok.", style_table_cell),
            Paragraph("Media", style_table_cell_center),
            Paragraph("Alto", style_table_cell_center),
            Paragraph("Integración del botón directo de WhatsApp con mensaje listo para enviar, combinando web y calidez humana.", style_table_cell)
        ],
        [
            Paragraph("<b>R5.</b> Pérdida de datos por fallo en servidor local o nube.", style_table_cell),
            Paragraph("Baja", style_table_cell_center),
            Paragraph("Crítico", style_table_cell_center),
            Paragraph("Copias de respaldo diarias automatizadas y fixtures de datos iniciales (`datos_iniciales.json`).", style_table_cell)
        ]
    ]
    
    col_widths_3 = [130, 45, 50, 279]
    t3 = Table(table_risk_data, colWidths=col_widths_3, repeatRows=1)
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, light_bg]),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    story.append(t3)
    story.append(Paragraph("<i>Tabla 5. Matriz de riesgos técnicos y operacionales. Fuente: Elaboración propia (2025).</i>", style_note))
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------
    # 9. PRESUPUESTO Y RECURSOS
    # -------------------------------------------------------------
    story.append(Paragraph("9. ESTIMACIÓN DE RECURSOS Y PRESUPUESTO ECONÓMICO", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=secondary_color, spaceAfter=8, spaceBefore=2))
    
    pres_text = (
        "El presupuesto del proyecto se calculó con base en 129 horas de ingeniería estimadas (43 días a razón de 3 horas diarias "
        "de desarrollo) valoradas a una tarifa profesional de mercado de $80.000 COP/hora, sumando costos de infraestructura y contingencia:"
    )
    story.append(Paragraph(pres_text, style_body))
    
    table_cost_data = [
        [
            Paragraph("Rubro / Concepto", style_table_header),
            Paragraph("Categoría", style_table_header),
            Paragraph("Cantidad / Unidad", style_table_header),
            Paragraph("Costo Unitario (COP)", style_table_header),
            Paragraph("Subtotal (COP)", style_table_header)
        ],
        [
            Paragraph("Honorarios de Ingeniería de Software", style_table_cell),
            Paragraph("Esfuerzo Humano", style_table_cell),
            Paragraph("129 horas", style_table_cell_center),
            Paragraph("$80.000 / h", style_table_cell_center),
            Paragraph("$10.320.000", style_table_cell_bold)
        ],
        [
            Paragraph("Servidor en la Nube / VPS Hosting (GCP)", style_table_cell),
            Paragraph("Infraestructura", style_table_cell),
            Paragraph("1 Instancia Anual", style_table_cell_center),
            Paragraph("$180.000 / año", style_table_cell_center),
            Paragraph("$180.000", style_table_cell)
        ],
        [
            Paragraph("Certificados SSL/TLS y Dominio Web", style_table_cell),
            Paragraph("Seguridad", style_table_cell),
            Paragraph("1 Licencia Anual", style_table_cell_center),
            Paragraph("$100.000", style_table_cell_center),
            Paragraph("$100.000", style_table_cell)
        ],
        [
            Paragraph("Conectividad a Internet de Alta Velocidad", style_table_cell),
            Paragraph("Indirecto", style_table_cell),
            Paragraph("4 meses", style_table_cell_center),
            Paragraph("$80.000 / mes", style_table_cell_center),
            Paragraph("$320.000", style_table_cell)
        ],
        [
            Paragraph("Energía Eléctrica y Servicios Públicos", style_table_cell),
            Paragraph("Indirecto", style_table_cell),
            Paragraph("4 meses", style_table_cell_center),
            Paragraph("$25.000 / mes", style_table_cell_center),
            Paragraph("$100.000", style_table_cell)
        ],
        [
            Paragraph("<b>SUBTOTAL DIRECTO E INDIRECTO</b>", style_table_cell_bold),
            Paragraph("—", style_table_cell_center),
            Paragraph("—", style_table_cell_center),
            Paragraph("—", style_table_cell_center),
            Paragraph("<b>$11.020.000</b>", style_table_cell_bold)
        ],
        [
            Paragraph("<b>Margen de Contingencias e Imprevistos (20%)</b>", style_table_cell),
            Paragraph("Contingencia", style_table_cell),
            Paragraph("Reserva", style_table_cell_center),
            Paragraph("20% Subtotal", style_table_cell_center),
            Paragraph("$2.204.000", style_table_cell)
        ],
        [
            Paragraph("<b>TOTAL GENERAL DEL PROYECTO</b>", style_table_cell_bold),
            Paragraph("Presupuesto", style_table_cell_bold),
            Paragraph("Total", style_table_cell_center),
            Paragraph("—", style_table_cell_center),
            Paragraph("<b>$13.224.000</b>", style_table_cell_bold)
        ]
    ]
    
    col_widths_4 = [150, 85, 95, 85, 89]
    t4 = Table(table_cost_data, colWidths=col_widths_4, repeatRows=1)
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -3), [colors.white, light_bg]),
        ('BACKGROUND', (0, -3), (-1, -3), colors.HexColor("#E2E8F0")),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#CBD5E0")),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
    ]))
    story.append(t4)
    story.append(Paragraph("<i>Tabla 6. Presupuesto detallado del proyecto de software. Fuente: Elaboración propia (2025).</i>", style_note))
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------
    # 10. CONCLUSIONES Y RESULTADOS ESPERADOS
    # -------------------------------------------------------------
    story.append(Paragraph("10. CONCLUSIONES Y RESULTADOS ESPERADOS", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=secondary_color, spaceAfter=8, spaceBefore=2))
    
    concl_1 = (
        "1. <b>Transformación Operativa del Emprendimiento:</b> La puesta en marcha de la tienda web «Sorpresas Kawaii» elimina la "
        "dependencia de canales informales, automatizando el catálogo, la verificación de inventario y el seguimiento de despachos con guías "
        "en tiempo real, lo que consolida la formalización del negocio y su capacidad de escalar ventas."
    )
    story.append(Paragraph(concl_1, style_body))
    
    concl_2 = (
        "2. <b>Cumplimiento Integral del RAE:</b> El plan de trabajo permite evidenciar el dominio de competencias profesionales de alto "
        "nivel: autogestión en la planificación de sprints, disciplina técnica en la suite de pruebas unitarias y liderazgo ético en la "
        "protección rigurosa de datos personales y transparencia comercial frente a la comunidad."
    )
    story.append(Paragraph(concl_2, style_body))
    
    concl_3 = (
        "3. <b>Mantenibilidad y Robustez Tecnológica:</b> La adopción de Django y una arquitectura modular MVT asegura que la plataforma "
        "pueda seguir expandiéndose a futuro (incorporación de pasarelas de pago adicionales o facturación electrónica) de manera ágil "
        "y con bajo costo de mantenimiento."
    )
    story.append(Paragraph(concl_3, style_body))
    story.append(Spacer(1, 8))

    # -------------------------------------------------------------
    # 11. REFERENCIAS BIBLIOGRÁFICAS
    # -------------------------------------------------------------
    story.append(Paragraph("11. REFERENCIAS BIBLIOGRÁFICAS (NORMAS APA 7.ª EDICIÓN)", style_h1))
    story.append(HRFlowable(width="100%", thickness=1, color=secondary_color, spaceAfter=8, spaceBefore=2))
    
    refs = [
        "Beck, K., Beedle, M., van Bennekum, A., Cockburn, A., Cunningham, W., Fowler, M., Grenning, J., Highsmith, J., Hunt, A., Jeffries, R., Kern, J., Marick, B., Martin, R. C., Mellor, S., Schwaber, K., Sutherland, J., & Thomas, D. (2001). <i>Manifesto for Agile Software Development</i>. Agile Alliance. https://agilemanifesto.org/",
        "Congreso de la República de Colombia. (2012, 17 de octubre). <i>Ley Estatutaria 1581 de 2012: Por la cual se dictan disposiciones generales para la protección de datos personales</i>. Diario Oficial No. 48.587.",
        "Django Software Foundation. (2025). <i>Django documentation (Version 6.0)</i>. https://docs.djangoproject.com/",
        "Omaña, M. (2012). Manufactura esbelta: una contribución para el desarrollo de software con calidad. <i>Red Enlace</i>, (5), 14–18.",
        "Pressman, R. S., & Maxim, B. R. (2021). <i>Ingeniería de software: Un enfoque práctico</i> (9.ª ed.). McGraw-Hill Interamericana.",
        "Schwaber, K., & Sutherland, J. (2020). <i>La Guía de Scrum: Las Reglas del Juego</i>. Scrum.org. https://scrumguides.org/",
        "Sommerville, I. (2011). <i>Ingeniería del software</i> (9.ª ed.). Pearson Educación."
    ]
    
    for ref in refs:
        ref_style = ParagraphStyle(
            'RefStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=8.5,
            leading=12,
            textColor=dark_neutral,
            leftIndent=24,
            firstLineIndent=-24,
            spaceAfter=6,
            alignment=4
        )
        story.append(Paragraph(ref, ref_style))
        
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generado exitosamente en: {pdf_path}")

if __name__ == "__main__":
    build_pdf()
