# 🎓 Sistema de Alertas Tempranas (SAE)

El **Sistema de Alertas Tempranas (SAE)** es una aplicación web diseñada para tutores y docentes. Su objetivo principal es detectar de forma proactiva a estudiantes en riesgo académico (basado en promedios e inasistencias), permitiendo una intervención rápida. Además, integra un Asistente Académico Inteligente (Chatbot RAG) que genera planes de estudio personalizados para los estudiantes.

---

## ✨ Características Principales

1. **Dashboard Directivo:** Panel general con métricas (KPIs), gráficas interactivas y un top 5 de alumnos en riesgo crítico.
2. **Directorio y Perfil Estudiantil:** Listado filtrable de alumnos (por riesgo, carrera, etc.) y un perfil detallado con historial de calificaciones y alertas.
3. **Gestión de Alertas:** Bandeja de entrada donde los docentes pueden atender o escalar las alertas automáticas que el sistema genera por bajo rendimiento.
4. **Chatbot RAG (IA Local):** Un asistente que utiliza Recuperación Aumentada (Retrieval-Augmented Generation) cruzando la información del estudiante con una base de conocimientos local para dar consejos precisos.
5. **Diseño Moderno:** Interfaz de usuario con modo oscuro (Dark Mode), diseño Glassmorphism y notificaciones en tiempo real (Toasts).

---

## 🛠️ Tecnologías Utilizadas

*   **Backend:** Python 3 + Flask
*   **Base de Datos:** SQLite (Sin configuración extra) + SQLAlchemy (ORM)
*   **Inteligencia (Chatbot):** Scikit-learn (Algoritmo TF-IDF local, sin costo de API externa)
*   **Frontend:** Jinja2 (Motor de plantillas), HTML5, CSS3 Nativo, JavaScript (AJAX)
*   **Gráficos:** Chart.js (CDN)

---

## ⚙️ Estructura del Proyecto

```text
sistema-alertas/
│
├── app.py                  # Archivo principal de la aplicación (Rutas y Lógica)
├── chatbot.py              # Motor RAG local para el Asistente Inteligente
├── models.py               # Modelos de Bases de Datos (Estudiantes, Alertas, BC...)
├── seed_db.py              # Script para poblar la BD con datos simulados
├── requirements.txt        # Dependencias de Python necesarias
├── sistema_alertas.db      # ¡Tu Base de Datos SQLite autogenerada!
│
├── static/
│   └── css/styles.css      # Hoja de estilos principal (Glassmorphism & Variables)
│
└── templates/              # Vistas y componentes HTML
    ├── base.html           # Plantilla maestra (Navbar, Estilos, Toasts base)
    ├── dashboard.html      # Pantalla 1: Home y gráficas generales
    ├── students.html       # Pantalla 2: Directorio con filtros
    ├── student_detail.html # Pantalla 3: Perfil individual y progreso
    ├── alerts.html         # Pantalla 4: Área para atender/escalar alertas
    └── chatbot.html        # Pantalla 5: Interfaz del asistente IA
```

---

## 🚀 Cómo inicializar y correr el proyecto

Sigue estos pasos para instalar el proyecto en tu computadora local:

### 1. Prerrequisitos
Asegúrate de tener instalado **Python 3.8 o superior** en tu sistema.

### 2. Instalar las dependencias
Abre una terminal o consola de comandos, ubícate en la carpeta del proyecto y ejecuta:

```bash
pip install -r requirements.txt
```

### 3. Crear y Poblar la Base de Datos
Para generar la base de datos `sistema_alertas.db` y llenarla con 20 alumnos de prueba y los textos para el chatbot Inteligente, ejecuta:

```bash
python seed_db.py
```
*(Deberás ver un mensaje de éxito indicando que se crearon estudiantes, alertas y la base de conocimiento).*

### 4. Arrancar el Servidor Web
Una vez configurado todo, levanta la aplicación:

```bash
python app.py
```

### 5. Usar el sistema
Abre tu navegador de preferencia (Chrome, Edge, Firefox) y dirígete a:
👉  **http://127.0.0.1:5000** 

---

## 📖 Instrucciones de Uso Rápido (Demo)

1. **Botón "Generar Alertas":** Si visitas el *Dashboard* o la pestaña de *Alertas*, verás este botón azul arriba a la derecha. Sirve para que el sistema escanee la BD en ese instante y levante notificaciones a profesores.
2. **Atender Alerta:** Ve al panel de *Alertas*. Verás botones verdes (Atender) y naranjas (Escalar). Presiona uno para simular que como profesor ya actuaste al respecto. Verás cómo desaparece de tu bandeja de tareas.
3. **Probar el RAG:** Ve a la pestaña *Chatbot*. 
   * A la izquierda, selecciona el nombre de algún alumno.
   * Selecciona una pregunta rápida, por ejemplo: *"Dame un plan de estudio personalizado"*.
   * Verás que el Bot usa *su nombre*, revisa *su promedio*, detecta *su materia más débil* y además busca en la BD un plan de acción para guiarlo.
