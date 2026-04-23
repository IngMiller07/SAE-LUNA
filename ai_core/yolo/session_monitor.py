import cv2
import time

from detector import detectar
from tutor import interpretar, logica_tutor, combinar_historial

historial = []
MAX_HISTORIAL = 5  # menos historial → más reactivo

ultimo_analisis = 0
intervalo = 0.8  # un poco más rápido

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

ultimo_estado = "no detectado"
contador_distraido = 0
predictions = []

while True:
    ret, frame = cap.read()
    if not ret:
        continue
    tiempo_actual = time.time()

    if tiempo_actual - ultimo_analisis > intervalo:

        predictions = detectar(frame)

        if predictions:
            print("Detectado:", [(p["class"], round(p["confidence"], 2)) for p in predictions])

        historial.append(predictions)
        if len(historial) > MAX_HISTORIAL:
            historial.pop(0)

        clases = combinar_historial(historial)
        print("Historial combinado:", clases)

        estado = interpretar([
            {"class": c, "confidence": 1.0} for c in clases
        ])

        # Anti-falso-positivo: distraído necesita confirmarse 2 veces seguidas
        if estado == "distraido":
            contador_distraido += 1
        else:
            contador_distraido = 0

        if estado == "distraido" and contador_distraido < 2:
            estado = ultimo_estado  # no cambiar todavía

        if estado != "no detectado":
            ultimo_estado = estado

        ultimo_analisis = tiempo_actual

    estado_mostrar = ultimo_estado
    mensaje = logica_tutor(estado_mostrar)

    colores = {
        "concentrado":    (0, 255, 0),
        "distraido":      (0, 0, 255),
        "atencion_media": (0, 165, 255),
    }
    color = colores.get(estado_mostrar, (255, 255, 255))

    cv2.putText(frame, mensaje, (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    if predictions:
        for pred in predictions:
            if pred["confidence"] < 0.5:
                continue
            x, y = int(pred["x"]), int(pred["y"])
            w, h = int(pred["width"]), int(pred["height"])
            cv2.rectangle(frame, (x - w//2, y - h//2), (x + w//2, y + h//2), color, 2)

            # etiqueta con clase y confianza
            label = f"{pred['class']} {pred['confidence']:.2f}"
            cv2.putText(frame, label, (x - w//2, y - h//2 - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    cv2.imshow("Tutor IA", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()