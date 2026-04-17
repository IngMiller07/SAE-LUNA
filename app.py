from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from models import db, Estudiante, Calificacion, Alerta, Seguimiento, BaseConocimiento
from chatbot import generar_respuesta
from datetime import datetime
import os

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'sistema_alertas.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'sistema_alertas_secret_2025'

db.init_app(app)

# ─────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────

@app.route('/')
def dashboard():
    total = Estudiante.query.count()
    riesgo_alto = Estudiante.query.filter_by(nivel_riesgo='Alto').count()
    riesgo_medio = Estudiante.query.filter_by(nivel_riesgo='Medio').count()
    riesgo_bajo = Estudiante.query.filter_by(nivel_riesgo='Bajo').count()
    alertas_activas = Alerta.query.filter_by(estado='Activa').count()
    alertas_atendidas = Alerta.query.filter_by(estado='Atendida').count()

    top_en_riesgo = (
        Estudiante.query
        .filter_by(nivel_riesgo='Alto')
        .order_by(Estudiante.promedio.asc())
        .limit(5)
        .all()
    )

    # Datos para gráfico de tendencia de promedios por carrera
    carreras = db.session.query(Estudiante.carrera, db.func.avg(Estudiante.promedio)).group_by(Estudiante.carrera).all()
    chart_carreras = [c[0].split()[0] for c in carreras]
    chart_promedios = [round(c[1], 2) for c in carreras]

    return render_template('dashboard.html',
        total=total,
        riesgo_alto=riesgo_alto,
        riesgo_medio=riesgo_medio,
        riesgo_bajo=riesgo_bajo,
        alertas_activas=alertas_activas,
        alertas_atendidas=alertas_atendidas,
        top_en_riesgo=top_en_riesgo,
        chart_carreras=chart_carreras,
        chart_promedios=chart_promedios,
    )

# ─────────────────────────────────────────────
# ESTUDIANTES
# ─────────────────────────────────────────────

@app.route('/students')
def students():
    riesgo_filter = request.args.get('riesgo', '')
    carrera_filter = request.args.get('carrera', '')
    search = request.args.get('q', '')

    query = Estudiante.query
    if riesgo_filter:
        query = query.filter_by(nivel_riesgo=riesgo_filter)
    if carrera_filter:
        query = query.filter_by(carrera=carrera_filter)
    if search:
        query = query.filter(Estudiante.nombre.ilike(f'%{search}%'))

    estudiantes = query.order_by(Estudiante.nivel_riesgo.asc(), Estudiante.promedio.asc()).all()
    carreras = db.session.query(Estudiante.carrera).distinct().all()
    carreras = [c[0] for c in carreras]

    return render_template('students.html',
        estudiantes=estudiantes,
        carreras=carreras,
        riesgo_filter=riesgo_filter,
        carrera_filter=carrera_filter,
        search=search,
    )

@app.route('/students/<int:student_id>')
def student_detail(student_id):
    est = Estudiante.query.get_or_404(student_id)
    calificaciones = Calificacion.query.filter_by(estudiante_id=student_id).order_by(Calificacion.periodo).all()
    alertas = Alerta.query.filter_by(estudiante_id=student_id).order_by(Alerta.fecha.desc()).all()

    # Agrupar calificaciones por materia para gráfica
    materias_dict = {}
    for cal in calificaciones:
        materias_dict.setdefault(cal.materia, []).append(cal.nota)
    chart_materias = list(materias_dict.keys())
    chart_notas = [round(sum(v) / len(v), 2) for v in materias_dict.values()]

    # Periodos para tabla
    periodos = sorted(set(c.periodo for c in calificaciones))
    cal_por_materia = {}
    for cal in calificaciones:
        cal_por_materia.setdefault(cal.materia, {})[cal.periodo] = cal.nota

    return render_template('student_detail.html',
        est=est,
        alertas=alertas,
        cal_por_materia=cal_por_materia,
        periodos=periodos,
        chart_materias=chart_materias,
        chart_notas=chart_notas,
    )

# ─────────────────────────────────────────────
# ALERTAS
# ─────────────────────────────────────────────

