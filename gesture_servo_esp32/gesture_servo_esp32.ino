/*
 * gesture_servo_esp32.ino
 * =======================
 * Recibe un ángulo (0-180) por Serial desde la PC
 * y mueve un servo suavemente a esa posición.
 *
 * Librería necesaria:
 *   - ESP32Servo (instalar desde el Gestor de librerías)
 *
 * Conexión del servo:
 *   Servo ROJO   → 5V  (o VIN si alimentas por USB)
 *   Servo MARRÓN → GND
 *   Servo NARANJA → GPIO 13 (señal PWM)
 *
 * El servo se mueve suavemente con interpolación para
 * evitar movimientos bruscos.
 */

#include <ESP32Servo.h>

// ── CONFIG ────────────────────────────────────────────────────────────────
#define SERVO_PIN     13      // Pin de señal del servo
#define SERVO_MIN_US  500     // Pulso mínimo en microsegundos
#define SERVO_MAX_US  2400    // Pulso máximo en microsegundos
#define SMOOTH_STEP   3       // Grados por paso de interpolación (velocidad)
#define SMOOTH_DELAY  10      // ms entre cada paso

// ── Variables ─────────────────────────────────────────────────────────────
Servo myServo;
int currentAngle = 90;   // Posición inicial
int targetAngle  = 90;

// ─────────────────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);

  // Asigna el timer PWM al servo
  ESP32PWM::allocateTimer(0);
  myServo.setPeriodHertz(50);
  myServo.attach(SERVO_PIN, SERVO_MIN_US, SERVO_MAX_US);

  // Posición central al inicio
  myServo.write(currentAngle);
  delay(500);

  Serial.println("=== Gesture Servo ESP32 listo ===");
  Serial.println("Esperando angulos (0-180) por Serial...");
}

// ─────────────────────────────────────────────────────────────────────────
// Mueve el servo suavemente desde currentAngle hasta target
void smoothMove(int target) {
  target = constrain(target, 0, 180);

  while (currentAngle != target) {
    if (currentAngle < target) {
      currentAngle = min(currentAngle + SMOOTH_STEP, target);
    } else {
      currentAngle = max(currentAngle - SMOOTH_STEP, target);
    }
    myServo.write(currentAngle);
    delay(SMOOTH_DELAY);
  }
}

// ─────────────────────────────────────────────────────────────────────────
void loop() {
  // Leer ángulo desde Serial
  if (Serial.available()) {
    String msg = Serial.readStringUntil('\n');
    msg.trim();

    if (msg.length() > 0) {
      int angle = msg.toInt();

      // Validar rango
      if (angle >= 0 && angle <= 180) {
        targetAngle = angle;
        Serial.print("Moviendo a: ");
        Serial.print(targetAngle);
        Serial.println("°");
        smoothMove(targetAngle);
        Serial.println("OK");
      } else {
        Serial.println("ERROR: angulo fuera de rango (0-180)");
      }
    }
  }
}
