import os
import sys
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.units import cm

from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie

def generar_reporte_riesgos(output_path=None):
    """Genera un reporte PDF fiel a las especificaciones originales con alta calidad visual."""
    if output_path is None:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        fecha = datetime.now().strftime("%Y%m%d_%H%M")
        output_path = os.path.join(base, f"reporte_corte_{fecha}.pdf")

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from database import get_session
    from models import Estudiante, Alerta, Seguimiento

    session = get_session()
    try:
        estudiantes = session.query(Estudiante).order_by(Estudiante.nivel_riesgo).all()
        alertas = session.query(Alerta).order_by(Alerta.fecha.desc()).all()
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
        elements.append(Paragraph(f"Reporte de Riesgo Académico por Corte | Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#1a237e')))
        elements.append(Spacer(1, 0.4*cm))

        total = len(estudiantes)
        riesgo_alto = sum(1 for e in estudiantes if e.nivel_riesgo == 'Alto')
        riesgo_medio = sum(1 for e in estudiantes if e.nivel_riesgo == 'Medio')
        riesgo_bajo = sum(1 for e in estudiantes if e.nivel_riesgo == 'Bajo')

        # ----------------------------------------------------
        # 1. ESTADÍSTICAS POR CORTE ACADÉMICO (Y GRÁFICO MEJORADO)
        # ----------------------------------------------------
        elements.append(Paragraph("1. Estadísticas de Riesgo Académico por Corte", heading_style))

        stats_data = [
            ["Clasificación", "Estudiantes", "Porcentaje"],
            ["Riesgo Alto", str(riesgo_alto), f"{(riesgo_alto/total*100) if total else 0:.1f}%"],
            ["Riesgo Medio", str(riesgo_medio), f"{(riesgo_medio/total*100) if total else 0:.1f}%"],
            ["Riesgo Bajo", str(riesgo_bajo), f"{(riesgo_bajo/total*100) if total else 0:.1f}%"],
            ["Total del Corte", str(total), "100.0%"]
        ]

        stats_table = Table(stats_data, colWidths=[6*cm, 3*cm, 3*cm])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f5f5f5'), colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        
        # Gráfico corregido (más espacio para que no se corte)
        if total > 0:
            d = Drawing(6*cm, 5*cm) # Espacio amplio
            pc = Pie()
            pc.x = 2*cm
            pc.y = 1*cm
            pc.width = 3.5*cm
            pc.height = 3.5*cm
            
            filtered_data, filtered_labels, filtered_colors = [], [], []
            if riesgo_alto > 0:
                filtered_data.append(riesgo_alto)
                filtered_labels.append('Alto')
                filtered_colors.append(colors.HexColor('#c62828'))
            if riesgo_medio > 0:
                filtered_data.append(riesgo_medio)
                filtered_labels.append('Medio')
                filtered_colors.append(colors.HexColor('#e65100'))
            if riesgo_bajo > 0:
                filtered_data.append(riesgo_bajo)
                filtered_labels.append('Bajo')
                filtered_colors.append(colors.HexColor('#2e7d32'))
                
            pc.data = filtered_data
            pc.labels = filtered_labels
            pc.slices.strokeWidth = 0.5
            for i, c in enumerate(filtered_colors):
                pc.slices[i].fillColor = c
            d.add(pc)
            
            layout_table = Table([[stats_table, d]], colWidths=[12.5*cm, 5.5*cm])
            layout_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE')]))
            elements.append(layout_table)
        else:
            elements.append(stats_table)

        elements.append(Spacer(1, 0.4*cm))

        # ----------------------------------------------------
        # 2. CLASIFICACIÓN DE ALERTAS (YOLO)
        # ----------------------------------------------------
        elements.append(Paragraph("2. Clasificación de Alertas del Sistema", heading_style))
        if alertas:
            alertas_data = [["Est.", "Prior.", "Alerta/Tópico", "Estudiante Involucrado", "Programa Académico"]]
            for a in alertas[:25]: # Límite de 25 paras no romper tablas de memoria
                est_n = a.estudiante.nombre[:20] + "..." if a.estudiante and len(a.estudiante.nombre)>20 else (a.estudiante.nombre if a.estudiante else "N/A")
                prog = a.estudiante.carrera[:20] + "..." if a.estudiante and len(a.estudiante.carrera)>20 else (a.estudiante.carrera if a.estudiante else "N/A")
                
                alertas_data.append([
                    a.estado[:4], # Acortar para caber ("Acti", "Esca")
                    a.prioridad[:4], # Acortar ("Alta", "Medi")
                    a.tipo.replace('_', ' ').title()[:20],
                    est_n,
                    prog
                ])
                
            al_table = Table(alertas_data, colWidths=[1.8*cm, 1.8*cm, 4.3*cm, 4.8*cm, 5.3*cm])
            al_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4527a0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ede7f6'), colors.white]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ce93d8')),
                ('PADDING', (0, 0), (-1, -1), 5),
            ]))
            elements.append(al_table)
        else:
            elements.append(Paragraph("El sistema operativo no cuenta con registros de alarmas ingresados.", normal_style))
            
        elements.append(Spacer(1, 0.4*cm))
        
        # ----------------------------------------------------
        # 3. REGISTRO DE INTERVENCIONES
        # ----------------------------------------------------
        elements.append(Paragraph("3. Registro de Intervenciones Profesionales", heading_style))
        if seguimientos:
            seg_data = [["ID Alerta", "Docente/Tutor Asignado", "Acción y Resolución", "Fecha"]]
            for s in seguimientos[:20]:
                seg_data.append([
                    f"#{s.alerta_id}",
                    s.docente[:20],
                    s.accion[:50] + "..." if len(s.accion)>50 else s.accion,
                    s.fecha.strftime("%d/%m/%Y") if s.fecha else "-"
                ])
            seg_table = Table(seg_data, colWidths=[2.5*cm, 4*cm, 9.5*cm, 2*cm])
            seg_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#e8eaf6'), colors.white]),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
                ('PADDING', (0, 0), (-1, -1), 5),
            ]))
            elements.append(seg_table)
        else:
            elements.append(Paragraph("Sin intervenciones reportadas en el presente corte.", normal_style))

        elements.append(Spacer(1, 2*cm))
        
        # FIRMA INSTITUCIONAL AÑADIDA POR INICIATIVA PROPIA
        firma_style = ParagraphStyle('Firma', parent=styles['Normal'], fontSize=10, alignment=1)
        elements.append(Paragraph("_____________________________________________", firma_style))
        elements.append(Spacer(1, 0.2*cm))
        elements.append(Paragraph("<b>Coordinación Académica</b><br/>Firma y Sello Digital", firma_style))

        elements.append(Spacer(1, 0.5*cm))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
        elements.append(Paragraph("Documento Oficial - Generado por Ecosistema SAE", subtitle_style))

        doc.build(elements)
        return True, output_path

    except Exception as e:
        return False, str(e)
    finally:
        session.close()
