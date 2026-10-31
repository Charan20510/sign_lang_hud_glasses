// Glasses display — receives words/sentences over UDP and shows them centred on the OLED.
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

const int SDA_PIN = 8;
const int SCL_PIN = 9;
const uint8_t OLED_ADDR = 0x3C;
const int UDP_PORT = 4210;        // must match network.udp_port in config.yaml

Adafruit_SSD1306 display(128, 64, &Wire, -1);
WiFiUDP udp;
char packet[256];

// Print one line centred left-right at height y. Text size 1 char = 6x8 px, size 2 = 12x16 px.
void drawCentered(const String &line, int size, int y) {
  int16_t x1, y1;
  uint16_t w, h;
  display.setTextSize(size);
  display.getTextBounds(line, 0, 0, &x1, &y1, &w, &h);
  display.setCursor((display.width() - w) / 2, y);
  display.print(line);
}

// Word-wrap text into lines of at most `cols` characters.
// Returns the number of lines, or 0 if it needs more than maxLines (lines[] then holds the first maxLines).
int wrap(const String &text, int cols, String lines[], int maxLines) {
  int n = 0;
  String line = "";
  int i = 0;
  while (i < (int)text.length()) {
    int sp = text.indexOf(' ', i);
    if (sp < 0) sp = text.length();
    String word = text.substring(i, sp);
    i = sp + 1;
    if (word.length() == 0) continue;
    while ((int)word.length() > cols) {        // word longer than a line: cut it
      if (line.length()) {
        if (n == maxLines) return 0;
        lines[n++] = line;
        line = "";
      }
      if (n == maxLines) return 0;
      lines[n++] = word.substring(0, cols);
      word = word.substring(cols);
    }
    if (line.length() == 0) {
      line = word;
    } else if ((int)(line.length() + 1 + word.length()) <= cols) {
      line += " " + word;
    } else {
      if (n == maxLines) return 0;
      lines[n++] = line;
      line = word;
    }
  }
  if (line.length()) {
    if (n == maxLines) return 0;
    lines[n++] = line;
  }
  return n;
}

// Show text in the middle of the screen: size 2 (10 chars x 4 lines) if it fits, else size 1 (21 x 8).
void showCentered(const String &text) {
  String lines[8];
  int size = 2;
  int n = wrap(text, 10, lines, 4);
  if (n == 0) {
    size = 1;
    n = wrap(text, 21, lines, 8);
    if (n == 0) n = 8;                         // still too long: show the first 8 lines
  }
  int lineH = 8 * size;
  int y = (display.height() - n * lineH) / 2;
  display.clearDisplay();
  for (int k = 0; k < n; k++) drawCentered(lines[k], size, y + k * lineH);
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
  display.setTextWrap(false);                    // wrap() does the line breaks
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
    showCentered(jsonText(String(packet)));
  }
}
