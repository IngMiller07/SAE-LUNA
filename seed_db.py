import random
from datetime import datetime, timedelta
from database import engine, get_session, init_db
from models import Base, Estudiante, Calificacion, Alerta, Seguimiento, BaseConocimiento

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
    }
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
    print("Inicializando base de datos...")
    Base.metadata.drop_all(bind=engine)
    init_db()
    
    session = get_session()

    try:
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
            session.add(est)
            session.flush()

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
                    session.add(cal)
            estudiantes.append(est)

        session.commit()

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
                session.add(alerta)

        session.commit()

        print("Cargando base de conocimiento...")
        for doc in CONOCIMIENTO:
            bc = BaseConocimiento(
                tema=doc['tema'],
                contenido=doc['contenido'],
                tags=doc['tags']
            )
            session.add(bc)

        session.commit()
        print("::: Base de datos poblada correctamente.")
        print(f"   - {len(estudiantes)} estudiantes registrados")
        alto = sum(1 for e in estudiantes if e.nivel_riesgo == 'Alto')
        medio = sum(1 for e in estudiantes if e.nivel_riesgo == 'Medio')
        bajo = sum(1 for e in estudiantes if e.nivel_riesgo == 'Bajo')
        print(f"   - Riesgo Alto: {alto} | Medio: {medio} | Bajo: {bajo}")
        
    except Exception as e:
        session.rollback()
        print(f"Error durante seed: {e}")
    finally:
        session.close()

if __name__ == '__main__':
    seed()
