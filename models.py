from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Estudiante(Base):
    __tablename__ = 'estudiantes'
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    carrera = Column(String(100), nullable=False)
    semestre = Column(Integer, nullable=False)
    email = Column(String(120), nullable=False)
    promedio = Column(Float, default=0.0)
    asistencia = Column(Float, default=0.0)  # porcentaje 0-100
    nivel_riesgo = Column(String(10), default='Bajo')  # Alto, Medio, Bajo
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    telegram_chat_id = Column(String(50), nullable=True)

    calificaciones = relationship('Calificacion', backref='estudiante', lazy=True, cascade='all, delete-orphan')
    alertas = relationship('Alerta', backref='estudiante', lazy=True, cascade='all, delete-orphan')

    def calcular_riesgo(self):
        if self.promedio < 6.0 or self.asistencia < 70:
            self.nivel_riesgo = 'Alto'
        elif self.promedio < 7.5 or self.asistencia < 80:
            self.nivel_riesgo = 'Medio'
        else:
            self.nivel_riesgo = 'Bajo'
        return self.nivel_riesgo

    def materia_mas_debil(self):
        if not self.calificaciones:
            return None
        return min(self.calificaciones, key=lambda c: c.nota)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'carrera': self.carrera,
            'semestre': self.semestre,
            'email': self.email,
            'promedio': round(self.promedio, 2),
            'asistencia': round(self.asistencia, 1),
            'nivel_riesgo': self.nivel_riesgo,
        }


class Calificacion(Base):
    __tablename__ = 'calificaciones'
    id = Column(Integer, primary_key=True)
    estudiante_id = Column(Integer, ForeignKey('estudiantes.id'), nullable=False)
    materia = Column(String(100), nullable=False)
    periodo = Column(String(20), nullable=False)  # ej. "2024-1", "2024-2"
    nota = Column(Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'materia': self.materia,
            'periodo': self.periodo,
            'nota': self.nota,
        }


class Alerta(Base):
    __tablename__ = 'alertas'
    id = Column(Integer, primary_key=True)
    estudiante_id = Column(Integer, ForeignKey('estudiantes.id'), nullable=False)
    tipo = Column(String(50), nullable=False)  # bajo_rendimiento, inasistencias, tendencia_negativa
    prioridad = Column(String(10), nullable=False)  # Alta, Media, Baja
    descripcion = Column(Text, nullable=False)
    estado = Column(String(20), default='Activa')  # Activa, Atendida, Escalada
    fecha = Column(DateTime, default=datetime.utcnow)

    seguimientos = relationship('Seguimiento', backref='alerta', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'estudiante_id': self.estudiante_id,
            'estudiante_nombre': self.estudiante.nombre if self.estudiante else '',
            'tipo': self.tipo,
            'prioridad': self.prioridad,
            'descripcion': self.descripcion,
            'estado': self.estado,
            'fecha': self.fecha.strftime('%Y-%m-%d %H:%M'),
        }


class Seguimiento(Base):
    __tablename__ = 'seguimientos'
    id = Column(Integer, primary_key=True)
    alerta_id = Column(Integer, ForeignKey('alertas.id'), nullable=False)
    docente = Column(String(100), nullable=False)
    accion = Column(Text, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)


class BaseConocimiento(Base):
    __tablename__ = 'base_conocimiento'
    id = Column(Integer, primary_key=True)
    tema = Column(String(150), nullable=False)
    contenido = Column(Text, nullable=False)
    tags = Column(String(300), nullable=False)  # CSV de palabras clave
