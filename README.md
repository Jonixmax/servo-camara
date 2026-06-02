# 🤌 Gesture Servo ESP32

Controla un servo motor con gestos de tu mano usando la webcam de tu PC y MediaPipe GestureRecognizer.

```
[Webcam] → Python + MediaPipe → Serial USB → ESP32 → Servo SG90
```

---

## 📦 Archivos del proyecto

```
servo/
├── gesture_detector_pc.py   # Script Python para la PC
├── gesture_servo_esp32.ino  # Firmware para el ESP32
└── README.md
```

---

## 🛒 Materiales

| Componente     | Detalles                        |
|----------------|---------------------------------|
| ESP32          | Cualquier variante DevKit       |
| Servo motor    | SG90 o MG90S                    |
| Cable USB      | Comunicación serial con la PC   |
| PC con cámara  | Python 3.13+                    |

---

## 🔌 Conexión del servo

```
Servo           ESP32
──────────────────────
ROJO   (VCC) →  VIN  (5V desde USB)
MARRÓN (GND) →  GND
NARANJA (SIG) → GPIO 13
```

> ⚠️ Si el servo vibra o el ESP32 se reinicia, aliméntalo con una fuente externa de 5V compartiendo GND con el ESP32.

---

## ⚙️ Instalación del firmware (ESP32)

### Librería necesaria

Instala desde el **Gestor de librerías** de Arduino IDE:
- `ESP32Servo`

### Subir el sketch

1. Abre `gesture_servo_esp32.ino` en Arduino IDE.
2. Selecciona tu placa ESP32 y el puerto correcto.
3. Sube el sketch.

---

## 🐍 Instalación del script (PC)

```bash
pip install opencv-python mediapipe pyserial
```

> **Nota:** Compatible con **Python 3.13**. En la primera ejecución se descargará el modelo de gestos automáticamente (~25MB). Si falla la descarga automática, descárgalo manualmente desde:
> `https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task`
> y guárdalo en `C:\Users\TU_USUARIO\.mediapipe_models\gesture_recognizer.task`

---

## ▶️ Uso

```bash
# Windows
python gesture_detector_pc.py --port COM4 --cam 1
```

> **Nota sobre la cámara:** Si tienes OBS u otro software de cámara virtual activo, puede ocupar el índice 0. Usa `--cam 1` para tu webcam real, o cierra OBS antes de ejecutar.

### Parámetros

| Parámetro | Default  | Descripción               |
|-----------|----------|---------------------------|
| `--port`  | —        | Puerto serial (requerido) |
| `--cam`   | `0`      | Índice de la cámara       |
| `--baud`  | `115200` | Velocidad serial          |

Presiona **`Q`** para cerrar.

---

## 🤚 Gestos y ángulos

| Gesto | Símbolo | Ángulo servo |
|-------|---------|:------------:|
| Thumb_Up | 👍 | 0° |
| Open_Palm | 🖐️ | 45° |
| Victory | ✌️ | 90° |
| Pointing_Up | ☝️ | 135° |
| Thumb_Down | 👎 | 180° |
| ILoveYou | 🤟 | 180° |
| Closed_Fist | ✊ | Sin cambio |

---

## 🛠️ Solución de problemas

| Síntoma | Solución |
|---------|----------|
| Servo no se mueve | Verifica GPIO 13 y que la librería ESP32Servo esté instalada |
| Servo vibra | Aliméntalo con fuente externa de 5V |
| Cámara muestra pantalla negra u OBS | Cierra OBS o usa `--cam 1` |
| Error al cargar mediapipe | Verifica que usas Python 3.13 y `pip install mediapipe` |
| Modelo no descarga | Descárgalo manualmente (ver sección instalación) |
| Gestos no se detectan | Mejora la iluminación y centra la mano en la cámara |

---

## 📄 Licencia

MIT — libre para usar, modificar y distribuir.
