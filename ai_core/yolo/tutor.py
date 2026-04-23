def interpretar(predictions):
    if not predictions:
        return "no detectado"

    clases = [
        (p["class"].lower(), p["confidence"])
        for p in predictions
        if p["confidence"] > 0.65  # [Optimizado] Umbral estricto para ignorar falsas sombras
    ]

    if not clases:
        return "no detectado"

    nombres = [c for c, _ in clases]

    # Regla 1: Phone presente → siempre distraído (sin importar el resto)
    phone_confs = [conf for c, conf in clases if "phone" in c]
    if phone_confs and max(phone_confs) > 0.70: # [Optimizado] El teléfono necesita altisima confidencialidad
        return "distraido"

    # Regla 2: Distracted explícito del modelo
    if any("distracted" in c for c in nombres):
        return "distraido"

    # Regla 3: Focused explícito del modelo
    if any("focused" in c for c in nombres):
        # Pero si hay phone junto a focused → igual distraído
        if phone_confs:
            return "distraido"
        return "concentrado"

    # Regla 4: Solo face → concentrado (mirando cámara)
    if any("face" in c for c in nombres):
        return "concentrado"

    return "no detectado"


def logica_tutor(estado):
    mensajes = {
        "concentrado":    "Bien, sigue asi",
        "distraido":      "Estas distraido",
        "atencion_media": "Enfocate en la actividad",
    }
    return mensajes.get(estado, "No detectado")


def combinar_historial(historial):
    """
    Retorna las clases más frecuentes del historial.
    Si 'phone' o 'distracted' aparece en al menos 1 frame reciente → se incluye.
    Clases de 'atención' (focused, face) requieren mayoría.
    """
    from collections import Counter

    total_frames = len(historial)
    if total_frames == 0:
        return []

    conteo = Counter()
    for frame_preds in historial:
        # una clase por frame (evita duplicados dentro del mismo frame)
        clases_frame = set(
            p["class"].lower()
            for p in frame_preds
            if p["confidence"] > 0.65 # [Optimizado] Memoria estricta
        )
        for c in clases_frame:
            conteo[c] += 1

    resultado = []
    for clase, cantidad in conteo.items():
        # Phone y distracted: basta con aparecer en 1 de los últimos frames
        if "phone" in clase or "distracted" in clase:
            if cantidad >= 1:
                resultado.append(clase)
        else:
            # Focused, face, pen, book: necesitan aparecer en al menos 40% de frames
            if cantidad / total_frames >= 0.4:
                resultado.append(clase)

    return resultado