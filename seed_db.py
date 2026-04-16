import random
from datetime import datetime, timedelta
from app import app, db
from models import Estudiante, Calificacion, Alerta, Seguimiento, BaseConocimiento

CARRERAS = [
    'Ingeniería en Sistemas', 'Administración de Empresas',
    'Contaduría Pública', 'Ingeniería Industrial', 'Psicología',
    'Derecho', 'Medicina', 'Arquitectura'
]

MATERIAS_POR_CARRERA = {
    'Ingeniería en Sistemas': ['Algoritmos', 'Base de Datos', 'Redes', 'Matemáticas', 'Programación'],
    'Administración de Empresas': ['Finanzas', 'Marketing', 'Economía', 'Estadística', 'Gestión'],
    'Contaduría Pública': ['Contabilidad', 'Auditoría', 'Fiscalización', 'Finanzas', 'Estadística'],
    'Ingeniería Industrial': ['Manufactura', 'Logística', 'Estadística', 'Matemáticas', 'Calidad'],
    'Psicología': ['Psicopatología', 'Neurociencia', 'Estadística', 'Terapia', 'Investigación'],
    'Derecho': ['Derecho Civil', 'Derecho Penal', 'Constitucional', 'Procesal', 'Mercantil'],
    'Medicina': ['Anatomía', 'Fisiología', 'Farmacología', 'Patología', 'Bioquímica'],
    'Arquitectura': ['Diseño', 'Estructuras', 'Urbanismo', 'Historia del Arte', 'Matemáticas'],
}

NOMBRES = [
    'Ana García', 'Carlos Rodríguez', 'María López', 'José Martínez',
    'Sofía Hernández', 'Luis Torres', 'Valentina Díaz', 'Miguel Sánchez',
    'Isabella Ramírez', 'Andrés Flores', 'Camila Morales', 'Diego Jiménez',
    'Lucía Álvarez', 'Sebastián Cruz', 'Daniela Romero', 'Mateo Vargas',
    'Fernanda Castillo', 'Alejandro Mendoza', 'Paola Guerrero', 'Ricardo Ramos'
]

PERIODOS = ['2024-1', '2024-2', '2025-1']

