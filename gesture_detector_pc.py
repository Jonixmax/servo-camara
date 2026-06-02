"""
gesture_detector_pc.py
======================
Usa mediapipe.tasks GestureRecognizer (Python 3.13 compatible).
Descarga el modelo gesture_recognizer.task automaticamente.

Gestos reconocidos → ángulo servo:
  None / Closed_Fist → sin cambio
  Thumb_Up           → 0°
  Open_Palm          → 45°
  Victory            → 90°
  Pointing_Up        → 135°
  Thumb_Down         → 180°
  ILoveYou           → 180°

Dependencias:
    pip install opencv-python mediapipe pyserial
"""

import cv2
import serial
import time
import argparse
import sys
import os
import urllib.request
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

# ── Mapeo gesto → ángulo ──────────────────────────────────────────────────
GESTURE_TO_ANGLE = {
    "Thumb_Up":    0,
    "Open_Palm":   45,
    "Victory":     90,
    "Pointing_Up": 135,
    "Thumb_Down":  180,
    "ILoveYou":    180,
}

GESTURE_COLORS = {
    "Thumb_Up":    (0, 120, 255),
    "Open_Palm":   (0, 220, 180),
    "Victory":     (0, 255, 80),
    "Pointing_Up": (255, 180, 0),
    "Thumb_Down":  (255, 60, 120),
    "ILoveYou":    (200, 0, 255),
    "Closed_Fist": (100, 100, 100),
    "None":        (60, 60, 60),
}

# Conexiones para dibujar la mano manualmente
HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (0,9),(9,10),(10,11),(11,12),
    (0,13),(13,14),(14,15),(15,16),
    (0,17),(17,18),(18,19),(19,20),
    (5,9),(9,13),(13,17),
]

# ─────────────────────────────────────────────────────────────────────────
class SerialSender:
    def __init__(self, port, baud=115200):
        try:
            self.conn = serial.Serial(port, baud, timeout=1)
            time.sleep(2)
            print(f"[Serial] Conectado a {port} @ {baud} baud")
        except serial.SerialException as e:
            print(f"[ERROR Serial] {e}")
            sys.exit(1)

    def send(self, value: str):
        self.conn.write(f"{value}\n".encode())

    def close(self):
        self.conn.close()


# ─────────────────────────────────────────────────────────────────────────
def get_model():
    model_dir  = os.path.join(os.path.expanduser("~"), ".mediapipe_models")
    model_path = os.path.join(model_dir, "gesture_recognizer.task")
    os.makedirs(model_dir, exist_ok=True)

    if not os.path.exists(model_path):
        url = ("https://storage.googleapis.com/mediapipe-models/"
               "gesture_recognizer/gesture_recognizer/float16/1/"
               "gesture_recognizer.task")
        print("[INFO] Descargando modelo gesture_recognizer (~25MB)...")
        try:
            urllib.request.urlretrieve(url, model_path)
            print("[INFO] Modelo descargado.")
        except Exception as e:
            print(f"[ERROR] No se pudo descargar: {e}")
            print("[INFO] Descarga manual desde:")
            print(f"       {url}")
            print(f"       Guárdalo en: {model_path}")
            sys.exit(1)
    return model_path


def draw_hand(frame, landmarks, w, h, color):
    pts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
    for a, b in HAND_CONNECTIONS:
        cv2.line(frame, pts[a], pts[b], color, 2)
    for pt in pts:
        cv2.circle(frame, pt, 4, (255, 255, 255), -1)
        cv2.circle(frame, pt, 3, color, -1)


def draw_overlay(frame, gesture, angle, fps):
    h, w = frame.shape[:2]
    color = GESTURE_COLORS.get(gesture, (200, 200, 200))

    # Barra de ángulo
    bx = 30
    bh = int((angle / 180) * 200)
    cv2.rectangle(frame, (bx, h - 50), (bx + 25, h - 250), (40, 40, 40), -1)
    cv2.rectangle(frame, (bx, h - 50 - bh), (bx + 25, h - 50), color, -1)
    cv2.putText(frame, f"{angle}deg", (bx - 5, h - 260),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # HUD superior
    cv2.rectangle(frame, (0, 0), (w, 50), (20, 20, 20), -1)
    cv2.putText(frame, f"Gesto: {gesture}", (10, 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    cv2.putText(frame, f"Servo: {angle}deg   FPS: {fps:.1f}", (10, 44),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    return frame


# ─────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", required=True)
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--cam",  type=int, default=0)
    args = parser.parse_args()

    sender     = SerialSender(args.port, args.baud)
    model_path = get_model()

    options = mp_vision.GestureRecognizerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=model_path),
        running_mode=mp_vision.RunningMode.VIDEO,
        num_hands=1,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5,
    )

    cap = cv2.VideoCapture(args.cam, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(args.cam)
    if not cap.isOpened():
        print(f"[ERROR] No se pudo abrir la cámara {args.cam}")
        sys.exit(1)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    last_gesture  = "None"
    current_angle = 90
    last_send     = 0
    t_prev        = time.time()
    frame_ms      = 0

    print("\n[INFO] Gestos disponibles:")
    for g, a in GESTURE_TO_ANGLE.items():
        print(f"         {g:15} → {a}°")
    print("\n[INFO] Presiona 'q' para salir.\n")

    with mp_vision.GestureRecognizer.create_from_options(options) as recognizer:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame  = cv2.flip(frame, 1)
            h, w   = frame.shape[:2]
            t_now  = time.time()
            fps    = 1.0 / max(t_now - t_prev, 1e-6)
            t_prev = t_now
            frame_ms += int(1000 / max(fps, 1))

            rgb      = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
            result   = recognizer.recognize_for_video(mp_image, frame_ms)

            gesture = "None"

            if result.gestures and result.hand_landmarks:
                gesture = result.gestures[0][0].category_name
                color   = GESTURE_COLORS.get(gesture, (200, 200, 200))
                draw_hand(frame, result.hand_landmarks[0], w, h, color)

                if gesture != last_gesture and t_now - last_send >= 0.25:
                    if gesture in GESTURE_TO_ANGLE:
                        current_angle = GESTURE_TO_ANGLE[gesture]
                        sender.send(str(current_angle))
                        print(f"[GESTO] {gesture} → {current_angle}°")
                    last_gesture = gesture
                    last_send    = t_now

            frame = draw_overlay(frame, gesture, current_angle, fps)
            cv2.imshow("Gesture Control → ESP32 Servo", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()
    sender.close()
    print("[INFO] Detenido.")


if __name__ == "__main__":
    main()