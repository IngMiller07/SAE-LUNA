"""
vision_yolo.py  —  SAE · Monitoreo de Atención con YOLO
=========================================================
Soporta tres modos automáticamente:
  1. Modelo personalizado local (distracted_model.pt) entrenado previamente.
  2. Roboflow Universe Local Inference (descarga automática via inference).
     Para esto requiere: pip install inference
  3. Modelo genérico COCO (yolov8n.pt) como fallback.
"""

import os
import cv2
import threading
import time

try:
    from ultralytics import YOLO
except ImportError:
    pass

_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ─── Rutas de modelos (orden de preferencia) ──────────────────────────────────
CUSTOM_MODEL_PATH = os.path.join(_BASE, "distracted_model.pt")
FALLBACK_MODEL_PATH = os.path.join(_BASE, "yolov8n.pt")


def get_api_key():
    """Busca la API Key en .env."""
    env_path = os.path.join(_BASE, ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.strip().startswith("ROBOFLOW_API_KEY"):
                    return line.split("=", 1)[1].strip().strip('"\'')
    return None


def _draw_boxes(frame, detections):
    COLOR_ALERT   = (0, 0, 220)    
    COLOR_OK      = (0, 200, 80)   
    COLOR_NEUTRAL = (200, 200, 200) 

    for det in detections:
        x1, y1, x2, y2 = det["box"]
        label = det["class"]
        conf  = det["conf"]
        color = COLOR_ALERT if det["is_alert"] else (
                COLOR_OK    if det["is_focused"] else COLOR_NEUTRAL)

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        txt = f"{label} {conf:.0%}"
        (tw, th), _ = cv2.getTextSize(txt, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
        cv2.rectangle(frame, (x1, y1 - th - 8), (x1 + tw + 6, y1), color, -1)
        cv2.putText(frame, txt, (x1 + 3, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
    return frame


class VisionMonitor:
    ALERT_THRESHOLD = 30   

    def __init__(self):
        self.model        = None
        self.model_loaded = False
        self.model_mode   = "none"    # "custom" | "roboflow" | "coco" | "none"
        
        self.cap     = None
        self.running = False
        self.thread  = None

        self.attention_state        = "ESPERANDO"
        self.inattention_frame_count = 0
        self.total_frames            = 0
        self.alert_count             = 0

        self.on_frame_update   = None  
        self.on_attention_alert = None 
        self.on_state_change    = None 

    def _load_model(self):
        """Carga el modelo de manera diferida cuando se abre la cámara."""
        # 1. Modelo Local Personalizado (ya entrenado)
        if os.path.exists(CUSTOM_MODEL_PATH):
            try:
                self.model = YOLO(CUSTOM_MODEL_PATH)
                self.model_loaded = True
                self.model_mode   = "custom"
                class_names = list(self.model.names.values())
                print(f"[YOLO] ✅ Modelo local cargado: {CUSTOM_MODEL_PATH} ({len(class_names)} clases)")
                return
            except Exception as e:
                print(f"[YOLO] ⚠ Error cargando modelo personalizado local: {e}")

        # 2. Roboflow Universe Inference Local Automático
        api_key = get_api_key()
        if api_key:
            try:
                # Requiere `pip install inference`
                from inference import get_model
                print("[YOLO] ⏳ Descargando/Inicializando modelo Roboflow via API...")
                # dataset de salman-yiavg/distracted-detection-2 version 1
                self.model = get_model(model_id="distracted-detection-2/1", api_key=api_key)
                self.model_loaded = True
                self.model_mode = "roboflow"
                print(f"[YOLO] ✅ Modelo Roboflow Universe cargado (distracted-detection-2/1)")
                return
            except ImportError:
                print("[YOLO] ⚠ Para auto-descargar el modelo de Roboflow, instala: pip install inference")
            except Exception as e:
                print(f"[YOLO] ⚠ No se pudo inicializar Roboflow inference: {e}")

        # 3. Fallback: COCO genérico
        if os.path.exists(FALLBACK_MODEL_PATH):
            try:
                self.model = YOLO(FALLBACK_MODEL_PATH)
                self.model_loaded = True
                self.model_mode   = "coco"
                print(f"[YOLO] ⚙ Modelo COCO de emergencia (fallback): {FALLBACK_MODEL_PATH}")
                return
            except Exception as e:
                pass

        print("[YOLO] ❌ No hay modelo disponible.")

    def start_camera(self, camera_index: int = 0):
        if self.running: return
        self._load_model()
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            if self.on_state_change: self.on_state_change("ERROR_CAMARA", 0)
            return
        self.running = True
        self.inattention_frame_count = 0
        self.total_frames = 0
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print(f"[YOLO] Monitoreo iniciado. Modo: {self.model_mode}")

    def stop_camera(self):
        self.running = False
        if self.thread: self.thread.join(timeout=2)
        if self.cap:
            self.cap.release()
            self.cap = None
        self.attention_state = "ESPERANDO"
        if self.on_state_change: self.on_state_change("ESPERANDO", 0)

    def _loop(self):
        while self.running and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.03)
                continue

            self.total_frames += 1
            detections = []
            has_alert   = False
            has_focus   = False
            has_person  = False

            if self.model_loaded:
                # Procesamiento según la librería
                if self.model_mode in ("custom", "coco"):
                    results = self.model(frame, conf=0.25, iou=0.45, verbose=False)
                    for r in results:
                        for box in r.boxes:
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            cls_name = self.model.names[int(box.cls[0])].lower()
                            conf     = float(box.conf[0])
                            is_alert, is_focused, is_person = self._classify(cls_name)
                            # Ignorar clases que no son persona, ni alerta, ni focus
                            if not (is_alert or is_focused or is_person):
                                continue

                            if is_alert: has_alert = True
                            if is_focused: has_focus = True
                            if is_person: has_person = True
                            detections.append({
                                "box": (x1, y1, x2, y2), "class": cls_name,
                                "conf": conf, "is_alert": is_alert, "is_focused": is_focused
                            })
                elif self.model_mode == "roboflow":
                    # Bajamos la confianza a 0.25 para que te detecte desde más lejos
                    results = self.model.infer(frame, confidence=0.25)[0]
                    if hasattr(results, "predictions"):
                        for p in results.predictions:
                            x, y = p.x, p.y
                            w, h = p.width, p.height
                            x1, y1 = int(x - w/2), int(y - h/2)
                            x2, y2 = int(x + w/2), int(y + h/2)
                            cls_name = str(p.class_name).lower()
                            conf = float(p.confidence)
                            
                            is_alert, is_focused, is_person = self._classify(cls_name)
                            if not (is_alert or is_focused or is_person):
                                continue

                            if is_alert: has_alert = True
                            if is_focused: has_focus = True
                            if is_person: has_person = True
                            detections.append({
                                "box": (x1, y1, x2, y2), "class": cls_name,
                                "conf": conf, "is_alert": is_alert, "is_focused": is_focused
                            })
                
                frame = _draw_boxes(frame.copy(), detections)

            # Lógica de estados
            new_state = self._compute_state(has_alert, has_focus, has_person)

            if new_state != self.attention_state:
                self.attention_state = new_state
                if self.on_state_change:
                    self.on_state_change(new_state, self.inattention_frame_count)

            if has_alert:
                self.inattention_frame_count += 1
            else:
                self.inattention_frame_count = max(0, self.inattention_frame_count - 2)

            if self.inattention_frame_count >= self.ALERT_THRESHOLD:
                self.alert_count += 1
                self.inattention_frame_count = 0
                cls_list = ", ".join(set(d["class"] for d in detections if d["is_alert"]))
                msg = (f"Alerta #{self.alert_count}: Inatención prolongada detectada "
                       f"({cls_list if cls_list else 'comportamiento sospechoso'}).")
                if self.on_attention_alert:
                    self.on_attention_alert(msg)

            if self.on_frame_update:
                self.on_frame_update(frame, detections)

            time.sleep(0.04)

    def _classify(self, cls_name: str):
        is_alert = False
        is_focused = False
        is_person = False
        if self.model_mode in ("custom", "roboflow"):
            if any(kw in cls_name for kw in {"distracted", "phone", "sleep", "not_focused"}):
                is_alert = True
            elif any(kw in cls_name for kw in {"focus", "attentive"}):
                is_focused = True
        else:
            if any(kw in cls_name for kw in {"cell phone", "laptop"}):
                is_alert = True
                
        if "person" in cls_name or "student" in cls_name or "human" in cls_name:
            is_person = True
            
        return is_alert, is_focused, is_person

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
