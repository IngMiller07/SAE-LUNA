import os
import sys
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import cm

# Imports para graficos
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie

def generar_reporte_riesgos(output_path=None):
    """Genera un reporte PDF profesional de riesgo académico."""
    if output_path is None:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        fecha = datetime.now().strftime("%Y%m%d_%H%M")
        output_path = os.path.join(base, f"reporte_cohorte_{fecha}.pdf")

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from database import get_session
    from models import Estudiante, Alerta, Seguimiento

    session = get_session()
    try:
        estudiantes = session.query(Estudiante).order_by(Estudiante.nivel_riesgo).all()
        alertas = session.query(Alerta).order_by(Alerta.fecha.desc()).all()
        alertas_pendientes = [a for a in alertas if a.estado in ('Activa', 'Escalada')]
        alertas_atendidas = [a for a in alertas if a.estado == 'Atendida']
        seguimientos = session.query(Seguimiento).all()

        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            leftMargin=1.5*cm, rightMargin=1.5*cm,
            topMargin=1.5*cm, bottomMargin=1.5*cm
        )

        styles = getSampleStyleSheet()
        elements = []

        title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=18, textColor=colors.HexColor('#1a237e'), spaceAfter=6)
        subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#546e7a'), spaceAfter=20)
        heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor('#1a237e'), spaceBefore=16, spaceAfter=8)
        normal_style = ParagraphStyle('Normal2', parent=styles['Normal'], fontSize=9)

        elements.append(Paragraph("Sistema de Alertas Estudiantiles - SAE", title_style))
        elements.append(Paragraph(f"Reporte Gerencial Consolidado | Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a237e')))
        elements.append(Spacer(1, 0.4*cm))

        total = len(estudiantes)
        riesgo_alto = sum(1 for e in estudiantes if e.nivel_riesgo == 'Alto')
        riesgo_medio = sum(1 for e in estudiantes if e.nivel_riesgo == 'Medio')
        riesgo_bajo = sum(1 for e in estudiantes if e.nivel_riesgo == 'Bajo')

        elements.append(Paragraph("Resumen Ejecutivo y Gráfico de Cohorte", heading_style))

        # Tabla del resumen
        stats_data = [
            ["Métricas del Sistema", "Valor"],
            ["Total de Estudiantes Inscritos", str(total)],
            ["Proporción Riesgo Alto", f"{riesgo_alto} ({(riesgo_alto/total*100) if total else 0:.1f}%)"],
            ["Proporción Riesgo Medio", f"{riesgo_medio} ({(riesgo_medio/total*100) if total else 0:.1f}%)"],
            ["Proporción Riesgo Bajo", f"{riesgo_bajo} ({(riesgo_bajo/total*100) if total else 0:.1f}%)"],
            ["Alertas Activas/Escaladas (YOLO)", str(len(alertas_pendientes))],
            ["Alertas Exitosamente Atendidas", str(len(alertas_atendidas))]
        ]

        stats_table = Table(stats_data, colWidths=[10*cm, 3.5*cm])
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
        
        # Generar Gráfico de Torta
        if total > 0:
            d = Drawing(10*cm, 5*cm)
            pc = Pie()
            pc.x = 2.5*cm
            pc.y = 0.5*cm
            pc.width = 4*cm
            pc.height = 4*cm
            
            # Quitar porcentajes si están vacíos
            filtered_data = []
            filtered_labels = []
            filtered_colors = []
            c_alto = colors.HexColor('#c62828')
            c_medio = colors.HexColor('#e65100')
            c_bajo = colors.HexColor('#2e7d32')
            
            if riesgo_alto > 0:
                filtered_data.append(riesgo_alto)
                filtered_labels.append('Alto')
                filtered_colors.append(c_alto)
            if riesgo_medio > 0:
                filtered_data.append(riesgo_medio)
                filtered_labels.append('Medio')
                filtered_colors.append(c_medio)
            if riesgo_bajo > 0:
                filtered_data.append(riesgo_bajo)
                filtered_labels.append('Bajo')
                filtered_colors.append(c_bajo)
                
            pc.data = filtered_data
            pc.labels = filtered_labels
            pc.slices.strokeWidth = 0.5
            for i, c in enumerate(filtered_colors):
                pc.slices[i].fillColor = c
                
            d.add(pc)
            
            # Agrupar tabla y gráfico en una tabla layout invisible
            layout_data = [[stats_table, d]]
            layout_table = Table(layout_data, colWidths=[14*cm, 4*cm])
            layout_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
            elements.append(layout_table)
        else:
            elements.append(stats_table)

        elements.append(Spacer(1, 0.5*cm))

        # Tabla RIESGO ALTO (Y MATERIA CRITICA)
        elements.append(Paragraph("Tutoría Prioritaria: Estudiantes en Riesgo Alto", heading_style))
        alto_data = [["Nombre", "Semestre", "Detección Temprana (Materia Débil)", "Prom", "Asistencia"]]
        for e in estudiantes:
            if e.nivel_riesgo == 'Alto':
                mat_debil = e.materia_mas_debil()
                str_debil = f"{mat_debil.materia} ({mat_debil.nota:.1f})" if mat_debil else "N/A"
                str_nom = e.nombre[:22] + "..." if len(e.nombre)>22 else e.nombre
                
                alto_data.append([str_nom, str(e.semestre), str_debil, f"{e.promedio:.1f}", f"{e.asistencia:.0f}%"])

        if len(alto_data) > 1:
            alto_table = Table(alto_data, colWidths=[4.7*cm, 1.8*cm, 7*cm, 1.5*cm, 3*cm])
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

        # REGISTRO DE ALERTAS SAE (YOLO)
        elements.append(Paragraph("Registro Dinámico SAE - Alarmas YOLO Activas", heading_style))
        if alertas_pendientes:
            alertas_data = [["Estado", "Prioridad", "Estudiante", "Motivo Capturado (Módulo Visión / RAG)", "Fecha"]]
            for a in alertas_pendientes:
                est_n = a.estudiante.nombre[:15] + "..." if a.estudiante and len(a.estudiante.nombre)>15 else (a.estudiante.nombre if a.estudiante else "N/A")
                alertas_data.append([
                    a.estado,
                    a.prioridad,
                    est_n,
                    a.descripcion[:45] + "..." if len(a.descripcion)>45 else a.descripcion,
                    a.fecha.strftime("%d/%m/%y %H:%M") if a.fecha else "-"
                ])
                
            al_table = Table(alertas_data, colWidths=[2.2*cm, 2.2*cm, 3.5*cm, 7.6*cm, 2.5*cm])
            al_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4527a0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ede7f6'), colors.white]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ce93d8')),
                ('PADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(al_table)
        else:
            elements.append(Paragraph("Excelente: No existen alertas pendientes en el sistema YOLO.", normal_style))
            
        elements.append(Spacer(1, 0.4*cm))
        
        # ANEXO DE GESTION 
        elements.append(Paragraph("Anexo de Gestión Académica: Historial Atendido", heading_style))
        if alertas_atendidas:
            at_data = [["Estudiante Evaluado", "Motivo Original de Alerta", "Fecha de Emisión"]]
            for a in alertas_atendidas:
                est_n = a.estudiante.nombre[:25] if a.estudiante else "N/A"
                at_data.append([
                    est_n,
                    a.descripcion[:65] + "..." if len(a.descripcion)>65 else a.descripcion,
                    a.fecha.strftime("%d/%m/%y %H:%M") if a.fecha else "-"
                ])
                
            att_table = Table(at_data, colWidths=[4.5*cm, 10.5*cm, 3*cm])
            att_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#e8f5e9'), colors.white]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#a5d6a7')),
                ('PADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(att_table)
        else:
            elements.append(Paragraph("El archivo de alertas atendidas está vacío.", normal_style))

        elements.append(Spacer(1, 1*cm))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
        elements.append(Paragraph("Generado exclusivamente por el motor RAG & YOLO del SAE | Uso Estrictamente Confidencial", subtitle_style))

        doc.build(elements)
        return True, output_path

    except Exception as e:
        return False, str(e)
    finally:
        session.close()
