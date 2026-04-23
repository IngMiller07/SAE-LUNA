"""
train_yolo.py  —  SAE · Entrenamiento YOLO con Dataset Roboflow
================================================================
Dataset: Distracted Detection 2 (salman-yiavg)
URL: https://universe.roboflow.com/salman-yiavg/distracted-detection-2

Clases esperadas (confirmar en data.yaml):
  distracted, focused, phone, book   (varía según versión del dataset)

USO:
  1. Instala las dependencias:     pip install roboflow ultralytics
  2. Pon tu API Key de Roboflow en .env  →  ROBOFLOW_API_KEY=xxxx  (o pásala como argumento)
  3. Ejecuta:  python train_yolo.py

El modelo entrenado quedará en:  runs/detect/sae_distracted/weights/best.pt
Cópialo a la raíz del proyecto como  distracted_model.pt  (automático al final).
"""

import os
import sys
import shutil
import argparse

# ─── Configuración ────────────────────────────────────────────
WORKSPACE     = "salman-yiavg"
PROJECT_ID    = "distracted-detection-2"
VERSION       = 1           # Cambia si hay versión más nueva en el proyecto
DATASET_DIR   = "./dataset_distracted"
MODEL_BASE    = "yolov8n.pt"   # nano = más rápido, menor VRAM
EPOCHS        = 40
IMG_SIZE      = 640
OUTPUT_NAME   = "sae_distracted"
OUTPUT_MODEL  = "distracted_model.pt"   # ruta destino en la raíz del proyecto


def get_api_key():
    """Busca la API Key en .env o en variable de entorno."""
    # 1. Intentar desde .env
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("ROBOFLOW_API_KEY"):
                    return line.split("=", 1)[1].strip().strip('"\'')
    # 2. Variable de entorno del sistema
    return os.environ.get("ROBOFLOW_API_KEY", "")


def download_dataset(api_key: str) -> str:
    """Descarga el dataset desde Roboflow en formato YOLOv8."""
    try:
        from roboflow import Roboflow
    except ImportError:
        print("[Train] Instala roboflow:  pip install roboflow")
        sys.exit(1)

    print(f"[Train] Conectando a Roboflow…  workspace={WORKSPACE}  project={PROJECT_ID}  v{VERSION}")
    rf = Roboflow(api_key=api_key)
    project = rf.workspace(WORKSPACE).project(PROJECT_ID)
    version = project.version(VERSION)
    dataset = version.download("yolov8", location=DATASET_DIR)
    yaml_path = os.path.join(DATASET_DIR, "data.yaml")
    if not os.path.exists(yaml_path):
        # Buscar recursivamente
        for root, _, files in os.walk(DATASET_DIR):
            for f in files:
                if f == "data.yaml":
                    yaml_path = os.path.join(root, f)
                    break
    print(f"[Train] Dataset descargado. data.yaml: {yaml_path}")
    return yaml_path


def print_classes(yaml_path: str):
    """Imprime las clases del dataset para confirmar."""
    try:
        import yaml
        with open(yaml_path) as f:
            data = yaml.safe_load(f)
        print(f"\n[Train] Clases detectadas en el dataset ({len(data.get('names', []))}):")
        for i, name in enumerate(data.get("names", [])):
            print(f"  [{i}] {name}")
        print()
    except Exception as e:
        print(f"[Train] No se pudo leer data.yaml: {e}")


def train(yaml_path: str):
    """Entrena el modelo YOLOv8 con el dataset descargado."""
    try:
        from ultralytics import YOLO
    except ImportError:
        print("[Train] Instala ultralytics:  pip install ultralytics")
        sys.exit(1)

    print(f"[Train] Iniciando entrenamiento…")
    print(f"        Modelo base : {MODEL_BASE}")
    print(f"        Épocas      : {EPOCHS}")
    print(f"        Img size    : {IMG_SIZE}")
    print(f"        Nombre run  : {OUTPUT_NAME}")

    model = YOLO(MODEL_BASE)
    results = model.train(
        data=yaml_path,
        epochs=EPOCHS,
        imgsz=IMG_SIZE,
        name=OUTPUT_NAME,
        project="runs/detect",
        exist_ok=True,
        patience=10,     # early stopping
        device=0 if _cuda_available() else "cpu",
        batch=8,
        workers=2,
        val=True,
        save=True,
        verbose=True,
    )
    return results


def _cuda_available() -> bool:
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def copy_best_model():
    """Copia best.pt a la raíz del proyecto como distracted_model.pt."""
    best = os.path.join("runs", "detect", OUTPUT_NAME, "weights", "best.pt")
    if os.path.exists(best):
        dest = os.path.join(os.path.dirname(__file__), OUTPUT_MODEL)
        shutil.copy2(best, dest)
        print(f"\n[Train] ✅ Modelo copiado a: {dest}")
        print("[Train] Actualiza SAE: en vision_yolo.py el modelo apuntará automáticamente a este archivo.")
        return dest
    else:
        print(f"[Train] ⚠  No se encontró best.pt en {best}")
        return None


def main():
    parser = argparse.ArgumentParser(description="Entrenamiento YOLO SAE")
    parser.add_argument("--api-key", default="", help="Roboflow API Key (o usa .env)")
    parser.add_argument("--epochs", type=int, default=EPOCHS)
    parser.add_argument("--skip-download", action="store_true",
                        help="No descargar dataset (usa ./dataset_distracted existente)")
    args = parser.parse_args()

    api_key = args.api_key or get_api_key()

    if not args.skip_download:
        if not api_key:
            print("\n[Train] ❌  Se necesita una Roboflow API Key.")
            print("  Opción 1: Agrégala al .env como  ROBOFLOW_API_KEY=tu_key")
            print("  Opción 2: Pásala como argumento  --api-key tu_key")
            print("  Obtén tu key en: https://app.roboflow.com/settings/api\n")
            sys.exit(1)
        yaml_path = download_dataset(api_key)
    else:
        yaml_path = os.path.join(DATASET_DIR, "data.yaml")
        if not os.path.exists(yaml_path):
            print(f"[Train] No se encontró {yaml_path}. Omite --skip-download para descargar.")
            sys.exit(1)

    print_classes(yaml_path)

    # Confirmar antes de entrenar
    print("═" * 55)
    print("  ¿Deseas iniciar el entrenamiento? (puede tardar 15–60 min)")
    print("  CPU mode si no tienes GPU compatible con CUDA.")
    print("═" * 55)
    resp = input("  Continuar? [s/N]: ").strip().lower()
    if resp not in ("s", "si", "sí", "y", "yes"):
        print("[Train] Entrenamiento cancelado.")
        sys.exit(0)

    train(yaml_path)
    model_dest = copy_best_model()

    if model_dest:
        print("\n✅  Entrenamiento completado.")
        print(f"   Modelo listo en: {model_dest}")
        print("   El sistema SAE cargará automáticamente este modelo al reiniciar.")
    else:
        print("\n⚠  Entrenamiento completado pero no se encontró best.pt.")


if __name__ == "__main__":
    main()
