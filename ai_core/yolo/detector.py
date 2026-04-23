import cv2
import numpy as np
import base64
from inference_sdk import InferenceHTTPClient

CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com/",
    api_key="8lT1sISr0MH9Xgt1697a"
)

def detectar(frame):
    # Optimización: Reducir drasticamente la calidad estructural del JPEG para acelerar la latencia de subida (Base64) en un 50%
    # No se altera ni recorta el tamaño real, así preservamos con exactitud las coordenadas que dibujarán las cajas despues.
    _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 60])
    b64 = base64.b64encode(buffer).decode("utf-8")

    result = CLIENT.infer(b64, model_id="distracted-detection-2/1")
    return result.get("predictions", [])