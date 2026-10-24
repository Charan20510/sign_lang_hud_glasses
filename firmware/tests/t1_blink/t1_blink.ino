// Test 1 — is the ESP32-C3 alive?
// Blinks the onboard LED (GPIO8, active-LOW on the SuperMini) and prints to Serial.
// Pass: LED blinks once per second AND Serial Monitor (115200) prints "alive N".
// Arduino IDE: board "ESP32C3 Dev Module", Tools > USB CDC On Boot = Enabled.

const int LED_PIN = 8;

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
}

void loop() {
  static int n = 0;
  digitalWrite(LED_PIN, LOW);   // LOW = LED on
  delay(500);
  digitalWrite(LED_PIN, HIGH);  // HIGH = LED off
  delay(500);
  Serial.printf("alive %d\n", n++);
}
