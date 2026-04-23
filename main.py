import os
import sys
import threading

# Asegurar que el directorio raiz esté en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db
from telegram_bot import get_telegram_service
from gui.main_window import AppWindow
import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


def main():
    print("[SAE] Iniciando Sistema de Alertas Estudiantiles v2.0...")

    # 1. Base de datos
    print("[SAE] Verificando base de datos...")
    init_db()

    # 2. Iniciar Telegram en background
    print("[SAE] Iniciando Servicio Telegram...")
    tg_service = get_telegram_service()
    tg_service.start()

    # 3. Lanzar UI (el RAG se inicializa async dentro de la GUI)
    print("[SAE] Desplegando interfaz gráfica...")
    app = AppWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
