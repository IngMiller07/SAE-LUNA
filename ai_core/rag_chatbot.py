"""
RAG Chatbot - Luna, Asistente Academica del SAE
Motor: Ollama llama3.2 (local, gratis, sin internet)
Sistema anti-alucinacion: SOLO cita datos que recibe como contexto real.
"""

import os
import glob
import requests

from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTOR_STORE_DIR = os.path.join(_BASE_DIR, "chroma_db")
DOC_DIR = os.path.join(_BASE_DIR, "documentos_rag")
OLLAMA_BASE = "http://localhost:11434"
MODEL_NAME = "llama3.2"

# Palabras que indican pregunta sobre informacion real del sistema
DB_TRIGGERS = [
    "estado academico", "informacion de", "datos de",
    "riesgo de", "promedio de", "asistencia de", "buscar estudiante",
    "perfil de", "cuantos estudiantes", "lista de estudiantes",
    "estudiantes en riesgo", "quienes estan", "quienes tienen",
    "riesgo alto", "riesgo medio", "alertas activas", "cohorte",
    "reporte", "quien tiene", "cual es el riesgo",
]

# Palabras filtro que NO son nombres propios (expandido para soportar busqueda amigable)
STOP_WORDS = {
    # Pronombres, articulos, preposiciones
    "el", "la", "los", "las", "un", "una", "unos", "unas", "con", "por", "para", 
    "como", "sobre", "del", "al", "en", "tu", "mi", "su", "sus", "te", "me", "se",
    # Academicas / Sistema
    "estado", "academico", "academica", "informacion", "datos", "riesgo", 
    "promedio", "asistencia", "estudiante", "estudiantes", "carrera", "semestre", 
    "materia", "cancelar", "habilitar", "universidad", "sistema", "profesor", 
    "horario", "clases", "beca", "tutorias", "biblioteca", "programa", "plan",
    # Verbos, saludos, interrogantes
    "quiero", "saber", "cual", "cuales", "tiene", "esta", "estan", "seguro", 
    "porque", "nivel", "buscar", "perfil", "dame", "dime", "puedes", "puedo", 
    "hacer", "ver", "estoy", "hola", "luna", "bien", "gracias", "mucho", "poco", 
    "y", "o", "si", "no"
}

def _should_query_db(query: str) -> bool:
    """Determina si la pregunta necesita datos reales del sistema SAE."""
    q = query.lower()
    if any(kw in q for kw in DB_TRIGGERS):
        return True
    
    words = [w.strip(".,?!") for w in query.split()]
    name_candidates = [
        w for w in words
        # Ya NO requerimos w[0].isupper() para validar mayusculas. 
        # Si no esta en la lista de exclusion y tiene +3 letras, es candidato.
        if len(w) >= 3 and w.lower() not in STOP_WORDS and w.isalpha()
    ]
    
    # Si hay 2+ palabras candidatas que no conforman el lexico estandar, sospechamos q es nombre
    if len(name_candidates) >= 2:
        return True
    # Si mencionan "de + posible nombre"
    if len(name_candidates) >= 1 and any(t in q for t in [" de ", "del ", " para "]):
        return True
    return False


