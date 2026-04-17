import sqlite3
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(BASE_DIR, 'sistema_alertas.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute('ALTER TABLE estudiantes ADD COLUMN telegram_chat_id VARCHAR(50);')
    conn.commit()
    print("✅ Columna 'telegram_chat_id' agregada exitosamente a la tabla 'estudiantes'.")
except sqlite3.OperationalError as e:
    print(f"ℹ️ OperationalError: {e}. (Probablemente la columna ya existe).")

conn.close()
