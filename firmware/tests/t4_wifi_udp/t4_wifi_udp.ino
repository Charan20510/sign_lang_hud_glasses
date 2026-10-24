// Test 4 — Wi-Fi + UDP: text typed on the laptop appears on the OLED.
// 1. Copy secrets.h.example -> secrets.h, fill hotspot name/password (2.4 GHz!).
// 2. Upload. OLED shows the IP address.
// 3. Laptop (same hotspot): python tools/send_test.py --host <IP> --text hello
// Pass: "hello" appears on the OLED. Also try --host glasses.local (mDNS).

#include <WiFi.h>
#include <WiFiUdp.h>
#include <ESPmDNS.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include "secrets.h"

const int SDA_PIN = 8;
const int SCL_PIN = 9;
const uint8_t OLED_ADDR = 0x3C;
const int UDP_PORT = 4210;        // must match network.udp_port in config.yaml

Adafruit_SSD1306 display(128, 64, &Wire, -1);
WiFiUDP udp;
char packet[256];

void show(const String &big, const String &small) {
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(2);
  display.setCursor(0, 0);
  display.println(big);
  display.setTextSize(1);
  display.setCursor(0, 48);
  display.println(small);
  display.display();
}

// Pull the value of "text" out of {"text": "...", "conf": 0.9}.
// ponytail: naive string search, fine for this test; final firmware can use ArduinoJson.
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
  show("WIFI...", WIFI_SSID);

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
  show("READY", ip);
}

void loop() {
  int len = udp.parsePacket();
  if (len > 0) {
    len = udp.read(packet, sizeof(packet) - 1);
    packet[len] = '\0';
    Serial.printf("got: %s\n", packet);
    show(jsonText(String(packet)), "from " + udp.remoteIP().toString());
  }
}
