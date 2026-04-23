from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

def create_mock_pdf():
    filepath = os.path.join("documentos_rag", "Guia_Intervencion_Academica.pdf")
    c = canvas.Canvas(filepath, pagesize=letter)
    
    textobject = c.beginText()
    textobject.setTextOrigin(50, 750)
    textobject.setFont("Helvetica-Bold", 14)
    textobject.textLine("Guía de Intervención para Estudiantes en Riesgo Académico")
    textobject.setFont("Helvetica", 11)
    textobject.textLine("")
    
    lineas = [
        "Capítulo 1: Bajo Rendimiento en Matemáticas y Física",
        "Si el estudiante presenta un rendimiento menor a 12/20 en ciencias exactas:",
        "- Paso 1: Derivar a tutorías presenciales los martes y jueves a las 16:00.",
        "- Paso 2: Usar simuladores interactivos PhET para reforzar la comprensión.",
        "- Paso 3: Asignar 3 horas de autoestudio semanal guiado.",
        "",
        "Capítulo 2: Inasistencias Recurrentes",
        "Si el estudiante supera el 15% de inasistencias en el semestre:",
        "- Acción A: Contactar al área de bienestar universitario para evaluar situación.",
        "- Acción B: Restructurar horario si existe conflicto laboral.",
        "- Acción C: Requiere justificación médica o laboral oficial.",
        "",
        "Capítulo 3: Metodología Pomodoro Oficial",
        "Para mejorar la concentración se recomienda 25 min de estudio y 5 de descanso,",
        "aislando el teléfono móvil o aplicaciones de redes sociales.",
        "",
        "Capítulo 4: Apoyo Psicológico Estudiantil",
        "Todo estudiante en 'Riesgo Alto' tiene derecho a 5 sesiones gratuitas",
        "con el departamento de psicología. Debe solicitarlas al correo psico@universidad.edu."
    ]
    
    for l in lineas:
        textobject.textLine(l)
        
    c.drawText(textobject)
    c.save()
    print("Mock PDF creado con éxito.")

if __name__ == "__main__":
    create_mock_pdf()