def _build_db_context(query: str) -> str:
    """
    Busca en el sistema. Busca cualquier candidato de nombre ignorando mayus/minusculas.
    """
    try:
        import sys
        if _BASE_DIR not in sys.path:
            sys.path.insert(0, _BASE_DIR)
        from database import get_session
        from models import Estudiante, Alerta
        from sqlalchemy import or_

        session = get_session()
        try:
            lines = []
            words = [w.strip(".,?!") for w in query.split()]
            search_terms = list(set([
                w for w in words
                if len(w) >= 3 and w.lower() not in STOP_WORDS and w.isalpha()
            ]))

            found = []
            if search_terms:
                conditions = [Estudiante.nombre.ilike(f"%{term}%") for term in search_terms]
                found = session.query(Estudiante).filter(or_(*conditions)).all()

            if found:
                lines.append("EXPEDIENTES ENCONTRADOS EN NUESTROS REGISTROS:")
                for e in found:
                    debil = e.materia_mas_debil()
                    alertas = session.query(Alerta).filter_by(estudiante_id=e.id, estado="Activa").all()
                    lines.append(f"  Nombre completo: {e.nombre}")
                    lines.append(f"  Carrera: {e.carrera}")
                    lines.append(f"  Semestre: {e.semestre}")
                    lines.append(f"  Email institucional: {e.email}")
                    lines.append(f"  Promedio actual: {e.promedio:.2f} / 10.0")
                    lines.append(f"  Porcentaje de asistencia: {e.asistencia:.1f}%")
                    lines.append(f"  Nivel de riesgo SAE: {e.nivel_riesgo}")
                    if debil:
                        lines.append(f"  Materia mas debil: {debil.materia} (nota: {debil.nota:.1f})")
                    lines.append(f"  Alertas activas: {len(alertas)}")
                    for a in alertas:
                        lines.append(f"    - [{a.prioridad}] {a.tipo}: {a.descripcion[:90]}")
                    lines.append("")
            else:
                # Resumen general cohorte
                estudiantes = session.query(Estudiante).order_by(Estudiante.nivel_riesgo, Estudiante.promedio).all()
                alertas_activas = session.query(Alerta).filter_by(estado="Activa").all()
                alto = [e for e in estudiantes if e.nivel_riesgo == "Alto"]
                medio = [e for e in estudiantes if e.nivel_riesgo == "Medio"]

                lines.append(f"RESUMEN GENERAL DEL SISTEMA — {len(estudiantes)} estudiantes registrados")
                lines.append(f"Alertas activas en el sistema: {len(alertas_activas)}")
                if alto:
                    lines.append(f"\nESTUDIANTES EN RIESGO ALTO ({len(alto)}):")
                    for e in alto:
                        lines.append(f"  - {e.nombre} | {e.carrera} Sem.{e.semestre}"
                                     f" | Prom: {e.promedio:.1f} | Asist: {e.asistencia:.0f}%")
                if medio:
                    lines.append(f"\nESTUDIANTES EN RIESGO MEDIO ({len(medio)}):")
                    for e in medio:
                        lines.append(f"  - {e.nombre} | {e.carrera} Sem.{e.semestre}"
                                     f" | Prom: {e.promedio:.1f} | Asist: {e.asistencia:.0f}%")

            return "\n".join(lines)

        finally:
            session.close()
    except Exception as e:
        return f"No pude extraer registros institucionales en este momento: {e}"


def _ollama_running() -> bool:
    try:
        return requests.get(f"{OLLAMA_BASE}/api/tags", timeout=3).status_code == 200
    except Exception:
        return False


def _model_available(model: str) -> bool:
    try:
        r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=3)
        return any(model in m["name"] for m in r.json().get("models", []))
    except Exception:
        return False


SYSTEM_PROMPT = """Eres Luna, la asistente academica del Sistema SAE de la Universidad Nacional Tecnologica (UNT).
Personalidad: calidez, empatia, precision. Hablas en espanol con naturalidad.

REGLAS ABSOLUTAS (si las violas el sistema falla):
1. JAMAS inventes datos numericos: promedios, notas, porcentajes o semestres. Usa unicamente los otorgados.
2. NUNCA menciones terminos crudos tecnicos de programacion para los usuarios como: "base de datos", "SQL", "contexto RAG" o "chunks". Si extraes informacion, refierete a ella de forma humana como: "el sistema", "el expediente", "nuestros registros".
3. Si te preguntan por un estudiante y su nombre NO aparece en la seccion "DATOS DEL SISTEMA SAE", responde de forma amable: "No logro encontrar a ese estudiante en los registros. ¿Podrias verificar si esta bien escrito?"
4. Cuando devuelvas datos academicos al usuario, no suenes como un robot leyendo una tabla. Habla de forma natural y calida, interpretando sus notas (ej: "Veo que Carlos tiene un promedio un poco bajo de 6.5, su materia debil es...").
5. Da respuestas suficientemente cortas para ser rapidas de leer, pero COMPLETAS (jamás cortes una frase a medias).

{db_section}
{rag_section}"""