CONOCIMIENTO = [
    {
        'tema': 'Técnicas de Estudio: Método Pomodoro',
        'contenido': '''El Método Pomodoro es una técnica de gestión del tiempo que mejora la concentración:
1. Elige una tarea a realizar
2. Configura un temporizador por 25 minutos (un "pomodoro")
3. Trabaja en la tarea hasta que suene el temporizador
4. Toma un descanso corto de 5 minutos
5. Después de 4 pomodoros, toma un descanso largo de 15-30 minutos

Beneficios: Reduce la procrastinación, mejora el enfoque y hace seguimiento del progreso.''',
        'tags': 'tiempo,concentración,estudio,organización,productividad,técnica'
    },
    {
        'tema': 'Plan de Estudio para Matemáticas',
        'contenido': '''Plan de Recuperación en Matemáticas (4 semanas):
Semana 1 - Fundamentos: Repasar álgebra básica, operaciones, fracciones. Recurso: Khan Academy (gratuito).
Semana 2 - Funciones: Funciones lineales, cuadráticas, exponenciales. Practicar 10 ejercicios diarios.
Semana 3 - Aplicaciones: Problemas de contexto real. Formar grupos de estudio.
Semana 4 - Evaluación: Simulacros de examen, identificar errores, reforzar temas débiles.

Recursos recomendados: Khan Academy, Matemáticas Profe Alex (YouTube), Wolfram Alpha para verificar.''',
        'tags': 'matemáticas,álgebra,funciones,cálculo,plan,recuperación,ejercicios'
    },
    {
        'tema': 'Plan de Estudio para Programación y Algoritmos',
        'contenido': '''Plan de Recuperación en Programación (4 semanas):
Semana 1 - Lógica básica: Variables, tipos de datos, operadores, condicionales. Practica en Scratch o Python.
Semana 2 - Estructuras de control: Bucles, funciones, recursividad. 1 ejercicio diario en HackerRank.
Semana 3 - Estructuras de datos: Listas, pilas, colas, árboles. Visualizar con VisuAlgo.net.
Semana 4 - Proyectos: Mini proyecto integrador. Code review con compañeros.

Recursos: freeCodeCamp, CS50 Harvard (gratuito), LeetCode (nivel fácil).''',
        'tags': 'programación,algoritmos,python,código,sistemas,bases,computación,software'
    },
    {
        'tema': 'Plan de Estudio para Base de Datos',
        'contenido': '''Plan de Recuperación en Base de Datos (3 semanas):
Semana 1 - Fundamentos: Modelos relacionales, entidad-relación, normalización (1FN, 2FN, 3FN).
Semana 2 - SQL: SELECT, INSERT, UPDATE, DELETE, JOIN. Practica en SQLiteOnline.com.
Semana 3 - Diseño avanzado: Índices, vistas, stored procedures, transacciones.

Ejercicio clave: Diseñar la BD de una librería completa (clientes, libros, ventas).
Recursos: W3Schools SQL, Mode Analytics Tutorial, SQLZoo.''',
        'tags': 'base de datos,sql,relacional,consultas,normalización,sistemas,datos'
    },
    {
        'tema': 'Gestión de la Ansiedad ante Exámenes',
        'contenido': '''Estrategias para reducir la ansiedad ante evaluaciones:
1. Preparación anticipada: Estudia en sesiones cortas días antes, no la noche anterior.
2. Técnica de respiración 4-7-8: Inhala 4s, retén 7s, exhala 8s. Repite 3 veces.
3. Visualización positiva: Imagínate respondiendo correctamente.
4. Rutina la noche anterior: Duerme 8 horas, prepara materiales, come bien.
5. Durante el examen: Lee todo primero, responde lo que sabes, gestiona el tiempo.

Recuerda: un examen no define tu valor como persona.''',
        'tags': 'ansiedad,estrés,examen,evaluación,salud mental,bienestar,técnica,concentración'
    },
    {
        'tema': 'Plan de Estudio para Estadística',
        'contenido': '''Plan de Recuperación en Estadística (4 semanas):
Semana 1 - Estadística descriptiva: Media, mediana, moda, desviación estándar. Usar Excel/Google Sheets.
Semana 2 - Probabilidad: Regla de la suma, multiplicación, distribuciones. Ejercicios contextualizados.
Semana 3 - Inferencia: Intervalos de confianza, pruebas de hipótesis (t-student, chi-cuadrado).
Semana 4 - Aplicación: Analizar un dataset real de tu área. Usar Google Colab con Python.

Recursos: StatQuest (YouTube), Khan Academy Statistics, SPSS o JASP (gratuito).''',
        'tags': 'estadística,probabilidad,datos,análisis,media,distribución,hipótesis,inferencia'
    },
    {
        'tema': 'Técnicas de Lectura y Comprensión de Textos',
        'contenido': '''Mejora tu comprensión lectora con estas estrategias:
1. Lectura SQ3R: Survey (explorar), Question (preguntar), Read (leer), Recite (resumir), Review (revisar).
2. Subrayado inteligente: Solo ideas principales (max 20% del texto).
3. Mapas mentales: Transforma el texto en un esquema visual.
4. Regla de los 3 pasos: Primera lectura rápida, segunda lectura profunda, tercera lectura para dudas.
5. Glosario propio: Anota términos nuevos con tu propia definición.''',
        'tags': 'lectura,comprensión,textos,derecho,psicología,medicina,humanidades,resumen'
    },
    {
        'tema': 'Plan de Estudio para Contabilidad y Finanzas',
        'contenido': '''Plan de Recuperación en Contabilidad (4 semanas):
Semana 1 - Ecuación contable: Activo = Pasivo + Patrimonio. Ejercicios de asientos contables.
Semana 2 - Estados financieros: Balance general, estado de resultados, flujo de efectivo.
Semana 3 - Análisis financiero: Razones financieras (liquidez, rentabilidad, endeudamiento).
Semana 4 - Casos reales: Analizar estados financieros de empresas públicas (bolsa de valores).

Herramientas: Excel con plantillas contables, AccountingCoach.com, casos de estudio Harvard.''',
        'tags': 'contabilidad,finanzas,balance,estados financieros,administración,economía,contaduría'
    },
    {
        'tema': 'Cómo Mejorar la Asistencia y Hábitos Académicos',
        'contenido': '''Si tienes problemas de asistencia, sigue este plan:
1. Identifica la causa raíz: ¿trabajo, transporte, desmotivación, salud?
2. Habla con tu tutor académico esta semana.
3. Crea una rutina fija: hora de levantarte, preparación, llegada a clases.
4. Usa un planner semanal (digital o físico) con todas tus clases y compromisos.
5. Encuentra un compañero de estudio para responsabilidad mutua.
6. Si hay causas externas graves (trabajo, familia), solicita apoyo institucional.

Recurso: App Notion o Google Calendar para organización.''',
        'tags': 'asistencia,hábitos,organización,puntualidad,motivación,rutina,responsabilidad'
    },
    {
        'tema': 'Plan de Estudio para Anatomía y Ciencias de la Salud',
        'contenido': '''Plan de Recuperación en Anatomía (4 semanas):
Semana 1 - Sistema esquelético y muscular: Usa modelos 3D en Visible Body o Complete Anatomy (app).
Semana 2 - Sistema nervioso y cardiovascular: Flashcards con Anki para memorizar estructuras.
Semana 3 - Sistemas digestivo, respiratorio y urinario: Dibujar y etiquetar de memoria.
Semana 4 - Integración: Casos clínicos simples relacionando sistemas.

Recursos: Netter Atlas de Anatomía, Khan Academy Medicine, YouTube "Armando Hasudungan".''',
        'tags': 'anatomía,medicina,fisiología,salud,cuerpo humano,biología,ciencias,memorización'
    },
    {
        'tema': 'Cómo Trabajar en Grupo de Forma Efectiva',
        'contenido': '''Guía para grupos de estudio productivos:
1. Máximo 4-5 personas para mayor participación.
2. Define roles: coordinador, secretario, expositor, investigador.
3. Agenda clara: tema del día, tiempo por tema, producto esperado.
4. Usa herramientas digitales: Google Docs, Notion, Discord para coordinar.
5. Cada miembro prepara su parte antes del encuentro.
6. Cierra con una reflexión: ¿qué aprendimos? ¿qué falta?

Evita: distracciones sociales, conversaciones fuera del tema, miembros que no participan.''',
        'tags': 'grupo,colaboración,trabajo equipo,organización,estrategia,productividad,social'
    },
    {
        'tema': 'Recursos Gratuitos para Estudiar en Línea',
        'contenido': '''Los mejores recursos gratuitos para estudiantes universitarios:
📚 Plataformas: Khan Academy, Coursera (auditar gratis), edX, MIT OpenCourseWare
🎥 YouTube: 3Blue1Brown (Matemáticas), Kurzgesagt (Ciencias), CrashCourse (general)
💻 Programación: freeCodeCamp, The Odin Project, CS50 Harvard
📖 Libros: Open Library, Project Gutenberg, Google Scholar
🔬 Ciencias: PubMed, ResearchGate, Sci-Hub (acceso a papers)
🧠 Productividad: Forest (app para enfoque), Notion (organización), Anki (flashcards)

Todos estos recursos son 100% gratuitos.''',
        'tags': 'recursos,gratuito,internet,online,plataforma,youtube,cursos,libros,tecnología'
    },
    {
        'tema': 'Manejo del Tiempo para Estudiantes con Carga Laboral',
        'contenido': '''Si estudias y trabajas, aplica estas estrategias:
1. Mapea tu semana: identifica TODAS tus horas disponibles (transporte, descansos).
2. Prioriza con la Matriz Eisenhower: urgente+importante primero.
3. Estudia en bloques cortos: 20-30 min son suficientes si son concentrados.
4. Aprovecha los tiempos muertos: podcasts educativos, flashcards en el celular.
5. Comunica tu situación al docente: muchos dan facilidades si lo pides a tiempo.
6. Una vez a la semana: planifica la siguiente semana completa.

Herramienta recomendada: Todoist o Google Tasks para gestión de pendientes.''',
        'tags': 'tiempo,trabajo,organización,planificación,carga,estrés,adulto,equilibrio'
    },
    {
        'tema': 'Plan de Recuperación General para Estudiantes en Riesgo',
        'contenido': '''Si estás en riesgo académico, este es tu plan de acción inmediato:
🚨 Esta semana:
- Identifica tus 2 materias más críticas
- Habla con tu tutor académico
- Revisa el reglamento de regularización de tu institución

📅 Próximas 2 semanas:
- Crea un horario de estudio (mínimo 2h diarias)
- Únete o forma un grupo de estudio
- Asiste al 100% de las clases

📈 Próximo mes:
- Evalúa tu progreso cada semana
- Ajusta tus estrategias según resultados
- Solicita asesoría adicional si es necesario

💪 Recuerda: La mayoría de los estudiantes que entran en riesgo pueden recuperarse con el apoyo adecuado.''',
        'tags': 'riesgo,recuperación,plan,urgente,general,apoyo,tutor,estrategia,motivación,bajo rendimiento'
    },
    {
        'tema': 'Técnica de Mapas Mentales para Estudiar',
        'contenido': '''Los mapas mentales potencian la memorización y comprensión:
Cómo hacer un mapa mental efectivo:
1. Coloca el TEMA CENTRAL en el medio (con imagen si puedes)
2. Dibuja ramas principales para cada subtema
3. De cada rama, agrega ramas secundarias con detalles
4. Usa colores diferentes para cada rama principal
5. Añade palabras clave, no oraciones completas
6. Incluye imágenes y símbolos para mayor retención

Herramientas digitales: MindMeister (gratuito), XMind, Coggle.it
Papel: Hoja horizontal, mínimo colores, letra clara

Ideal para: Derecho, Historia, Medicina, Administración, Psicología.''',
        'tags': 'mapas mentales,memorización,visual,organización,técnica,estudio,esquema,resumen,conceptos'
    },
]

