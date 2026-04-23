import os
import threading
import telebot
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

bot = None
if TOKEN and TOKEN != 'tu_token_aqui':
    bot = telebot.TeleBot(TOKEN)

user_states = {}

def _get_context(est):
    if not est:
        return ""
    materia_debil = est.materia_mas_debil()
    # Mantenemos concordancia con el prompt del sistema anti-jerga de programación
    lines = ["EXPEDIENTE ENCONTRADO EN NUESTROS REGISTROS:",
             f"  Nombre completo: {est.nombre}",
             f"  Carrera: {est.carrera}",
             f"  Semestre: {est.semestre}",
             f"  Email institucional: {est.email}",
             f"  Promedio actual: {est.promedio:.2f} / 10.0",
             f"  Porcentaje de asistencia: {est.asistencia:.1f}%",
             f"  Nivel de riesgo SAE: {est.nivel_riesgo}"]
    if materia_debil:
        lines.append(f"  Materia mas debil: {materia_debil.materia} (nota: {materia_debil.nota:.1f})")
    
    lines.append("\nNOTA PARA EL LLM: El usuario con el que estas hablando por chat es ESTE estudiante. Hablale directamente, sin tecnicismos.")
    
    return "\n".join(lines)

if bot:
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        chat_id = message.chat.id
        from database import get_session
        from models import Estudiante
        session = get_session()
        try:
            est = session.query(Estudiante).filter_by(telegram_chat_id=str(chat_id)).first()
            if est:
                bot.reply_to(message, f"¡Hola de nuevo, {est.nombre}! 👋\n\nSoy *Luna*, tu asistente académica del SAE.\n\nPuedes preguntarme cualquier cosa sobre técnicas de estudio, tu situación académica o cómo mejorar tu rendimiento.\n\nEscribe */info* para ver tu perfil académico actual.", parse_mode="Markdown")
            else:
                bot.reply_to(message, "¡Bienvenido al *Asistente SAE*! 🎓\n\nSoy *Luna*, tu consultora académica virtual.\n\nPara darte una atención personalizada, necesito identificarte. Por favor escribe tu *correo institucional*:", parse_mode="Markdown")
                user_states[chat_id] = 'WAITING_EMAIL'
        finally:
            session.close()

    @bot.message_handler(commands=['info'])
    def send_profile(message):
        chat_id = message.chat.id
        from database import get_session
        from models import Estudiante, Alerta
        session = get_session()
        try:
            est = session.query(Estudiante).filter_by(telegram_chat_id=str(chat_id)).first()
            if est:
                alertas = session.query(Alerta).filter_by(estudiante_id=est.id, estado='Activa').count()
                riesgo_emoji = "🔴" if est.nivel_riesgo == "Alto" else ("🟡" if est.nivel_riesgo == "Medio" else "🟢")
                materia_debil = est.materia_mas_debil()
                msg = (f"📊 *Tu Perfil Académico*\n\n"
                       f"👤 Nombre: {est.nombre}\n"
                       f"🎓 Carrera: {est.carrera}\n"
                       f"📅 Semestre: {est.semestre}\n"
                       f"📈 Promedio: {est.promedio:.1f}/10\n"
                       f"✅ Asistencia: {est.asistencia:.0f}%\n"
                       f"{riesgo_emoji} Nivel de Riesgo: *{est.nivel_riesgo}*\n"
                       f"⚠️ Alertas Activas: {alertas}\n"
                       f"📚 Materia más débil: {materia_debil.materia if materia_debil else 'N/A'}")
                bot.reply_to(message, msg, parse_mode="Markdown")
            else:
                bot.reply_to(message, "No estás registrado aún. Escribe /start para vincular tu cuenta.")
        finally:
            session.close()

    @bot.message_handler(commands=['salir', 'logout'])
    def process_logout(message):
        chat_id = message.chat.id
        from database import get_session
        from models import Estudiante
        session = get_session()
        try:
            est = session.query(Estudiante).filter_by(telegram_chat_id=str(chat_id)).first()
            if est:
                est.telegram_chat_id = None
                session.commit()
                user_states.pop(chat_id, None)
                bot.reply_to(message, "Sesión cerrada. Escribe /start para volver a vincular.")
            else:
                bot.reply_to(message, "No hay sesión activa.")
        finally:
            session.close()

    @bot.message_handler(func=lambda msg: user_states.get(msg.chat.id) == 'WAITING_EMAIL')
    def process_email(message):
        chat_id = message.chat.id
        email = message.text.strip().lower()
        from database import get_session
        from models import Estudiante
        session = get_session()
        try:
            est = session.query(Estudiante).filter_by(email=email).first()
            if est:
                est.telegram_chat_id = str(chat_id)
                session.commit()
                user_states.pop(chat_id, None)
                riesgo_emoji = "🔴" if est.nivel_riesgo == "Alto" else ("🟡" if est.nivel_riesgo == "Medio" else "🟢")
                bot.reply_to(message,
                    f"✅ ¡Vinculado exitosamente!\n\n"
                    f"Hola, *{est.nombre}* 👋\n"
                    f"{riesgo_emoji} Tu riesgo académico actual es *{est.nivel_riesgo}*\n"
                    f"📊 Promedio: {est.promedio:.1f} | Asistencia: {est.asistencia:.0f}%\n\n"
                    f"Ahora puedes preguntarme cualquier cosa. Escribe */info* para ver tu perfil completo.",
                    parse_mode="Markdown")
            else:
                bot.reply_to(message, "No encontré ningún estudiante con ese correo. Verifica que sea tu correo institucional (ej: juan.perez@universidad.edu)")
        except Exception as e:
            bot.reply_to(message, "Hubo un error técnico. Intenta de nuevo.")
        finally:
            session.close()

    @bot.message_handler(func=lambda m: True)
    def handle_all(message):
        chat_id = message.chat.id
        query = message.text.strip()
        from database import get_session
        from models import Estudiante
        session = get_session()
        try:
            est = session.query(Estudiante).filter_by(telegram_chat_id=str(chat_id)).first()
            ctx = _get_context(est)
            bot.send_chat_action(chat_id, 'typing')
            from ai_core.rag_chatbot import get_chatbot
            rag = get_chatbot()
            response = rag.ask(query, explicit_db_context=ctx)
            
            # Formatear y Enviar respuesta a Telegram
            if len(response) > 4000:
                for i in range(0, len(response), 4000):
                    chunk = response[i:i+4000]
                    try:
                        bot.reply_to(message, chunk, parse_mode="Markdown")
                    except telebot.apihelper.ApiTelegramException:
                        bot.reply_to(message, chunk) # Fallback seguro
            else:
                try:
                    bot.reply_to(message, response, parse_mode="Markdown")
                except telebot.apihelper.ApiTelegramException:
                    bot.reply_to(message, response) # Fallback seguro
        finally:
            session.close()


class TelegramService:
    def __init__(self):
        self.thread = None
        self.running = False

    def start(self):
        if not bot:
            print("[Telegram] Token no configurado. Bot no iniciará.")
            return
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        print("[Telegram] Bot iniciado.")

    def _run(self):
        import time
        while self.running:
            try:
                bot.polling(none_stop=True, timeout=20, long_polling_timeout=15)
            except Exception as e:
                err = str(e)
                if "409" in err:
                    print("[Telegram] Conflicto de instancias (409). Reintentando en 10s...")
                    time.sleep(10)
                else:
                    print(f"[Telegram] Error: {e}")
                    time.sleep(5)

    def send_alert(self, chat_id, text):
        if bot and chat_id:
            try:
                bot.send_message(chat_id, text, parse_mode="Markdown")
            except Exception as e:
                print(f"[Telegram] Error enviando a {chat_id}: {e}")


_telegram_service = None

def get_telegram_service():
    global _telegram_service
    if _telegram_service is None:
        _telegram_service = TelegramService()
    return _telegram_service
