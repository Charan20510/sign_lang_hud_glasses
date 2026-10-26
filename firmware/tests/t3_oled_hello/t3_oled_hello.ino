// Test 3 — does the OLED show text?
// Needs libraries: Adafruit SSD1306 + Adafruit GFX (Library Manager).
// Pass: big "HELLO" on top, small counter below that changes every second.
// Set MIRROR_X to 1 to check the mirrored (HUD reflection) view.

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define MIRROR_X 1

const int SDA_PIN = 8;
const int SCL_PIN = 9;
const uint8_t OLED_ADDR = 0x3C;   // change to 0x3D if Test 2 found 0x3D

Adafruit_SSD1306 display(128, 64, &Wire, -1);

void setup() {
  Serial.begin(115200);
  Wire.begin(SDA_PIN, SCL_PIN);
  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
    Serial.println("OLED init failed");
    while (true) delay(1000);
  }
  if (MIRROR_X) {
    display.ssd1306_command(0xA0);   // segment remap off -> flips left/right
  }
}

void loop() {
  static int n = 0;
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(2);
  display.setCursor(0, 0);
  display.println("HELLO");
  display.setTextSize(1);
  display.setCursor(0, 40);
  display.printf("count %d", n++);
  display.display();
  delay(1000);
}