class RAGChatbot:
    def __init__(self):
        self.vectorstore = None
        self.llm = None
        self.embeddings = None
        self.ready = False
        self._init()

    def _init(self):
        if not _ollama_running():
            print("[Luna] Ollama no esta corriendo.")
            return
        if not _model_available(MODEL_NAME):
            print(f"[Luna] Modelo '{MODEL_NAME}' no disponible.")
            return
        try:
            self.llm = OllamaLLM(
                model=MODEL_NAME,
                base_url=OLLAMA_BASE,
                temperature=0.3,
                num_predict=450,       # Suficientemente largo para no quedar incompleto, pero mas agil que 700.
                num_ctx=2048,          # Límite estricto de memoria de contexto para asegurar velocidad.
                top_k=30,
                top_p=0.85,
                repeat_penalty=1.1,
            )
            print(f"[Luna] LLM '{MODEL_NAME}' optimizado cargado.")
            self.ready = True
        except Exception as e:
            print(f"[Luna] Error LLM: {e}")
            return
        self._load_rag()

    def _load_rag(self):
        try:
            self.embeddings = OllamaEmbeddings(
                model="nomic-embed-text", base_url=OLLAMA_BASE)
            if os.path.exists(VECTOR_STORE_DIR) and os.listdir(VECTOR_STORE_DIR):
                self.vectorstore = Chroma(
                    persist_directory=VECTOR_STORE_DIR,
                    embedding_function=self.embeddings
                )
                n = self.vectorstore._collection.count()
                print(f"[Luna] VectorStore RAG: {n} fragmentos.")
            else:
                self._ingest_pdfs()
        except Exception as e:
            print(f"[Luna] RAG desactivado: {e}")
            self.vectorstore = None

    def _ingest_pdfs(self):
        pdfs = glob.glob(os.path.join(DOC_DIR, "*.pdf"))
        if not pdfs:
            print("[Luna] Sin PDFs en documentos_rag/")
            return
        try:
            docs = []
            for f in pdfs:
                docs.extend(PyPDFLoader(f).load())
            splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
            chunks = splitter.split_documents(docs)
            self.vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                persist_directory=VECTOR_STORE_DIR,
            )
            print(f"[Luna] {len(chunks)} fragmentos indexados.")
        except Exception as e:
            print(f"[Luna] Error ingesta: {e}")

    def _get_rag_context(self, query: str) -> str:
        if not self.vectorstore:
            return ""
        try:
            # RAG optimizado a 2 fragmentos maximo
            docs = self.vectorstore.similarity_search(query, k=2)
            return "\n\n".join(d.page_content for d in docs) if docs else ""
        except Exception:
            return ""

    def ask(self, query: str, explicit_db_context: str = "") -> str:
        if not self.llm:
            return ("Mi motor de IA no esta disponible. "
                    "Asegurate de que Ollama este corriendo.")

        db_section = ""
        if explicit_db_context:
            db_section = (
                "\n=== DATOS DEL SISTEMA SAE ===\n"
                + explicit_db_context +
                "\n=== FIN DATOS SAE ==="
            )
        elif _should_query_db(query):
            db_data = _build_db_context(query)
            db_section = (
                "\n=== DATOS DEL SISTEMA SAE ===\n"
                + db_data +
                "\n=== FIN DATOS SAE ==="
            )

        rag_raw = self._get_rag_context(query)
        rag_section = (
            "\n=== REGLAMENTACION INSTITUCIONAL (UNT) ===\n"
            + rag_raw +
            "\n=== FIN REGLAMENTACION ==="
        ) if rag_raw else ""

        system = SYSTEM_PROMPT.format(
            db_section=db_section,
            rag_section=rag_section
        )

        full_prompt = (
            f"INSTRUCCIONES DEL SISTEMA:\n{system}\n\n"
            f"ESTUDIANTE (USUARIO): {query}\n\n"
            f"RESPUESTA DE LUNA:"
        )

        try:
            response = self.llm.invoke(full_prompt)
            return str(response).strip()
        except Exception as e:
            return f"Tuve un problema tecnico, perdon la tardanza: {e}"


# ─── Singleton ────────────────────────────────────────────────────────────────
_chatbot_instance = None

def get_chatbot() -> RAGChatbot:
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = RAGChatbot()
    return _chatbot_instance
