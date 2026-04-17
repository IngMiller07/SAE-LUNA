import os
import telebot
from dotenv import load_dotenv
from app import app, db
from models import Estudiante
from chatbot import generar_respuesta

# Cargar variables de entorno (Token)
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

if not TOKEN or TOKEN == 'tu_token_aqui':
    print("❌ ERROR: El Token de Telegram no está configurado en el archivo .env")
    exit(1)

bot = telebot.TeleBot(TOKEN)

# Diccionario temporal para guardar estado de registro
user_states = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    
    with app.app_context():
        # Buscar si el usuario ya está registrado con este chat_id
        est = Estudiante.query.filter_by(telegram_chat_id=str(chat_id)).first()
        
        if est:
            bot.reply_to(message, f"¡Hola de nuevo, {est.nombre}! 👋\nSoy tu Asistente Académico SAE. Ya estás vinculado al sistema.\n\nPuedes preguntarme sobre tus materias, técnicas de estudio o alertas.\n_(Si deseas desvincular esta cuenta para usar otra, escribe /salir)_", parse_mode="Markdown")
        else:
            bot.reply_to(message, "¡Bienvenido al Asistente SAE! 🎓\nPara proporcionarte ayuda personalizada sobre tu riesgo académico y planes de estudio, necesito vincularte a nuestro sistema de alertas.\n\nPor favor, **escribe tu correo electrónico institucional** a continuación para buscarte en la base de datos:", parse_mode="Markdown")
            user_states[chat_id] = 'WAITING_EMAIL'

@bot.message_handler(commands=['logout', 'salir'])
def process_logout(message):
    chat_id = message.chat.id
    
    with app.app_context():
        est = Estudiante.query.filter_by(telegram_chat_id=str(chat_id)).first()
        if est:
            est.telegram_chat_id = None
            db.session.commit()
            if chat_id in user_states:
                del user_states[chat_id]
            bot.reply_to(message, "🔌 **Sesión cerrada correctamente.**\nSe ha desvinculado tu correo de este teléfono. Ya no recibirás notificaciones aquí.\n\nEscribe /start si deseas vincular otro correo institucional.", parse_mode="Markdown")
        else:
            bot.reply_to(message, "No hay ninguna sesión vinculada actualmente. Escribe /start para iniciar.")

@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == 'WAITING_EMAIL')
def process_email(message):
    chat_id = message.chat.id
    email = message.text.strip().lower()
    
    with app.app_context():
        est = Estudiante.query.filter_by(email=email).first()
        
        if est:
            try:
                est.telegram_chat_id = str(chat_id)
                db.session.commit()
                bot.reply_to(message, f"✅ ¡Enhorabuena {est.nombre}!\nTu cuenta ha sido vinculada exitosamente a tu perfil de la carrera de {est.carrera}.\n\nA partir de ahora recibirás aquí tus alertas académicas y puedes consultarme para armar tus planes de estudio personalizados. ¡Prueba preguntándome sobre tu materia más débil!")
                del user_states[chat_id]
            except Exception as e:
                bot.reply_to(message, "❌ Hubo un error al guardar tu cuenta. Intenta de nuevo más tarde.")
        else:
            bot.reply_to(message, "No pude encontrar ningún estudiante con ese correo. Por favor, asegúrate de que sea tu correo institucional (ej. nombre.apellido@universidad.edu) e intenta escribirlo de nuevo.")

@bot.message_handler(func=lambda message: True)
def handle_questions(message):
    chat_id = message.chat.id
    query = message.text
    
    with app.app_context():
        est = Estudiante.query.filter_by(telegram_chat_id=str(chat_id)).first()
        
        # Enviar indicador de escribiendo
        bot.send_chat_action(chat_id, 'typing')
        
        # Generar respuesta usando nuestra lógica RAG
        # Para Telegram, vamos a limpiar un poco la respuesta quitando los ### porque Telegram prefiere negritas * o **
        raw_respuesta = generar_respuesta(query, est, db.session)
        
        # Limpieza básica para Markdown en Telegram
        clean_respuesta = raw_respuesta.replace('###', '🎯').replace('**', '*').replace('---\n', '')
        
        # Enviar mensaje dividiendo en pedazos si es muy largo
        if len(clean_respuesta) > 4000:
            for x in range(0, len(clean_respuesta), 4000):
                bot.reply_to(message, clean_respuesta[x:x+4000])
        else:
            bot.reply_to(message, clean_respuesta)

if __name__ == '__main__':
    print("🤖 Iniciando Bot de Telegram de SAE...")
    bot.polling(none_stop=True)
