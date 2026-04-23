"""
vision_yolo.py  —  SAE · Monitoreo de Atención (Adaptador de Módulo Cerrado)
=========================================================
Este script actúa como Puente (Adapter Pattern) para consumir la IA
cerrada desarrollada por los compañeros, importando ai_core.yolo
y ejecutando la inferencia de manera asíncrona para no congelar la GUI.
"""

import os
import cv2
import threading
import time
import concurrent.futures

# Importaciones directas del módulo cerrado tal como fue exigido
from ai_core.yolo.detector import detectar
from ai_core.yolo.tutor import interpretar, logica_tutor, combinar_historial

def _draw_boxes(frame, predictions, estado):
    # Dibuja usando las predicciones nativas del closed module
    COLOR_ALERT   = (0, 0, 220)    
    COLOR_OK      = (0, 200, 80)   
    COLOR_NEUTRAL = (200, 200, 200) 
    
    if estado == "distraido":
        color = COLOR_ALERT
    elif estado == "concentrado":
        color = COLOR_OK
    else:
        color = COLOR_NEUTRAL

    for pred in predictions:
        if pred["confidence"] < 0.5:
            continue
        x, y = int(pred["x"]), int(pred["y"])
        w, h = int(pred["width"]), int(pred["height"])
        x1, y1 = int(x - w/2), int(y - h/2)
        x2, y2 = int(x + w/2), int(y + h/2)

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        txt = f"{pred['class']} {pred['confidence']:.2f}"
        (tw, th), _ = cv2.getTextSize(txt, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
        cv2.rectangle(frame, (x1, y1 - th - 8), (x1 + tw + 6, y1), color, -1)
        cv2.putText(frame, txt, (x1 + 3, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
    
    # Dibujar estado global en esquina superior
    mensaje = logica_tutor(estado)
    cv2.putText(frame, mensaje, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    return frame


class VisionMonitor:
    # Umbrales reducidos dado que la inferencia web asíncrona ocurre cada ~600ms
    ALERT_THRESHOLD = 5  
    MAX_HISTORIAL = 5

    def __init__(self):
        self.cap     = None
        self.running = False
        self.thread  = None
        
        # ThreadPool para evadir el delay de inferencia del módulo
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        self.future = None

        self.attention_state        = "ESPERANDO"
        self.inattention_frame_count = 0
        self.alert_count             = 0

        self.on_frame_update   = None  
        self.on_attention_alert = None 
        self.on_state_change    = None 
        
        self.historial = []
        self.last_predictions = []
        self.ultimo_estado = "no detectado"

    def _load_model(self):
        print("[YOLO Adaptador] Inicializado. Delegando inferencia a módulo cerrado 'ai_core/yolo/'.")

    def start_camera(self, camera_index: int = 0):
        if self.running: return
        self._load_model()
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            if self.on_state_change: self.on_state_change("ERROR_CAMARA", 0)
            return
        
        self.cap.set(3, 640)
        self.cap.set(4, 480)
        
        self.running = True
        self.inattention_frame_count = 0
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print(f"[YOLO Adaptador] Monitoreo interactivo iniciado.")

    def stop_camera(self):
        self.running = False
        if self.thread: self.thread.join(timeout=2)
        if self.cap:
            self.cap.release()
            self.cap = None
        self.attention_state = "ESPERANDO"
        if self.on_state_change: self.on_state_change("ESPERANDO", 0)

    def _loop(self):
        # Bucle central súper-veloz para mantener FPS en GUI (30fps)
        while self.running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.03)
                continue

            # Gestión Asíncrona: Solo mandar frame a la IA cuando la anterior termine
            if self.future is None or self.future.done():
                if self.future is not None:
                    try:
                        self.last_predictions = self.future.result()
                        
                        # Lógica estricta de "Tutor"
                        self.historial.append(self.last_predictions)
                        if len(self.historial) > self.MAX_HISTORIAL:
                            self.historial.pop(0)

                        clases = combinar_historial(self.historial)
                        estado_actual = interpretar([{"class": c, "confidence": 1.0} for c in clases])
                        
                        if estado_actual != "no detectado":
                            self.ultimo_estado = estado_actual
                            
                        # Mapear estado del módulo compañero a nuestra GUI SAE
                        has_alert = (self.ultimo_estado == "distraido")
                        has_focus = (self.ultimo_estado == "concentrado")
                        has_person = (self.ultimo_estado != "no detectado")
                        
                        new_state = self._compute_state(has_alert, has_focus, has_person)

                        if new_state != self.attention_state:
                            self.attention_state = new_state
                            if self.on_state_change:
                                self.on_state_change(new_state, self.inattention_frame_count)

                        if has_alert:
                            self.inattention_frame_count += 1
                        else:
                            self.inattention_frame_count = max(0, self.inattention_frame_count - 1)

                        if self.inattention_frame_count >= self.ALERT_THRESHOLD:
                            self.alert_count += 1
                            self.inattention_frame_count = 0
                            msg = f"Alerta SAE #{self.alert_count}: Inatención detectada por módulo inteligente Tutor."
                            if self.on_attention_alert:
                                self.on_attention_alert(msg)

                    except Exception as e:
                        print(f"Error asíncrono en módulo YOLO cerrado: {e}")
                
                # Despachar carga pesada (detectar API) al sub-hilo
                if self.running:
                    self.future = self.executor.submit(detectar, frame.copy())
                    
            # Acoplado visual de bounding boxes
            display_frame = _draw_boxes(frame.copy(), self.last_predictions, self.ultimo_estado)

            if self.on_frame_update:
                # Retorna [] vacío en el segundo arg porque GUI no lo requiere internamente.
                self.on_frame_update(display_frame, []) 

            time.sleep(0.03)

    def _compute_state(self, has_alert, has_focus, has_person):
        if has_alert:
            if self.inattention_frame_count < self.ALERT_THRESHOLD // 2: return "DISTRAIDO"
            return "ALERTA"
        elif has_focus:
            return "ATENTO"
        elif has_person:
            self.inattention_frame_count = max(0, self.inattention_frame_count - 1)
            return "ATENTO"
        else:
            return "SIN_PERSONA"
