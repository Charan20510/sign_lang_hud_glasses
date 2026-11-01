// Glasses display — receives words/sentences over UDP and shows them on the OLED.
// A word that fits is shown big (size 2) in the centre; longer text (a sentence) scrolls right-to-left
// on one line SCROLL_PASSES times, then the screen goes blank (a new packet interrupts at any time).
// Packet (docs/interface.md): {"text": "hello", "conf": 0.92}  on UDP port 4210, mDNS name glasses.local.
// 1. Copy secrets.h from ../tests/t4_wifi_udp/ (or secrets.h.example -> secrets.h), 2.4 GHz hotspot.
// 2. Board: ESP32C3 Dev Module, USB CDC On Boot: Enabled. Upload.
// 3. Laptop (same hotspot): python software/run.py --simulate
// Based on t4_wifi_udp (Wi-Fi + UDP) and t6_mirror_center (centring + mirror flags).

#include <WiFi.h>
#include <WiFiUdp.h>
#include <ESPmDNS.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "secrets.h"

#define MIRROR_X 0                // 1 = flip left/right (if the HUD optics mirror the text)
#define FLIP_Y   0                // 1 = flip upside down
#define SCROLL_PX_PER_S 60        // sentence scroll speed; must match SCROLL_PX_PER_S in software/run.py
#define FRAME_MS        20        // redraw interval while scrolling
#define SCROLL_PASSES   2         // scroll the sentence this many times, then blank; must match software/run.py

const int SDA_PIN = 8;
const int SCL_PIN = 9;
const uint8_t OLED_ADDR = 0x3C;
const int UDP_PORT = 4210;        // must match network.udp_port in config.yaml

Adafruit_SSD1306 display(128, 64, &Wire, -1);
WiFiUDP udp;
char packet[256];

String scrollText = "";           // text being scrolled ("" = nothing scrolling)
int scrollW = 0;                  // its width in pixels at text size 2
unsigned long scrollStart = 0;    // millis() when the scroll started
unsigned long lastFrame = 0;      // millis() of the last scroll redraw

// Print one line centred left-right at height y. Text size 1 char = 6x8 px, size 2 = 12x16 px.
void drawCentered(const String &line, int size, int y) {
  int16_t x1, y1;
  uint16_t w, h;
  display.setTextSize(size);
  display.getTextBounds(line, 0, 0, &x1, &y1, &w, &h);
  display.setCursor((display.width() - w) / 2, y);
  display.print(line);
}

// New text: fits on the screen -> static in the centre; wider than the screen -> start scrolling.
void showText(const String &text) {
  int16_t x1, y1;
  uint16_t w, h;
  display.setTextSize(2);
  display.getTextBounds(text, 0, 0, &x1, &y1, &w, &h);
  if (w <= display.width()) {
    scrollText = "";
    display.clearDisplay();
    drawCentered(text, 2, (display.height() - 16) / 2);
    display.display();
  } else {
    scrollText = text;
    scrollW = w;
    scrollStart = millis();
    lastFrame = 0;                               // draw the first frame right away
  }
}

// One scroll frame. The position comes from the time since the start, so the speed stays the same
// however long a redraw takes: text enters at the right edge, moves left, restarts once fully gone.
// After SCROLL_PASSES passes the screen is cleared and scrolling stops.
void scrollFrame() {
  unsigned long moved = (millis() - scrollStart) * SCROLL_PX_PER_S / 1000;
  unsigned long pass = scrollW + display.width();      // pixels for one full pass
  if (moved / pass >= SCROLL_PASSES) {
    scrollText = "";                                   // done: blank screen until the next packet
    display.clearDisplay();
    display.display();
    return;
  }
  int x = display.width() - (int)(moved % pass);
  display.clearDisplay();
  display.setTextSize(2);
  display.setCursor(x, (display.height() - 16) / 2);
  display.print(scrollText);
  display.display();
}

// Boot/status screen: big title in the middle, small detail line under it.
void showStatus(const String &title, const String &detail) {
  display.clearDisplay();
  drawCentered(title, 2, 16);
  drawCentered(detail, 1, 40);
  display.display();
}

// Pull the value of "text" out of {"text": "...", "conf": 0.9}.
// ponytail: naive string search (no escaped quotes); switch to ArduinoJson if the packet grows.
String jsonText(const String &s) {
  int k = s.indexOf("\"text\"");
  if (k < 0) return s;                       // not JSON -> show raw packet
  int a = s.indexOf('"', s.indexOf(':', k) + 1);
  int b = s.indexOf('"', a + 1);
  return (a < 0 || b < 0) ? s : s.substring(a + 1, b);
}

void setup() {
  Serial.begin(115200);
  Wire.begin(SDA_PIN, SCL_PIN);
  display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR);
  if (MIRROR_X) display.ssd1306_command(0xA0);   // segment remap off -> flips left/right
  if (FLIP_Y)   display.ssd1306_command(0xC0);   // COM scan normal -> flips upside down
  display.setTextColor(SSD1306_WHITE);
  display.setTextWrap(false);                    // long text runs off the edge (scrolls) instead of wrapping
  showStatus("WIFI...", WIFI_SSID);

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  WiFi.setTxPower(WIFI_POWER_8_5dBm);   // SuperMini antenna often fails at full power
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  String ip = WiFi.localIP().toString();
  Serial.println("\nIP: " + ip);
  MDNS.begin("glasses");                 // reachable as glasses.local
  udp.begin(UDP_PORT);
  showStatus("READY", ip);
}

void loop() {
  int len = udp.parsePacket();
  if (len > 0) {
    len = udp.read(packet, sizeof(packet) - 1);
    packet[len] = '\0';
    Serial.printf("got: %s\n", packet);
    showText(jsonText(String(packet)));
  }
  if (scrollText.length() && millis() - lastFrame >= FRAME_MS) {
    lastFrame = millis();
    scrollFrame();
  }
}
