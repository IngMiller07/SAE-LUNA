from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Estudiante(db.Model):
    __tablename__ = 'estudiantes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    carrera = db.Column(db.String(100), nullable=False)
    semestre = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    promedio = db.Column(db.Float, default=0.0)
    asistencia = db.Column(db.Float, default=0.0)  # porcentaje 0-100
    nivel_riesgo = db.Column(db.String(10), default='Bajo')  # Alto, Medio, Bajo
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    telegram_chat_id = db.Column(db.String(50), nullable=True)

    calificaciones = db.relationship('Calificacion', backref='estudiante', lazy=True, cascade='all, delete-orphan')
    alertas = db.relationship('Alerta', backref='estudiante', lazy=True, cascade='all, delete-orphan')

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


class Calificacion(db.Model):
    __tablename__ = 'calificaciones'
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('estudiantes.id'), nullable=False)
    materia = db.Column(db.String(100), nullable=False)
    periodo = db.Column(db.String(20), nullable=False)  # ej. "2024-1", "2024-2"
    nota = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'materia': self.materia,
            'periodo': self.periodo,
            'nota': self.nota,
        }


class Alerta(db.Model):
    __tablename__ = 'alertas'
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('estudiantes.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # bajo_rendimiento, inasistencias, tendencia_negativa
    prioridad = db.Column(db.String(10), nullable=False)  # Alta, Media, Baja
    descripcion = db.Column(db.Text, nullable=False)
    estado = db.Column(db.String(20), default='Activa')  # Activa, Atendida, Escalada
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

    seguimientos = db.relationship('Seguimiento', backref='alerta', lazy=True, cascade='all, delete-orphan')

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


class Seguimiento(db.Model):
    __tablename__ = 'seguimientos'
    id = db.Column(db.Integer, primary_key=True)
    alerta_id = db.Column(db.Integer, db.ForeignKey('alertas.id'), nullable=False)
    docente = db.Column(db.String(100), nullable=False)
    accion = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)


class BaseConocimiento(db.Model):
    __tablename__ = 'base_conocimiento'
    id = db.Column(db.Integer, primary_key=True)
    tema = db.Column(db.String(150), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    tags = db.Column(db.String(300), nullable=False)  # CSV de palabras clave
