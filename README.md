# 🎓 Sistema de Alertas Tempranas (SAE) - Prototipo Universitario

El **Sistema de Alertas Tempranas Estudiantiles (SAE)** es una aplicación de escritorio avanzada para la detección proactiva e intervención de alumnos en riesgo académico o de deserción. Este proyecto universitario consolida un **Dashboard Gerencial**, **Visión por Computadora (YOLO/Roboflow)**, Inteligencia Artificial Generativa **(RAG con Llama 3.2)**, automatización en mensajería vía **Telegram** y la exportación local de archivos.

---

## ✨ Características Principales y Requisitos Cumplidos

El sistema fue diseñado acatando de manera irrestricta la rúbrica del proyecto 6, y agrupa cuatro (4) motores de IA principales:

1. **Aplicación GUI Robusta (CustomTkinter):**
   *   Gestión por pestañas (Sidebar menu) sin usar Tkinter clásico. Diseño premium oscuro con retroalimentación visual asíncrona.
   *   Dashboard interactivo con lista de estudiantes críticos y KPIs de asistencia/promedio en tiempo real extraídos de una base de datos local SQLite.

2. **Chatbot RAG Anti-Alucinaciones (Ollama + LangChain + ChromaDB):**
   *   El chatbot ("Luna") procesa preguntas de lenguaje natural en milisegundos construyendo un esquema RAG (Retrieval-Augmented Generation).
   *   Lee fragmentos de PDFs institucionales en la capeta oculta y cruza la información en tiempo real con los registros en SQL de notas y promedios reales del estudiante, sin inventar ni rellenar resultados.

3. **Visión YOLO en la Nube (API Roboflow Inference):**
   *   Módulo de monitoreo conductual embebido usando tu cámara.
   *   No usa un YOLO predeterminado ni asfixia la memoria RAM. Utiliza `inference-core` para interceptar la API oficial de Roboflow, descargando en tiempo real tu dataset `salman-yiavg/distracted-detection-2` entrenado y computando los `Bounding Boxes` de acuerdo a tus directrices estipuladas (*Distracted / Focused / Phone*). 

4. **Botificaciones Remotas (Telegram Bot API):**
   *   Canal de comunicación bidireccional asíncrono para notificar alertas de riesgo graves instantáneamente al dispositivo móvil de los coordinadores y estudiantes.

5. **Generador Profesional de Reportes (ReportLab):**
   *   Exporte inteligente de expedientes críticos a archivos PDF maquetados y paginados, con la flexibilidad para abrir cuadros de diálogo del sistema operativo y permitir al tutor guardar el resultado donde lo desee. 

---

## 🛠️ Tecnologías Empleadas

- **Frontend & App Engine:** Python 3.11, `customtkinter`, `threading`
- **Backend de Almacenamiento:** SQLite3 embebido administrado velozmente mediante **SQLAlchemy (ORM)**
- **Inteligencia NLP & RAG Text:** `langchain`, `langchain-ollama`, `langchain-chromadb`. Motor primario Llama 3.2, embebedores Nomic.
- **Visión Asistida:** `ultralytics` (YOLOv8 framework base), `inference-core` (Inferencia Roboflow nativa) y OpenCV `cv2`.
- **Automatización Documental:** `reportlab`, `pypdf`
- **Conectividad:** `pyTelegramBotAPI`, `python-dotenv`

---

## 🚀 Cómo Inicializar y Levantar el Proyecto (Guía Técnica)

### Paso 1: Prerrequisitos de Entorno
Asegúrate de tener instalado **Python 3.10 o superior** y **Ollama** instalado en tu computadora (para ejecutar el LLM local).
Descarga Ollama nativo en `ollama.com` e instala el modelo de base tecleando en cualquier terminal:
```bash
ollama run llama3.2
ollama pull nomic-embed-text
```

### Paso 2: Instalación de Dependencias
Dentro de la carpeta del proyecto, ejecuta la descarga masiva de requerimientos técnicos en tu consola:
```bash
pip install -r requirements.txt
pip install inference-core pydantic==2.8
```

### Paso 3: Variables de Entorno y Conexión APIS (.env)
Asegurate de crear un archivo en la raíz llamado `.env` y estructurarlo obligatoriamente con todos tus tokens:
```env
# BotFather en Telegram 
TELEGRAM_TOKEN=1234567:XX-XXXXXXXXXXXXXXXXXXX

# API de Roboflow para la autodescarga de la cámara YOLO
ROBOFLOW_API_KEY=tu_token_aqui_roboflow
```

### Paso 4: Base de Datos Embebida (Out of the Box)
A diferencia de proyectos abstractos, este SAE ya cuenta con toda la data académica lista para ti. Los datos (`sistema_alertas.db`) y la memoria semántica de las reglas universitarias (`chroma_db/`) se descargan automáticamente dentro de este repositorio sin configuraciones extra. No necesitas instalar ningún motor SQL externo, SQLite lo maneja por defecto.

### Paso 5: ¡Correr la Aplicación Final!
Todo está amarrado a un solo hilo maestro con limpieza en segundo plano. Nunca ejecutes varios scripts a la vez, únicamente corre este:
```bash
python main.py
```

---

## 📖 Manual de Usuario (Guía de Interfaz Paso a Paso)

El sistema cuenta con una barra de navegación lateral constante. A continuación se explica cómo interactuar con cada uno de los 5 módulos principales:

