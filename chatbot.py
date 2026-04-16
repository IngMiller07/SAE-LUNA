import re
from models import BaseConocimiento

def _tokenize(text):
    """Simple tokenizer: lowercase, split by non-alphanumeric, filter short tokens."""
    text = text.lower()
    tokens = re.split(r'[^a-záéíóúüñ0-9]+', text)
    return set(t for t in tokens if len(t) > 2)

def buscar_documentos(query, db_session, top_k=3):
    """
    Búsqueda por solapamiento de tokens entre la query y los tags/tema de cada documento.
    Devuelve los top_k documentos más relevantes.
    """
    query_tokens = _tokenize(query)
    docs = db_session.query(BaseConocimiento).all()
    scored = []
    for doc in docs:
        doc_tokens = _tokenize(doc.tags + ' ' + doc.tema + ' ' + doc.contenido[:200])
        overlap = len(query_tokens & doc_tokens)
        if overlap > 0:
            scored.append((overlap, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for _, doc in scored[:top_k]]

def generar_respuesta(query, estudiante_ctx, db_session):
    """
    Genera una respuesta RAG:
    1. Recupera documentos relevantes
    2. Combina con el contexto del estudiante
    3. Retorna respuesta estructurada
    """
    docs = buscar_documentos(query, db_session)

    # Contexto del estudiante (puede ser None si es consulta anónima)
    ctx_text = ''
    if estudiante_ctx:
        ctx_text = (
            f"📊 **Tu perfil académico:**\n"
            f"- Promedio: {estudiante_ctx.promedio:.2f}\n"
            f"- Asistencia: {estudiante_ctx.asistencia:.0f}%\n"
            f"- Nivel de riesgo: {estudiante_ctx.nivel_riesgo}\n"
        )
        materia_debil = estudiante_ctx.materia_mas_debil()
        if materia_debil:
            ctx_text += f"- Materia más débil: {materia_debil.materia} ({materia_debil.nota:.1f})\n"
        ctx_text += '\n'

    if not docs:
        return (
            ctx_text +
            "No encontré información específica sobre eso, pero puedo ayudarte con:\n"
            "- Técnicas de estudio (pomodoro, mapas mentales)\n"
            "- Planes de recuperación por materia\n"
            "- Manejo del estrés y ansiedad\n"
            "- Gestión del tiempo\n\n"
            "¿Sobre cuál de estos temas te gustaría más información?"
        )

    respuesta = ctx_text
    for i, doc in enumerate(docs):
        respuesta += f"### 📚 {doc.tema}\n"
        respuesta += doc.contenido.strip() + '\n\n'
        if i < len(docs) - 1:
            respuesta += '---\n\n'

    respuesta += '\n💬 ¿Tienes alguna pregunta específica sobre alguno de estos temas?'
    return respuesta