TIPOS_ALERTA = ['bajo_rendimiento', 'inasistencias', 'tendencia_negativa']
PRIORIDADES = {'Alto': 'Alta', 'Medio': 'Media', 'Bajo': 'Baja'}


def generar_descripcion_alerta(tipo, estudiante):
    if tipo == 'bajo_rendimiento':
        return f"{estudiante.nombre} presenta un promedio de {estudiante.promedio:.1f}, por debajo del mínimo requerido."
    elif tipo == 'inasistencias':
        return f"{estudiante.nombre} tiene {estudiante.asistencia:.0f}% de asistencia, por debajo del 80% mínimo."
    else:
        return f"{estudiante.nombre} muestra una tendencia negativa en su rendimiento académico reciente."


def seed():
    with app.app_context():
        db.drop_all()
        db.create_all()

        print("Creando estudiantes...")
        estudiantes = []
        for i, nombre in enumerate(NOMBRES):
            carrera = random.choice(CARRERAS)
            semestre = random.randint(1, 8)
            asistencia = random.uniform(55, 99)
            promedio = random.uniform(4.5, 9.5)

            est = Estudiante(
                nombre=nombre,
                carrera=carrera,
                semestre=semestre,
                email=nombre.lower().replace(' ', '.') + '@universidad.edu',
                promedio=round(promedio, 2),
                asistencia=round(asistencia, 1),
            )
            est.calcular_riesgo()
            db.session.add(est)
            db.session.flush()

            materias = MATERIAS_POR_CARRERA.get(carrera, ['Materia General'])
            for materia in materias:
                for periodo in PERIODOS:
                    nota = round(random.uniform(4.0, 10.0), 1)
                    cal = Calificacion(
                        estudiante_id=est.id,
                        materia=materia,
                        periodo=periodo,
                        nota=nota
                    )
                    db.session.add(cal)
            estudiantes.append(est)

        db.session.commit()

        print("Generando alertas...")
        for est in estudiantes:
            if est.nivel_riesgo in ('Alto', 'Medio'):
                tipo = random.choice(TIPOS_ALERTA)
                alerta = Alerta(
                    estudiante_id=est.id,
                    tipo=tipo,
                    prioridad=PRIORIDADES[est.nivel_riesgo],
                    descripcion=generar_descripcion_alerta(tipo, est),
                    fecha=datetime.utcnow() - timedelta(days=random.randint(0, 14))
                )
                db.session.add(alerta)

        db.session.commit()

        print("Cargando base de conocimiento...")
        for doc in CONOCIMIENTO:
            bc = BaseConocimiento(
                tema=doc['tema'],
                contenido=doc['contenido'],
                tags=doc['tags']
            )
            db.session.add(bc)

        db.session.commit()
        print("✅ Base de datos poblada correctamente.")
        print(f"   - {len(estudiantes)} estudiantes registrados")
        alto = sum(1 for e in estudiantes if e.nivel_riesgo == 'Alto')
        medio = sum(1 for e in estudiantes if e.nivel_riesgo == 'Medio')
        bajo = sum(1 for e in estudiantes if e.nivel_riesgo == 'Bajo')
        print(f"   - Riesgo Alto: {alto} | Medio: {medio} | Bajo: {bajo}")


if __name__ == '__main__':
    seed()
