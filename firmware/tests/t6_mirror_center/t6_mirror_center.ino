// Test 6 — mirrored text in the centre of the OLED (HUD reflection view).
// Needs libraries: Adafruit SSD1306 + Adafruit GFX (Library Manager).
// Pass: TEXT sits in the middle of the screen, back-to-front on the OLED,
// and reads normally when you look at it in a mirror / through the acrylic.
// MIRROR_X flips left/right, FLIP_Y flips upside down (try both in Step 12).

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define MIRROR_X 0
#define FLIP_Y   0

const char *TEXT = "HELLO";
const uint8_t TEXT_SIZE = 2;      // 1 = small, 2 = medium, 3 = big (HELLO fits up to 4)

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
  if (FLIP_Y) {
    display.ssd1306_command(0xC0);   // COM scan normal -> flips upside down
  }

  // Centre: measure the text, then start at (screen - text) / 2.
  int16_t x1, y1;
  uint16_t w, h;
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(TEXT_SIZE);
  display.getTextBounds(TEXT, 0, 0, &x1, &y1, &w, &h);
  display.setCursor((display.width() - w) / 2, (display.height() - h) / 2);
  display.print(TEXT);
  display.display();
  Serial.printf("'%s' %ux%u px, mirror_x=%d flip_y=%d\n", TEXT, w, h, MIRROR_X, FLIP_Y);
}

void loop() {}
