"""
Generador de Base de Conocimiento Institucional — SAE
Crea 5 documentos PDF realistas para el RAG:
  1. Reglamento Académico Universitario
  2. Protocolo de Intervención para Estudiantes en Riesgo
  3. Guía Completa de Técnicas de Estudio
  4. Directorio de Recursos y Servicios de Apoyo
  5. Plan de Mejoramiento Académico por Área
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "documentos_rag")
os.makedirs(OUT, exist_ok=True)

W, H = A4
AZUL = colors.HexColor('#1a237e')
AZUL_CLARO = colors.HexColor('#3949ab')
GRIS = colors.HexColor('#546e7a')
ROJO = colors.HexColor('#c62828')
VERDE = colors.HexColor('#2e7d32')
FONDO = colors.HexColor('#f5f5f5')


def base_styles():
    s = getSampleStyleSheet()
    styles = {
        'titulo': ParagraphStyle('titulo', parent=s['Title'], fontSize=20, textColor=AZUL,
                                  spaceAfter=6, alignment=TA_CENTER, leading=24),
        'subtitulo': ParagraphStyle('subtitulo', parent=s['Normal'], fontSize=12, textColor=GRIS,
                                     spaceAfter=16, alignment=TA_CENTER),
        'h1': ParagraphStyle('h1', parent=s['Heading1'], fontSize=14, textColor=AZUL,
                              spaceBefore=14, spaceAfter=6, leading=18),
        'h2': ParagraphStyle('h2', parent=s['Heading2'], fontSize=12, textColor=AZUL_CLARO,
                              spaceBefore=10, spaceAfter=4),
        'h3': ParagraphStyle('h3', parent=s['Heading3'], fontSize=10, textColor=GRIS,
                              spaceBefore=6, spaceAfter=3, fontName='Helvetica-Bold'),
        'body': ParagraphStyle('body', parent=s['Normal'], fontSize=9.5, leading=14,
                                alignment=TA_JUSTIFY, spaceAfter=6),
        'bullet': ParagraphStyle('bullet', parent=s['Normal'], fontSize=9.5, leading=14,
                                  leftIndent=16, spaceAfter=3),
        'nota': ParagraphStyle('nota', parent=s['Normal'], fontSize=8.5, textColor=GRIS,
                                leftIndent=12, fontName='Helvetica-Oblique', spaceAfter=4),
        'tabla_hdr': ParagraphStyle('tabla_hdr', parent=s['Normal'], fontSize=9,
                                     fontName='Helvetica-Bold', textColor=colors.white),
        'tabla_cel': ParagraphStyle('tabla_cel', parent=s['Normal'], fontSize=8.5, leading=12),
    }
    return styles


def doc(path, title, content_fn):
    d = SimpleDocTemplate(path, pagesize=A4,
                          leftMargin=2.2*cm, rightMargin=2.2*cm,
                          topMargin=2*cm, bottomMargin=2*cm)
    st = base_styles()
    elems = []
    content_fn(elems, st)
    d.build(elems)
    print(f"  [OK] {os.path.basename(path)}")


def hr(elems):
    elems.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc'), spaceAfter=8))


def sp(elems, h=0.3):
    elems.append(Spacer(1, h*cm))


# ═══════════════════════════════════════════════════════════════════
# DOCUMENTO 1: Reglamento Académico
# ═══════════════════════════════════════════════════════════════════
def gen_reglamento(elems, st):
    elems.append(Paragraph("UNIVERSIDAD NACIONAL TECNOLÓGICA", st['titulo']))
    elems.append(Paragraph("Reglamento Académico Estudiantil — Versión 2024", st['subtitulo']))
    hr(elems); sp(elems)

    elems.append(Paragraph("CAPÍTULO I: SISTEMA DE EVALUACIÓN", st['h1']))
    elems.append(Paragraph(
        "Art. 1. El sistema de evaluación de la Universidad Nacional Tecnológica (UNT) está basado en una "
        "escala de 0.0 a 10.0. La nota mínima de aprobación para cualquier asignatura es 6.0 puntos. "
        "Las evaluaciones parciales tienen un peso del 30% cada una, y el examen final el 40% restante.",
        st['body']))

    elems.append(Paragraph("Art. 2. Modalidades de evaluación:", st['h2']))
    for item in [
        "Parcial 1 (semana 5): 30% de la nota final.",
        "Parcial 2 (semana 10): 30% de la nota final.",
        "Examen final (semana 16): 40% de la nota final.",
        "Talleres y trabajos: se suman como bonificación hasta 0.5 puntos sobre la nota final.",
        "Quizzes sorpresa: pueden reemplazar hasta el 10% de un parcial si el docente lo dispone.",
    ]:
        elems.append(Paragraph(f"• {item}", st['bullet']))
    sp(elems)

    elems.append(Paragraph("Art. 3. Habilitación y supletorios:", st['h2']))
    elems.append(Paragraph(
        "El estudiante que obtenga entre 4.0 y 5.9 en la nota definitiva tiene derecho a un examen de "
        "habilitación. La nota máxima que puede obtenerse mediante habilitación es 6.0. "
        "No hay segunda habilitación. El examen supletorio aplica únicamente por enfermedad grave "
        "debidamente certificada o calamidad doméstica comprobada.", st['body']))

    elems.append(Paragraph("CAPÍTULO II: ASISTENCIA", st['h1']))
    elems.append(Paragraph(
        "Art. 4. La asistencia a clases es obligatoria. El estudiante que acumule más del 20% de "
        "inasistencias injustificadas en una asignatura perderá el derecho a presentar el examen final "
        "y reprobará automáticamente la materia con nota 0.0.", st['body']))
    elems.append(Paragraph(
        "Art. 5. Las inasistencias justificadas deben ser reportadas dentro de los 3 días hábiles "
        "siguientes ante la Secretaría Académica, adjuntando el soporte correspondiente (incapacidad "
        "médica, citación judicial, duelo familiar de primer grado).", st['body']))

    datos = [
        ["Inasistencias acumuladas", "Estado del estudiante", "Acción recomendada"],
        ["1–5% (1–2 clases)", "Sin riesgo", "Seguimiento normal"],
        ["6–10% (3–5 clases)", "Riesgo Bajo", "Notificación al estudiante"],
        ["11–15% (6–8 clases)", "Riesgo Medio", "Cita obligatoria con tutor académico"],
        ["16–20% (9–11 clases)", "Riesgo Alto", "Intervención inmediata y notificación a coordinación"],
        [">20% (>11 clases)", "Pérdida de derecho", "Reprobación automática — sin examen final"],
    ]
    t = Table(datos, colWidths=[5.5*cm, 4*cm, 7*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), AZUL), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [FONDO, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#cccccc')),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    elems.append(t); sp(elems)

    elems.append(Paragraph("CAPÍTULO III: REPITENCIA Y CANCELACIONES", st['h1']))
    elems.append(Paragraph(
        "Art. 6. Un estudiante puede cancelar una asignatura antes de la semana 8 sin que afecte "
        "su historial académico. Después de la semana 8, la cancelación implica una nota de 0.0 "
        "en el sistema a efectos estadísticos. Solo se permite cancelar máximo 2 asignaturas por "
        "semestre y 6 en toda la carrera.", st['body']))
    elems.append(Paragraph(
        "Art. 7. La repitencia de una asignatura está permitida hasta 3 veces. A la cuarta pérdida, "
        "el estudiante debe solicitar ante el Consejo Académico una valoración especial. "
        "Si la solicitud es negada, deberá cambiar de programa académico.", st['body']))
    elems.append(Paragraph(
        "Art. 8. Promedio Académico Acumulado (PAA): un PAA inferior a 5.5 activa el estado de "
        "'Alerta Académica'. Si el PAA cae por debajo de 4.5 en dos semestres consecutivos, "
        "el estudiante puede ser suspendido académicamente por un semestre.", st['body']))

    elems.append(Paragraph("CAPÍTULO IV: BECAS Y BENEFICIOS ACADÉMICOS", st['h1']))
    for item in [
        "Beca de Excelencia Académica: PAA ≥ 9.0, sin materias reprobadas. Descuento del 50% en matrícula.",
        "Beca Socioeconómica: Estudio de caso por Bienestar Universitario. Requiere renovación semestral.",
        "Monitor Académico: PAA ≥ 8.0. El monitor recibe auxilio económico y certificado de experiencia.",
        "Matrícula de Honor: Para el mejor promedio de cada programa. Matrícula gratuita el semestre siguiente.",
        "Descuento por hermanos: Si dos o más hermanos estudian simultáneamente, descuento del 15% a cada uno.",
    ]:
        elems.append(Paragraph(f"• {item}", st['bullet']))


# ═══════════════════════════════════════════════════════════════════
# DOCUMENTO 2: Protocolo de Intervención
# ═══════════════════════════════════════════════════════════════════
def gen_protocolo(elems, st):
    elems.append(Paragraph("PROTOCOLO DE INTERVENCIÓN TEMPRANA", st['titulo']))
    elems.append(Paragraph("Sistema de Alertas Estudiantiles (SAE) — Guía para Docentes y Coordinadores", st['subtitulo']))
    hr(elems); sp(elems)

    elems.append(Paragraph("1. OBJETIVO DEL SISTEMA SAE", st['h1']))
    elems.append(Paragraph(
        "El Sistema de Alertas Estudiantiles (SAE) de la UNT tiene como objetivo detectar "
        "oportunamente a los estudiantes con riesgo de deserción o bajo rendimiento para activar "
        "rutas de atención personalizadas antes de que la situación sea irreversible. "
        "El SAE integra análisis de datos académicos, seguimiento docente y atención psicosocial.",
        st['body']))

    elems.append(Paragraph("2. CLASIFICACIÓN DE NIVELES DE RIESGO", st['h1']))
    datos = [
        ["Nivel", "Criterios", "Tiempo de respuesta", "Responsable"],
        ["BAJO\n(Verde)", "Promedio 6.5–7.4\nAsistencia 80–89%\nSin repitencias", "15 días hábiles", "Docente titular"],
        ["MEDIO\n(Amarillo)", "Promedio 5.0–6.4\nAsistencia 70–79%\n1 repitencia activa", "5 días hábiles", "Coordinador académico"],
        ["ALTO\n(Rojo)", "Promedio < 5.0\nAsistencia < 70%\n2+ repitencias", "48 horas", "Coordinador + Bienestar"],
    ]
    t = Table(datos, colWidths=[3*cm, 6.5*cm, 3.5*cm, 3.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), AZUL), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#e8f5e9'), colors.HexColor('#fff3e0'),
                                               colors.HexColor('#ffebee')]),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elems.append(t); sp(elems)

    elems.append(Paragraph("3. RUTA DE ATENCIÓN — RIESGO ALTO", st['h1']))
    pasos = [
        ("Paso 1 — Detección (Día 1)", "El SAE identifica al estudiante automáticamente. Se genera alerta en el sistema y se notifica por Telegram al estudiante y por email al docente titular."),
        ("Paso 2 — Primer contacto (Día 1–2)", "El docente o coordinador realiza un primer contacto (llamada, email o mensaje) para confirmar que el estudiante recibió la alerta y acordar una cita."),
        ("Paso 3 — Diagnóstico (Día 3–5)", "Cita presencial de 30 minutos. Se aplicia encuesta de diagnóstico socioeconómico y académico. Se identifica la causa raíz del bajo rendimiento: económica, familiar, de salud o académica pura."),
        ("Paso 4 — Plan de mejoramiento (Día 5–7)", "Se diseña un plan personalizado con metas semanales, horario de tutorías y compromisos formalizados. El estudiante firma el acuerdo de compromiso académico."),
        ("Paso 5 — Seguimiento (Semanas 2–4)", "Revisión semanal por el tutor asignado. Si el promedio sube ≥ 0.5 puntos o la asistencia mejora ≥ 10%, la alerta se clasifica como 'Atendida'. Si no mejora, se escala a Bienestar."),
        ("Paso 6 — Cierre o escalada (Semana 5+)", "Si el indicador mejora sostenidamente por 3 semanas, se cierra la alerta. Si persiste, se abre proceso psicosocial con el área de bienestar universitario."),
    ]
    for titulo, desc in pasos:
        elems.append(Paragraph(titulo, st['h2']))
        elems.append(Paragraph(desc, st['body']))

    elems.append(Paragraph("4. ACCIONES ESPECÍFICAS POR CAUSA DE RIESGO", st['h1']))

    causas = [
        ("Bajo rendimiento en Matemáticas / Cálculo", [
            "Derivar a tutorías del Departamento de Ciencias Básicas (martes y jueves, 14:00–17:00, Bloque C, aula 301).",
            "Recomendar plataforma Khan Academy para refuerzo en álgebra y límites.",
            "Asignar monitor académico del semestre superior de la misma carrera.",
            "Si nota < 4.0, evaluar la posibilidad de cancelación antes de la semana 8.",
        ]),
        ("Bajo rendimiento en Programación", [
            "Hackathons de práctica internos (viernes 16:00, Laboratorio de Sistemas, Bloque A).",
            "Grupo de apoyo 'Code Clinic' — estudiantes pares de semestres superiores.",
            "Recursos: freeCodeCamp, Codecademy, LeetCode (nivel facil).",
            "Revisar si el estudiante cuenta con computador en casa — si no, gestionar préstamo del laboratorio.",
        ]),
        ("Inasistencias recurrentes", [
            "Indagar la causa real: trabajo, transporte, salud, desmotivación.",
            "Si trabaja: ajustar horario con Coordinación de Horarios (solicitud antes del semana 4).",
            "Si hay problema de salud: derivar a Servicio Médico Universitario (clínica, 1er piso bloque principal).",
            "Si es desmotivación: sesión con Orientación Vocacional.",
        ]),
        ("Problemas económicos", [
            "Contactar Bienestar Universitario para estudio socioeconómico urgente (correo: bienestar@unt.edu.co).",
            "Informar sobre la Beca de Emergencia Económica (aplica en cualquier momento del semestre).",
            "Verificar si el estudiante conoce el subsidio de alimentación (comedor universitario, costo diferencial).",
            "Orientar sobre trabajos de monitoria y empleos de medio tiempo compatibles con el horario.",
        ]),
    ]
    for causa, acciones in causas:
        elems.append(Paragraph(causa, st['h3']))
        for a in acciones:
            elems.append(Paragraph(f"→ {a}", st['bullet']))
        sp(elems, 0.2)

    elems.append(Paragraph("5. INDICADORES DE ÉXITO DE LA INTERVENCIÓN", st['h1']))
    for item in [
        "Mejora de promedio ≥ 0.5 puntos en el siguiente parcial.",
        "Reducción de inasistencias al menos un 50% respecto al período de alerta.",
        "Participación activa del estudiante en las tutorías asignadas (asistencia ≥ 80%).",
        "El estudiante manifiesta sentirse apoyado y con claridad sobre su plan (encuesta de satisfacción ≥ 7/10).",
        "No repetición de la asignatura en el siguiente semestre.",
    ]:
        elems.append(Paragraph(f"✓ {item}", st['bullet']))


# ═══════════════════════════════════════════════════════════════════
# DOCUMENTO 3: Guía de Técnicas de Estudio
# ═══════════════════════════════════════════════════════════════════
def gen_tecnicas(elems, st):
    elems.append(Paragraph("GUÍA DE TÉCNICAS DE APRENDIZAJE EFECTIVO", st['titulo']))
    elems.append(Paragraph("Oficina de Desarrollo Estudiantil — Universidad Nacional Tecnológica", st['subtitulo']))
    hr(elems); sp(elems)

    elems.append(Paragraph("INTRODUCCIÓN", st['h1']))
    elems.append(Paragraph(
        "Esta guía recoge las técnicas de estudio con mayor evidencia científica para la retención "
        "y comprensión del conocimiento universitario. Están diseñadas para estudiantes de ingeniería "
        "y ciencias exactas, pero son aplicables a cualquier área. El uso sistemático de estas "
        "técnicas puede mejorar el rendimiento académico entre un 30% y un 60% según estudios de "
        "la Universidad de Waterloo (2019) y el MIT Learning Lab (2021).", st['body']))

    elems.append(Paragraph("1. TÉCNICA POMODORO (Gestión del tiempo)", st['h1']))
    elems.append(Paragraph(
        "Desarrollada por Francesco Cirillo, es la técnica más efectiva para combatir la procrastinación "
        "y mantener la concentración durante el estudio universitario.", st['body']))
    pasos = [
        ("Bloque de trabajo", "25 minutos de estudio sin interrupciones. Teléfono en modo avión. Notificaciones del PC desactivadas."),
        ("Descanso corto", "5 minutos de pausa activa: estiramiento, agua, respiración. NUNCA redes sociales en este descanso."),
        ("Ciclo completo", "Cada 4 pomodoros (2 horas de trabajo efectivo), descanso largo de 20–30 minutos."),
        ("Registro", "Anota cuántos pomodoros completaste por tema. Te ayuda a estimar tiempos futuros."),
    ]
    for nombre, desc in pasos:
        elems.append(Paragraph(f"<b>{nombre}:</b> {desc}", st['bullet']))
    elems.append(Paragraph(
        "Nota: Para materias como Cálculo o Programación, se recomienda sesiones de 50 minutos "
        "(2 pomodoros continuos) pues el tiempo de 'calentamiento cognitivo' es mayor.", st['nota']))
    sp(elems)

    elems.append(Paragraph("2. REPETICIÓN ESPACIADA (Spaced Repetition)", st['h1']))
    elems.append(Paragraph(
        "Basada en la curva del olvido de Ebbinghaus. Consiste en repasar el material "
        "en intervalos crecientes para fijar la información en la memoria a largo plazo. "
        "Es 3 veces más eficiente que el estudio masivo (estudiar todo el día antes del examen).",
        st['body']))
    datos = [
        ["Sesión", "Cuándo estudiar", "Duración sugerida"],
        ["1ª sesión", "El mismo día de la clase", "20–30 min"],
        ["2ª sesión", "Al día siguiente", "15 min"],
        ["3ª sesión", "3 días después", "10 min"],
        ["4ª sesión", "1 semana después", "10 min"],
        ["5ª sesión", "2 semanas después", "5 min (ya está fijado)"],
    ]
    t = Table(datos, colWidths=[3.5*cm, 7*cm, 5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), AZUL_CLARO), ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 8.5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [FONDO, colors.white]),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#cccccc')),
        ('PADDING', (0, 0), (-1, -1), 5), ('ALIGN', (2, 0), (2, -1), 'CENTER'),
    ]))
    elems.append(t); sp(elems)

    elems.append(Paragraph("3. MÉTODO CORNELL (Toma de notas)", st['h1']))
    elems.append(Paragraph(
        "Desarrollado en la Universidad de Cornell. Divide la hoja en tres secciones: "
        "columna izquierda para palabras clave y preguntas, columna derecha para las notas de clase, "
        "y una sección inferior para el resumen. Se ha demostrado que los estudiantes que usan "
        "Cornell retienen el 78% del material vs. el 34% con notas lineales tradicionales.", st['body']))

    elems.append(Paragraph("4. MAPAS MENTALES (Organización visual)", st['h1']))
    for item in [
        "Coloca el concepto central en el medio y ramifica subcategorías con colores diferentes.",
        "Usa imágenes y símbolos — el cerebro recuerda 6x más las imágenes que el texto plano.",
        "Herramientas gratuitas: MindMeister (online), XMind (descargable), draw.io.",
        "Ideal para repasar antes del examen: reconstruir el mapa de memoria es la mejor autoevaluación.",
        "Para Programación: usa diagramas de flujo como mapas conceptuales del código.",
    ]:
        elems.append(Paragraph(f"• {item}", st['bullet']))
    sp(elems)

    elems.append(Paragraph("5. APRENDIZAJE ACTIVO (Active Recall)", st['h1']))
    elems.append(Paragraph(
        "En lugar de releer los apuntes (re-reading), cierrra el libro y escribe todo lo que recuerdas "
        "sobre el tema. Este proceso de 'recuperación activa' fortalece los caminos neuronales mucho "
        "más que la relectura pasiva. Combínalo con flashcards digitales (Anki — gratuito).", st['body']))

    elems.append(Paragraph("6. PLANIFICACIÓN SEMANAL DEL ESTUDIO", st['h1']))
    elems.append(Paragraph(
        "Recomendación UNT: por cada hora de clase, dedica 2 horas de estudio independiente. "
        "Un estudiante de tiempo completo (18 créditos) debería estudiar mínimo 36 horas "
        "adicionales por semana fuera del aula.", st['body']))
    for item in [
        "Domingo por la noche: planea las materias que estudiarás cada día de la semana siguiente.",
        "Distribuye las materias difíciles en la mañana (pico cognitivo para la mayoría de personas).",
        "Nunca estudies la misma materia más de 2 horas seguidas — el aprendizaje intercalado es más eficiente.",
        "Reserva los viernes por la tarde para repasar toda la semana (primera sesión de spaced repetition).",
        "Usa una agenda física o Google Calendar — los compromisos escritos se cumplen 42% más.",
    ]:
        elems.append(Paragraph(f"• {item}", st['bullet']))

    elems.append(Paragraph("7. MANEJO DEL ESTRÉS ACADÉMICO", st['h1']))
    elems.append(Paragraph(
        "El estrés crónico reduce la capacidad de memoria de trabajo hasta en un 40%. "
        "Estrategias validadas clínicamente:", st['body']))
    for item in [
        "Dormir mínimo 7 horas — el sueño consolida la memoria declarativa (fórmulas, fechas, conceptos).",
        "Ejercicio 30 min/día — aumenta el BDNF, proteína que mejora la plasticidad neuronal y el aprendizaje.",
        "Meditación de 10 min al despertar (app Headspace o Calm, versión gratuita) — reduce cortisol un 23%.",
        "Técnica 5-4-3-2-1 para ataques de ansiedad antes de exámenes: nombra 5 cosas que ves, 4 que tocas, etc.",
        "Si el estrés es persistente más de 2 semanas, busca apoyo en Psicología Universitaria (gratuito).",
    ]:
        elems.append(Paragraph(f"• {item}", st['bullet']))


# ═══════════════════════════════════════════════════════════════════
# DOCUMENTO 4: Directorio de Recursos
# ═══════════════════════════════════════════════════════════════════
def gen_recursos(elems, st):
    elems.append(Paragraph("DIRECTORIO DE RECURSOS Y SERVICIOS DE APOYO ESTUDIANTIL", st['titulo']))
    elems.append(Paragraph("Universidad Nacional Tecnológica — Actualización Semestre 2024-2", st['subtitulo']))
    hr(elems); sp(elems)

    elems.append(Paragraph(
        "La UNT pone a disposición de sus estudiantes un amplio portafolio de servicios de apoyo. "
        "Todos los servicios listados en este documento son GRATUITOS para estudiantes matriculados "
        "activos. Solo debes presentar tu carnet universitario vigente.", st['body']))

    servicios = [
        ("BIENESTAR UNIVERSITARIO", [
            ("Ubicación", "Bloque A, Piso 1, Oficina 105"),
            ("Horario", "Lunes a viernes 7:00 a.m. – 7:00 p.m. / Sábados 8:00 – 12:00"),
            ("Correo", "bienestar@unt.edu.co"),
            ("Teléfono", "601-555-0101 ext. 1050"),
            ("Servicios", "Estudios socioeconómicos, gestión de becas, auxilios de emergencia, fondo de alimentación"),
            ("Trámite beca emergencia", "Formulario en línea en portal.unt.edu.co → Bienestar → Solicitudes. Respuesta en 5 días hábiles."),
        ]),
        ("PSICOLOGÍA Y SALUD MENTAL", [
            ("Ubicación", "Bloque D, Piso 2, Consultorios 201–205"),
            ("Horario", "Lunes a viernes 8:00 a.m. – 6:00 p.m."),
            ("Correo", "psicologia@unt.edu.co"),
            ("Citas", "WhatsApp: 310-555-0202 o en el portal universitario"),
            ("Servicios", "5 sesiones individuales gratuitas por semestre, talleres de manejo del estrés, grupos de apoyo"),
            ("Urgencias", "Si sientes que estás en crisis, puedes ir directamente sin cita previa en horario de atención."),
        ]),
        ("TUTORÍAS ACADÉMICAS — CIENCIAS BÁSICAS", [
            ("Ubicación", "Bloque C, Aula 301 (Matemáticas) / Aula 302 (Física) / Lab 108 (Química)"),
            ("Horario", "Martes y jueves 14:00–17:00 / Sábados 9:00–12:00"),
            ("Materias cubiertas", "Cálculo I, II y III, Álgebra Lineal, Física I y II, Química General, Estadística"),
            ("Modalidad", "Presencial y virtual (Google Meet — enlace en el portal)"),
            ("Costo", "Completamente gratuito para estudiantes de la UNT"),
            ("Monitores", "Estudiantes de semestres 6+ con promedio ≥ 8.5, seleccionados por el departamento."),
        ]),
        ("TUTORÍAS — INGENIERÍA Y SISTEMAS", [
            ("Ubicación", "Laboratorio de Sistemas, Bloque A, Piso 2"),
            ("Horario", "Lunes, miércoles y viernes 15:00–18:00"),
            ("Materias", "Programación I y II, Estructuras de Datos, Bases de Datos, Redes, Algoritmos"),
            ("Grupos Code Clinic", "Viernes 16:00 — sesión grupal abierta de resolución de problemas"),
            ("Recursos adicionales", "Acceso a licencias de software: Visual Studio, GitHub Pro, JetBrains educativo"),
        ]),
        ("BIBLIOTECA Y RECURSOS DIGITALES", [
            ("Horario", "Lunes a sábado 7:00 a.m. – 9:00 p.m."),
            ("Bases de datos", "Acceso gratuito a: IEEE Xplore, Springer, SciELO, EBSCO, Google Scholar institucional"),
            ("Software licenciado", "MATLAB, AutoCAD, SPSS, Microsoft Office 365 (descarga en cuenta institucional)"),
            ("Préstamo de equipos", "Portátiles disponibles por 4 horas en el mostrador principal (carnet como garantía)"),
            ("Salas de estudio", "12 salas grupales reservables por 2 horas en biblioteca.unt.edu.co"),
        ]),
        ("SERVICIO MÉDICO UNIVERSITARIO", [
            ("Ubicación", "Bloque Principal, Piso 1 (entrada lateral)"),
            ("Horario", "Lunes a viernes 7:00 a.m. – 5:00 p.m."),
            ("Correo", "salud@unt.edu.co"),
            ("Servicios", "Consulta médica general, enfermería, primeros auxilios, incapacidades"),
            ("Importante", "Si requieres incapacidad por enfermedad para justificar inasistencias, debe expedirse aquí o en EPS. La UNT acepta máximo 3 incapacidades por semestre."),
        ]),
        ("ORIENTACIÓN VOCACIONAL Y PROFESIONAL", [
            ("Ubicación", "Bloque B, Oficina 210"),
            ("Servicios", "Pruebas de orientación vocacional, asesoría de cambio de programa, perfil de competencias"),
            ("Ferias de empleo", "1 feria por semestre (ver calendario en portal). Más de 50 empresas asisten."),
            ("Prácticas profesionales", "Coordinación en el semestre 7+. Lista de empresas aliadas en el portal."),
            ("LinkedIn universitario", "Taller gratuito de optimización de perfil LinkedIn (primer viernes de cada mes)."),
        ]),
    ]

    for nombre, datos in servicios:
        elems.append(Paragraph(nombre, st['h1']))
        tabla_data = [[k, v] for k, v in datos]
        t = Table(tabla_data, colWidths=[4*cm, 12.5*cm])
        t.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5), ('LEADING', (0, 0), (-1, -1), 12),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [FONDO, colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#dddddd')),
            ('PADDING', (0, 0), (-1, -1), 5), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elems.append(t); sp(elems, 0.4)

    elems.append(Paragraph("RECURSOS DIGITALES RECOMENDADOS", st['h1']))
    recursos_digitales = [
        ("Matemáticas y Física", "Khan Academy (khanacademy.org) — cursos completos en español, gratuito."),
        ("Programación", "freeCodeCamp, Codecademy, The Odin Project — gratuitos con certificación."),
        ("Idiomas", "Duolingo (inglés), la UNT ofrece 4 niveles de inglés técnico gratuitos por semestre."),
        ("Productividad", "Notion (gestión de tareas), Anki (flashcards), Forest (bloqueador de distracciones)."),
        ("Bienestar mental", "Headspace (meditación), Smiling Mind (gratuito), canal YouTube: 'Pick Up Limes'."),
        ("Cursos MOOC", "Coursera (auditoría gratuita), edX, MIT OpenCourseWare — materiales universitarios de élite."),
    ]
    for area, rec in recursos_digitales:
        elems.append(Paragraph(f"<b>{area}:</b> {rec}", st['bullet']))


# ═══════════════════════════════════════════════════════════════════
# DOCUMENTO 5: Planes de Mejoramiento por Área
# ═══════════════════════════════════════════════════════════════════
def gen_planes(elems, st):
    elems.append(Paragraph("PLANES DE MEJORAMIENTO ACADÉMICO PERSONALIZADOS", st['titulo']))
    elems.append(Paragraph("Guía por Área de Conocimiento — Departamento Académico UNT 2024", st['subtitulo']))
    hr(elems); sp(elems)

    elems.append(Paragraph(
        "Este documento establece planes de mejoramiento específicos según el área de debilidad "
        "detectada por el SAE. Cada plan está diseñado para ser ejecutado en 4 semanas, "
        "con metas medibles y recursos concretos.", st['body']))

    planes = [
        ("PLAN A — CÁLCULO Y ÁLGEBRA", "Para estudiantes con promedio < 6.0 en materias de matemáticas", [
            ("Semana 1 — Diagnóstico", [
                "Hacer la prueba de nivel gratuita en khanacademy.org/math/calculus-1 para identificar brechas.",
                "Revisar los temas del último parcial con el docente titular (solicitar cita por email).",
                "Identificar los 3 temas más débiles y priorizarlos.",
                "Materiales: apuntes de clase + libro recomendado: 'Cálculo' de Stewart (biblioteca, código QM303ST).",
            ]),
            ("Semana 2 — Fundamentos", [
                "Dedicar 1 hora diaria a álgebra básica: factorización, funciones, trigonometría.",
                "Resolver mínimo 10 ejercicios diarios de práctica graduada (fácil → difícil).",
                "Asistir a tutoría de Ciencias Básicas (martes y jueves 14:00, Bloque C-301).",
                "Usar el método Cornell para notas — anotar las fórmulas clave con explicación propia.",
            ]),
            ("Semana 3 — Aplicación", [
                "Trabajar con exámenes anteriores de la materia (pedirlos al monitor académico).",
                "Simulacro de examen bajo condiciones reales: tiempo cronometrado, sin apuntes.",
                "Revisar errores del simulacro y clasificarlos: ¿error de concepto o de cálculo?",
                "Grupos de estudio de máximo 3 personas — enseñar el tema a otro es la mejor forma de aprenderlo.",
            ]),
            ("Semana 4 — Consolidación", [
                "Repaso completo con mapa mental de todos los temas del periodo.",
                "Segunda prueba simulacro — la meta es superar la nota del examen anterior en al menos 1.5 puntos.",
                "Evaluar si es necesario solicitar habilitación (solo si la nota actual está entre 4.0 y 5.9).",
                "Reportar avance al tutor del SAE para actualizar el estado de la alerta.",
            ]),
        ]),
        ("PLAN B — PROGRAMACIÓN Y ALGORITMIA", "Para estudiantes con promedio < 6.0 en materias de sistemas/informática", [
            ("Semana 1 — Ambiente y fundamentos", [
                "Instalar Python (gratuito) y practicar con ejercicios básicos en repl.it (sin instalación local).",
                "Completar los primeros 5 módulos de freeCodeCamp — JavaScript o Python según la materia.",
                "Asistir al grupo Code Clinic (viernes 16:00, Lab Sistemas, Bloque A).",
                "Meta de la semana: escribir 3 funciones que resuelvan problemas del cotidiano (calculadora, factorial, etc.).",
            ]),
            ("Semana 2 — Lógica y estructuras", [
                "Practicar con LeetCode nivel 'Easy' — mínimo 2 problemas diarios.",
                "Dibujar el diagrama de flujo ANTES de escribir el código — hábito fundamental.",
                "Revisar errores con el depurador (debugger) en lugar de agregar prints al código.",
                "Estudiar en pareja: programación en par (pair programming) acelera el aprendizaje un 60%.",
            ]),
            ("Semana 3 — Proyecto integrador", [
                "Desarrollar un mini-proyecto personal: lista de tareas, calculadora de notas, juego simple.",
                "Subir el proyecto a GitHub (cuenta gratuita) — esto también construye el portafolio profesional.",
                "Pedir retroalimentación al monitor o docente sobre el código escrito.",
                "Resolver los talleres del semestre que estén pendientes — cada taller entregado suma a la nota.",
            ]),
            ("Semana 4 — Preparación evaluación", [
                "Resolver exámenes pasados de la asignatura cronometrado.",
                "Memorizar los patrones más comunes: loops, condicionales, funciones recursivas, manejo de listas.",
                "Si la materia incluye bases de datos: practicar consultas SQL básicas en sqlzoo.net (gratuito).",
                "Solicitar al docente una revisión del avance antes del examen.",
            ]),
        ]),
        ("PLAN C — MEJORA DE ASISTENCIA", "Para estudiantes con asistencia < 75% en cualquier materia", [
            ("Diagnóstico de la causa", [
                "Identificar la causa real de las inasistencias: ¿laboral, salud, transporte, desmotivación?",
                "Si es laboral: solicitar ante Coordinación de Horarios un cambio de jornada (disponible hasta semana 6).",
                "Si es de salud: obtener certificado médico y presentarlo en Secretaría dentro de 3 días hábiles.",
                "Si es desmotivación: sesión de orientación vocacional (Bloque B, Oficina 210).",
            ]),
            ("Estrategia de recuperación", [
                "Hablar directamente con cada docente afectado — muchos aceptan compromisos directos.",
                "Calcular exactamente cuántas clases puedes faltar sin perder el derecho a examen (20% del total).",
                "Crear un sistema de alarmas y recordatorios para cada clase en Google Calendar.",
                "Buscar un compañero 'buddy' que te notifique si llegas tarde o no apareces.",
            ]),
            ("Hábitos de consistencia", [
                "Preparar la noche anterior todo lo necesario para el día siguiente (mochila, materiales, ropa).",
                "Dormir a una hora fija — la falta de sueño es la principal causa de no ir a clases.",
                "Registrar tu asistencia tú mismo en una hoja de seguimiento semanal.",
                "Premio semanal si asististe al 100% de las clases de esa semana (refuerzo positivo).",
            ]),
        ]),
        ("PLAN D — GESTIÓN DEL TIEMPO Y ORGANIZACIÓN", "Para estudiantes que no logran completar tareas y evaluaciones a tiempo", [
            ("Sistema de organización", [
                "Usar una sola agenda (física o digital) para TODAS las materias y compromisos personales.",
                "Al inicio de cada semana: listar todas las actividades y fechas de entrega pendientes.",
                "Clasificar tareas por urgencia/importancia (Matriz de Eisenhower).",
                "Nunca confiar en la memoria — todo se escribe inmediatamente al recibir el compromiso.",
            ]),
            ("Rutina diaria de estudio", [
                "Definir un horario fijo de estudio (mismo lugar, misma hora): el cerebro crea hábito en 21 días.",
                "Bloque matutino (6:00–8:00): materias más difíciles. El cerebro trabaja mejor en la mañana.",
                "Bloque vespertino (15:00–18:00): talleres, lecturas, revisión de notas.",
                "Bloque nocturno (20:00–21:00): repaso rápido y planificación del día siguiente.",
            ]),
            ("Herramientas digitales", [
                "Notion o Trello para gestión de proyectos académicos con fechas límite.",
                "Google Calendar con recordatorios 48h y 2h antes de cada entrega.",
                "Forest App (bloqueador de celular) durante sesiones de estudio.",
                "Pomodoro Timer en pomofocus.io — gratuito, sin instalación.",
            ]),
        ]),
    ]

    for nombre, desc, semanas in planes:
        elems.append(Paragraph(nombre, st['h1']))
        elems.append(Paragraph(desc, st['nota']))
        sp(elems, 0.2)
        for sem_nombre, acciones in semanas:
            elems.append(Paragraph(sem_nombre, st['h2']))
            for a in acciones:
                elems.append(Paragraph(f"• {a}", st['bullet']))
        sp(elems, 0.5)


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generando base de conocimiento institucional del SAE...")
    doc(os.path.join(OUT, "01_Reglamento_Academico_UNT.pdf"), "Reglamento", gen_reglamento)
    doc(os.path.join(OUT, "02_Protocolo_Intervencion_SAE.pdf"), "Protocolo", gen_protocolo)
    doc(os.path.join(OUT, "03_Guia_Tecnicas_Estudio.pdf"), "Técnicas", gen_tecnicas)
    doc(os.path.join(OUT, "04_Directorio_Recursos_Apoyo.pdf"), "Recursos", gen_recursos)
    doc(os.path.join(OUT, "05_Planes_Mejoramiento_Academico.pdf"), "Planes", gen_planes)
    print(f"\n5 documentos generados en: {OUT}")
    print("Ahora reinicia la app para que el RAG re-indexe la base de conocimiento.")
