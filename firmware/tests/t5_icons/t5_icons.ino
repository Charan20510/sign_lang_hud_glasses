// Test 5 (for fun) — show your own image2cpp bitmap(s) on the OLED.
// Needs libraries: Adafruit SSD1306 + Adafruit GFX (Library Manager).
//
// HOW TO USE A NEW IMAGE
//   1. image2cpp: Code output format "Arduino code", Draw mode "Horizontal - 1 bit per pixel".
//   2. Paste the whole output into bitmap.h (below the PASTE line, replacing the old one).
//   3. Copy the size from image2cpp's first comment ("// 'name', 960x1280px") into BMP_W / BMP_H below.
//   4. Upload.

// ======================= CHANGE THESE =======================
#define BMP_W      960     // image width  in px (from image2cpp comment)
#define BMP_H      1280    // image height in px (from image2cpp comment)
#define INVERT     0       // 1 = swap black/white (if it looks like a negative)
#define SHOW_MS    3000    // ms per image when bitmap.h holds several
#define SDA_PIN    8       // ESP32-C3 SuperMini I2C pins
#define SCL_PIN    9
#define OLED_ADDR  0x3C
// ============================================================

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "bitmap.h"

const int SCREEN_W = 128;
const int SCREEN_H = 64;

Adafruit_SSD1306 display(SCREEN_W, SCREEN_H, &Wire, -1);

// Nearest-neighbour shrink of a 1-bit bitmap (rows padded to whole bytes) to fit the screen,
// keeping its shape, centred.
void drawFitted(const unsigned char *bmp, int srcW, int srcH) {
  int dstW, dstH;
  if (srcW * SCREEN_H > srcH * SCREEN_W) {   // wider than the screen: width limits
    dstW = SCREEN_W;
    dstH = srcH * SCREEN_W / srcW;
  } else {                                   // taller: height limits
    dstH = SCREEN_H;
    dstW = srcW * SCREEN_H / srcH;
  }
  int x0 = (SCREEN_W - dstW) / 2;
  int y0 = (SCREEN_H - dstH) / 2;
  int bytesPerRow = (srcW + 7) / 8;

  for (int y = 0; y < dstH; y++) {
    int sy = y * srcH / dstH;
    for (int x = 0; x < dstW; x++) {
      int sx = x * srcW / dstW;
      uint8_t b = pgm_read_byte(&bmp[sy * bytesPerRow + sx / 8]);
      bool on = b & (0x80 >> (sx & 7));
      if (on != INVERT) display.drawPixel(x0 + x, y0 + y, SSD1306_WHITE);
    }
  }
}

void setup() {
  Serial.begin(115200);
  Wire.begin(SDA_PIN, SCL_PIN);   // C3 SuperMini: must set pins, defaults differ
  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
    Serial.println("OLED init failed");
    while (true) delay(1000);
  }
}

void loop() {
  for (int i = 0; i < epd_bitmap_allArray_LEN; i++) {
    display.clearDisplay();
    drawFitted(epd_bitmap_allArray[i], BMP_W, BMP_H);
    display.display();
    delay(SHOW_MS);
  }
}
