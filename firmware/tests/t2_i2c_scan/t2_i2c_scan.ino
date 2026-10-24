// Test 2 — can the ESP32-C3 see the OLED on the I2C bus?
// Wiring: OLED VCC->3V3, GND->GND, SDA->GPIO8, SCL->GPIO9.
// Pass: Serial prints "found device at 0x3C" (some boards use 0x3D).

#include <Wire.h>

const int SDA_PIN = 8;
const int SCL_PIN = 9;

void setup() {
  Serial.begin(115200);
  delay(1000);                  // give USB serial time to connect
  Wire.begin(SDA_PIN, SCL_PIN);
}

void loop() {
  int found = 0;
  for (byte addr = 1; addr < 127; addr++) {
    Wire.beginTransmission(addr);
    if (Wire.endTransmission() == 0) {   // 0 = a device answered
      Serial.printf("found device at 0x%02X\n", addr);
      found++;
    }
  }
  if (found == 0) Serial.println("no I2C devices - check wiring");
  Serial.println("---");
  delay(3000);
}
