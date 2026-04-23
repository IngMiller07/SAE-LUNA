import os
import sys
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import cm

def generar_reporte_riesgos(output_path=None):
    """Genera un reporte PDF profesional de riesgo académico."""
    # Ruta por defecto junto al ejecutable
    if output_path is None:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        fecha = datetime.now().strftime("%Y%m%d_%H%M")
        output_path = os.path.join(base, f"reporte_cohorte_{fecha}.pdf")

    # Importar aquí para no circular
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from database import get_session
    from models import Estudiante, Alerta, Seguimiento

    session = get_session()
    try:
        estudiantes = session.query(Estudiante).order_by(Estudiante.nivel_riesgo).all()
        alertas_activas = session.query(Alerta).filter_by(estado='Activa').all()
        seguimientos = session.query(Seguimiento).all()

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            leftMargin=2*cm, rightMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm
        )

        styles = getSampleStyleSheet()
        elements = []

        # Encabezado
        title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=18, textColor=colors.HexColor('#1a237e'), spaceAfter=6)
        subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#546e7a'), spaceAfter=20)
        heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor('#1a237e'), spaceBefore=16, spaceAfter=8)
        normal_style = ParagraphStyle('Normal2', parent=styles['Normal'], fontSize=9)

        elements.append(Paragraph("Sistema de Alertas Estudiantiles - SAE", title_style))
        elements.append(Paragraph(f"Reporte de Riesgo Académico por Cohorte | Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a237e')))
        elements.append(Spacer(1, 0.4*cm))

        # Estadísticas generales
        total = len(estudiantes)
        riesgo_alto = sum(1 for e in estudiantes if e.nivel_riesgo == 'Alto')
        riesgo_medio = sum(1 for e in estudiantes if e.nivel_riesgo == 'Medio')
        riesgo_bajo = sum(1 for e in estudiantes if e.nivel_riesgo == 'Bajo')

        elements.append(Paragraph("Resumen Ejecutivo", heading_style))

        stats_data = [
            ["Indicador", "Valor"],
            ["Total de Estudiantes", str(total)],
            ["En Riesgo Alto", str(riesgo_alto)],
            ["En Riesgo Medio", str(riesgo_medio)],
            ["En Riesgo Bajo", str(riesgo_bajo)],
            ["Alertas Activas", str(len(alertas_activas))],
            ["Intervenciones Registradas", str(len(seguimientos))],
        ]

        stats_table = Table(stats_data, colWidths=[10*cm, 6*cm])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f5f5f5'), colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(stats_table)
        elements.append(Spacer(1, 0.5*cm))

        # Tabla de estudiantes en RIESGO ALTO
        elements.append(Paragraph("Estudiantes en Riesgo Alto", heading_style))
        alto_data = [["Nombre", "Carrera", "Semestre", "Promedio", "Asistencia"]]
        for e in estudiantes:
            if e.nivel_riesgo == 'Alto':
                alto_data.append([e.nombre, e.carrera[:22], str(e.semestre), f"{e.promedio:.1f}", f"{e.asistencia:.0f}%"])

        if len(alto_data) > 1:
            alto_table = Table(alto_data, colWidths=[5*cm, 5.5*cm, 2.2*cm, 2.5*cm, 2.5*cm])
            alto_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#c62828')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffebee'), colors.white]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
                ('PADDING', (0, 0), (-1, -1), 5),
            ]))
            elements.append(alto_table)
        else:
            elements.append(Paragraph("No hay estudiantes en riesgo alto registrados.", normal_style))

        elements.append(Spacer(1, 0.4*cm))

        # Tabla de estudiantes en RIESGO MEDIO
        elements.append(Paragraph("Estudiantes en Riesgo Medio", heading_style))
        medio_data = [["Nombre", "Carrera", "Semestre", "Promedio", "Asistencia"]]
        for e in estudiantes:
            if e.nivel_riesgo == 'Medio':
                medio_data.append([e.nombre, e.carrera[:22], str(e.semestre), f"{e.promedio:.1f}", f"{e.asistencia:.0f}%"])

        if len(medio_data) > 1:
            medio_table = Table(medio_data, colWidths=[5*cm, 5.5*cm, 2.2*cm, 2.5*cm, 2.5*cm])
            medio_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e65100')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#fff3e0'), colors.white]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
                ('PADDING', (0, 0), (-1, -1), 5),
            ]))
            elements.append(medio_table)

        elements.append(Spacer(1, 0.4*cm))

        # Registro de intervenciones
        elements.append(Paragraph("Historial de Intervenciones", heading_style))
        if seguimientos:
            seg_data = [["Alerta ID", "Docente", "Acción", "Fecha"]]
            for s in seguimientos[:20]:  # máx 20
                seg_data.append([
                    f"#{s.alerta_id}",
                    s.docente[:20],
                    s.accion[:35],
                    s.fecha.strftime("%d/%m/%Y")
                ])
            seg_table = Table(seg_data, colWidths=[2*cm, 4*cm, 9*cm, 2.5*cm])
            seg_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 7.5),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#e8eaf6'), colors.white]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
                ('PADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(seg_table)
        else:
            elements.append(Paragraph("No hay intervenciones registradas aún.", normal_style))

        elements.append(Spacer(1, 1*cm))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
        elements.append(Paragraph("Generado automáticamente por el Sistema SAE | Documento Confidencial", subtitle_style))

        doc.build(elements)
        return True, output_path

    except Exception as e:
        return False, str(e)
    finally:
        session.close()