### 1. 📊 Dashboard Principal (Inicio)
- **Propósito:** Mostrar una vista macro del estado de la universidad.
- **Uso:** Al abrir la app, verás los KPIs superiores (Total de estudiantes, Alertas Activas, Promedios). En la parte inferior, una alerta roja listará a los estudiantes con Riesgo Alto y Medio para que sepas quiénes requieren tu atención primaria al iniciar el día.

### 2. 🤖 Luna IA (Asistente Académica RAG)
- **Propósito:** Resolver dudas instantáneas combinando el contexto interno de la Universidad (PDFs) con la Base de Datos oficial de estudiantes.
- **Uso:** Navega a la pestaña de Luna IA. En el cuadro de texto inferior puedes interactuar de dos modos:
  - *Búsqueda Institucional:* Pregunta cosas normativas como "¿Cómo cancelar una materia?" o "¿Cuál es el reglamento de becas?".
  - *Búsqueda Sensitiva:* Pregunta por el rendimiento de un alumno, por ejemplo: *"Dime el promedio real de carlos gomez"*. El sistema, ignorando temporalmente la base general, buscará en las tablas SQL a este alumno, extrayendo sus inasistencias y notas para redactarte una respuesta amigable. No tienes que preocuparte por las mayúsculas.

### 3. ⚠️ Gestión de Alertas Estudiantiles
- **Propósito:** Revisar y canalizar los avisos automáticos generados al bajar las notas de los alumnos.
- **Uso:** 
  1. Accede a la pestaña y revisa la lista de alertas (cada una mostrará nombre del alumno, tipo de alerta y prioridad).
  2. Haz clic en el botón verde **Atender** si tú, como tutor, vas a lidiar presencialmente con el caso (desactivando la urgencia en pantalla).
  3. Haz clic en el botón naranja **Escalar**. Esto invocará de modo silencioso la API de **Telegram**, haciéndole llegar en tiempo real el registro al celular del orientador estudiantil (bot).

### 4. 📄 Generación de Reportes PDF
- **Propósito:** Exportar consolidados masivos estadísticos para el coordinador o el decano.
- **Uso:** Da un solo clic en rojo al botón central **Descargar Reporte Completo**. Se abrirá en tu pantalla el Explorador de Archivos de Windows; elige en qué carpeta lo guardarás. La aplicación se congelará solo la barra de descarga un instante y un *tick* verde confirmará tu guardado exitoso con gráficas incrustadas.

### 5. 👁️ Monitoreo de Atención Activa (Visión YOLO)
- **Propósito:** Analizar la concentración y postura corporal de un estudiante frente al propio equipo en tutorías o clases.
- **Uso:** 
  1. Da un clic al botón de Play **(Iniciar Cámara)**.
  2. La pantalla cargará un frame de OpenCV y se conectará de fondo a Roboflow Universe. Trata de mantener tu perfil bien iluminado.
  3. **Demostración:** Finge estar viendo tu celular en tus manos debajo de la barbilla o mira repentinamente a un costado sin movimiento por 5 segundos continuos. Verás como la barra de Inatención lateral sube drásticamente mandando un evento de peligro a la bitácora cuando logre alcanzar el 100%.

---

## 🌐 Guía de Despliegue (Clonación para Docentes y Evaluadores)

Este proyecto está diseñado para funcionar de manera **autónoma y portable**. Al descargar o clonar este repositorio desde GitHub, el proyecto se descargará con la **Base de Datos SQL (estudiantes y alertas)** instruida y la **Base Vectorial (RAG con PDFs)** completamente incrustadas. Usted no necesita gestionar migraciones ni poblar datos manualmente.

Para ejecutar este sistema en su propia máquina de evaluación, por favor siga minuciosamente estos tres pasos:

### 1. Variables de Entorno (Tokens de Seguridad)
Por motivos de ciberseguridad, los *API Keys* y permisos no están públicos. En la ruta raíz encontrará un archivo llamado `.env.example`:
- Renombre ese archivo a simplemente `.env` (borrando la extensión `.example`).
- Ábralo con cualquier editor de texto y pegue las dos claves de acceso (Token de Telegram y API Key de Roboflow) proporcionadas por el equipo de desarrollo.

### 2. Motor de Inteligencia Artificial (Ollama)
"Luna" (nuestro asistente) corre localmente en su CPU/GPU para proteger la privacidad de los datos de la Universidad enviando cero datos a servidores de terceros (como OpenAI). Necesita instalar el motor de razonamiento antes de arrancar.
- Descargue Ollama desde [ollama.com](https://ollama.com/) e instálelo en su PC.
- Abra su terminal o Símbolo del Sistema y ejecute los siguientes comandos para descargar el cerebro base de lenguaje y el convertidor vectorial:
  ```bash
  ollama run llama3.2
  ollama pull nomic-embed-text
  ```

### 3. Arranque del Sistema
Instale las librerías dependientes (como interfaz gráfica UI, algoritmos matemáticos y procesamiento de imágenes) e inicie el archivo central del proyecto:
```bash
pip install -r requirements.txt
python main.py
```

🎉 **¡El proyecto SAE levantará idéntico y listó para la evaluación!**

> *Proyecto Académico Universitario: Arquitectura orientada a la concurrencia asíncrona, robustez en el diseño de interfaces modernas, e integración de vanguardia con modelos de Inteligencia Artificial locales y distribuidos en nube.*
