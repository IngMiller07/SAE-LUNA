# Proyecto 6: Sistema de Alertas Tempranas para Estudiantes en Riesgo Académico

## 1. Problemática

La detección de estudiantes con bajo rendimiento o riesgo de deserción se realiza tardíamente, cuando ya es difícil intervenir de manera efectiva. La universidad requiere una herramienta que analice indicadores académicos en tiempo real y active alertas oportunas.

## 2. Objetivo General del Prototipo

Desarrollar una aplicación de escritorio (Python con backend que analice datos académicos, genere alertas tempranas, y active intervenciones automatizadas mediante IA generativa, visión por computadora y Telegram.

## 3. Aplicación de Escritorio

Aplicación de escritorio en Python con CustomTkinter (prohibido Tkinter estándar).

**Funcionalidades requeridas:**

- Ingesta y análisis de datos académicos por estudiante (notas, asistencias, repitencias).
- Generación automática de alertas con nivel de riesgo (bajo, medio, alto).
- Seguimiento docente por alertas activas.
- Historial de intervenciones realizadas.
- Generación de reportes PDF de riesgo por cohorte y programa.

## 4. Componentes de Inteligencia Artificial Requeridos

El prototipo DEBE implementar los cuatro (4) componentes de IA descritos a continuación. Cada componente es obligatorio y se evalúa de forma independiente en la rúbrica.

| Componente IA | Tecnología | Descripción y funcionalidad |
| --- | --- | --- |
| Chatbot RAG | LangChain + ChromaDB + OpenAI/Ollama | Intervención automatizada que ofrece planes de estudio personalizados a estudiantes en riesgo detectados. Responde dudas académicas y orienta hacia recursos de apoyo. Base de conocimiento construida con guías de estudio, planes de mejoramiento y recursos académicos institucionales. |
| YOLO + Roboflow + Cámara | YOLO + Roboflow + OpenCV | Análisis de atención e interés en tutorías o sesiones presenciales: el modelo detecta expresiones de desatención (mirando hacia otro lado, usando el celular) mediante la cámara activa del PC. El dataset debe entrenarse en Roboflow con muestras reales. |
| Telegram Bot | python-telegram-bot | Canal seguro para notificar al estudiante sobre su alerta de riesgo y conectarlo con un asesor académico. El estudiante puede responder para confirmar recepción o solicitar apoyo adicional. |
| Reportes PDF | ReportLab o WeasyPrint | Reporte de riesgo académico por cohorte con estadísticas, clasificación de alertas y registro de intervenciones. Exportable para coordinadores de programa desde la app de escritorio. |

**Aclaraciones técnicas importantes:**

- El Chatbot RAG debe construir su propia base de datos con documentos institucionales reales. No se acepta el uso de una API genérica sin RAG propio.
- YOLO debe entrenarse con un dataset propio en Roboflow. El modelo debe estar conectado a la cámara activa del PC para procesamiento en tiempo real.
- La aplicación de escritorio debe usar CustomTkinter. El uso de Tkinter estándar será penalizado con cero (0) en ese criterio.
- Los reportes PDF deben generarse automáticamente desde la app de escritorio usando ReportLab o WeasyPrint.

## 5. Stack Tecnológico Sugerido

- Frontend de escritorio: Python
- Backend/API: FastAPI o Flask (Python)
- Base de datos: PostgreSQL, SQLite o MongoDB
- IA Generativa RAG: LangChain + ChromaDB/FAISS + OpenAI API u Ollama (local)
- Visión por computadora: YOLO + Roboflow + OpenCV
- Bot de Telegram: python-telegram-bot
- Reportes PDF: ReportLab o WeasyPrint