@app.route('/alerts')
def alerts():
    estado_filter = request.args.get('estado', 'Activa')
    prioridad_filter = request.args.get('prioridad', '')

    query = Alerta.query
    if estado_filter:
        query = query.filter_by(estado=estado_filter)
    if prioridad_filter:
        query = query.filter_by(prioridad=prioridad_filter)

    alertas = query.order_by(Alerta.fecha.desc()).all()

    stats = {
        'total': Alerta.query.count(),
        'activas': Alerta.query.filter_by(estado='Activa').count(),
        'atendidas': Alerta.query.filter_by(estado='Atendida').count(),
        'escaladas': Alerta.query.filter_by(estado='Escalada').count(),
        'alta': Alerta.query.filter_by(prioridad='Alta', estado='Activa').count(),
        'media': Alerta.query.filter_by(prioridad='Media', estado='Activa').count(),
    }

    return render_template('alerts.html',
        alertas=alertas,
        stats=stats,
        estado_filter=estado_filter,
        prioridad_filter=prioridad_filter,
    )

@app.route('/alerts/<int:alert_id>/action', methods=['POST'])
def alert_action(alert_id):
    alerta = Alerta.query.get_or_404(alert_id)
    data = request.get_json()
    accion = data.get('accion')
    docente = data.get('docente', 'Docente')

    if accion == 'atender':
        alerta.estado = 'Atendida'
        msg = 'Alerta marcada como atendida.'
    elif accion == 'escalar':
        alerta.estado = 'Escalada'
        msg = 'Alerta escalada a coordinación.'
    else:
        return jsonify({'success': False, 'message': 'Acción inválida'}), 400

    seg = Seguimiento(
        alerta_id=alert_id,
        docente=docente,
        accion=f"{accion.capitalize()}: {msg}",
    )
    db.session.add(seg)
    db.session.commit()
    return jsonify({'success': True, 'message': msg, 'nuevo_estado': alerta.estado})

@app.route('/alerts/generate', methods=['POST'])
def generate_alerts():
    """Regenera alertas automáticas para todos los estudiantes."""
    estudiantes = Estudiante.query.all()
    nuevas = 0
    for est in estudiantes:
        ya_tiene = Alerta.query.filter_by(estudiante_id=est.id, estado='Activa').first()
        if not ya_tiene and est.nivel_riesgo in ('Alto', 'Medio'):
            tipo = 'bajo_rendimiento' if est.promedio < 6.5 else 'inasistencias'
            desc = f"{est.nombre}: promedio {est.promedio:.1f}, asistencia {est.asistencia:.0f}%."
            nueva = Alerta(
                estudiante_id=est.id,
                tipo=tipo,
                prioridad='Alta' if est.nivel_riesgo == 'Alto' else 'Media',
                descripcion=desc,
            )
            db.session.add(nueva)
            db.session.flush() # Para obtener el ID si fuera necesario
            
            # Enviar notificación Telegram si está vinculado
            if est.telegram_chat_id:
                try:
                    import telebot
                    import os
                    from dotenv import load_dotenv
                    load_dotenv()
                    telegram_token = os.getenv('TELEGRAM_TOKEN')
                    if telegram_token and telegram_token != 'tu_token_aqui':
                        bot = telebot.TeleBot(telegram_token)
                        msg = f"⚠️ *ALERTA ACADÉMICA*\n¡Hola {est.nombre}!\n\nTienes una nueva alerta por _{tipo.replace('_', ' ')}_.\n*Nivel de Prioridad:* {nueva.prioridad}\n\nPor favor, ingresa al portal o comunícate con tu docente."
                        bot.send_message(est.telegram_chat_id, msg, parse_mode="Markdown")
                except Exception as e:
                    print(f"Error mandando Telegram a {est.nombre}: {e}")
                    
            nuevas += 1
    db.session.commit()
    return jsonify({'success': True, 'nuevas_alertas': nuevas})

# ─────────────────────────────────────────────
# CHATBOT
# ─────────────────────────────────────────────

@app.route('/chatbot')
def chatbot():
    estudiante_id = request.args.get('student_id')
    est = Estudiante.query.get(estudiante_id) if estudiante_id else None
    estudiantes = Estudiante.query.order_by(Estudiante.nombre).all()
    return render_template('chatbot.html', est=est, estudiantes=estudiantes)

@app.route('/chatbot/message', methods=['POST'])
def chatbot_message():
    data = request.get_json()
    query = data.get('message', '').strip()
    estudiante_id = data.get('student_id')

    if not query:
        return jsonify({'response': 'Por favor escribe un mensaje.'})

    est = Estudiante.query.get(estudiante_id) if estudiante_id else None
    respuesta = generar_respuesta(query, est, db.session)
    return jsonify({'response': respuesta})

# ─────────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
