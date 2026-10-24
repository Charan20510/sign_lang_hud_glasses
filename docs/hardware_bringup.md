# Hardware bring-up — test every part before building the glasses

Branch: `testout`. Do the steps in order. Each one has a pass/fail check.
Write your result in the table at the bottom and in today's `docs/handoff/YYYY-MM-DD.md`.

Do **not** connect any LiPo during these tests (batteries haven't arrived, and the TP4056 needs a mod first — see Step 7).

## Step 1 — Visual check + multimeter basics
**Goal:** spot damaged parts; learn the 2 meter modes you'll use.
1. Look at each board: no cracked chips, bent pins, burnt marks. OLED glass not cracked.
2. Multimeter **continuity** (diode/beep symbol): touch both probes together → beep. That's your "is it connected?" test.
3. Multimeter **DC volts** (V⎓, 20 V range): plug the ESP32-C3 into the Mac with the Type-C cable. Black probe on a `G` pin, red on `5V` → ~5.0 V. Red on `3V3` → ~3.3 V.

**Pass:** beep works, 5V ≈ 4.8–5.2 V, 3V3 ≈ 3.2–3.4 V. (Pins aren't soldered yet — just touch the pads gently.)

## Step 2 — Solder headers (ESP32-C3 #1 only; keep #2 as a spare)
**Goal:** straight, clean header pins so the board fits the breadboard.
1. Snap two 8-pin pieces off the 40×1 / 40×2 male berg strip (SuperMini has 2 rows of 8).
2. Push them into the breadboard (long side down), lay the ESP32-C3 on top, components facing up. The breadboard holds them straight.
3. Iron at ~330 °C, a little flux. Touch iron to pad + pin together 1 s, feed solder, remove solder, then iron. Shiny cone = good; ball = reheat.
4. OLED: if its 4 pins aren't already soldered, do the same.
5. Continuity check every **neighbouring** pin pair → must **not** beep (no solder bridges).

**Pass:** all pins shiny cones, no beep between neighbours.

## Step 3 — ESP32-C3 alive (`firmware/tests/t1_blink`)
**Setup once:**
- Install Arduino IDE 2. Boards Manager → install **esp32 by Espressif Systems**.
- Tools → Board: **ESP32C3 Dev Module**. Tools → **USB CDC On Boot: Enabled** (otherwise Serial prints nothing).
- Port: `/dev/cu.usbmodem…` (no driver needed — the C3 has native USB).

Open `t1_blink.ino` → Upload → Serial Monitor at 115200.

**Pass:** blue LED blinks every second, Serial shows `alive 0, alive 1, …`.
**If upload fails:** hold **BOOT**, tap **RST**, release BOOT, upload again. Try another cable (some are charge-only).

## Step 4 — OLED (`t2_i2c_scan`, then `t3_oled_hello`)
Wiring on the breadboard (USB still powers everything):

| OLED pin | ESP32-C3 pin |
|---|---|
| VCC | 3V3 |
| GND | G |
| SDA | GPIO8 |
| SCL | GPIO9 |

1. Upload `t2_i2c_scan`. **Pass:** Serial shows `found device at 0x3C`. (If it shows `0x3D`, change `OLED_ADDR` in the next sketches.)
2. Libraries: Library Manager → install **Adafruit SSD1306** (accept Adafruit GFX too).
3. Upload `t3_oled_hello`. **Pass:** big `HELLO` + counter ticking.
4. Set `MIRROR_X 1`, upload, look at the OLED in a mirror → text should read normally. (That's what the HUD reflection needs.)
5. Swap in OLED #2 and repeat 1+3.

**If "no I2C devices":** SDA/SCL swapped, loose jumper, or VCC on 5V by mistake.

## Step 5 + 6 — Wi-Fi + UDP link (`t4_wifi_udp` + `tools/send_test.py`)
1. Phone hotspot must be **2.4 GHz** (iPhone: Settings → Personal Hotspot → **Maximize Compatibility ON**).
2. In `firmware/tests/t4_wifi_udp/` copy `secrets.h.example` → `secrets.h`, fill SSID/password. (`secrets.h` is gitignored — never commit it.)
3. Upload. OLED shows `WIFI...` then `READY` + the IP (e.g. `172.20.10.5`).
4. Connect the Mac to the same hotspot, then:
   ```
   venv/bin/python tools/send_test.py --host <IP-from-OLED> --text hello
   venv/bin/python tools/send_test.py --text hello          # uses glasses.local
   venv/bin/python tools/send_test.py --host <IP>           # interactive, type words
   ```
**Pass:** `hello` appears on the OLED within ~0.5 s; `glasses.local` also works.
**If stuck on WIFI...:** wrong password, 5 GHz hotspot, or move closer (the SuperMini antenna is weak; the sketch already lowers TX power, which helps).
**If IP works but glasses.local doesn't:** fine for now — use the IP; note it in Issues.

## Step 7 — TP4056 + slide switch (USB only, NO LiPo)
**TP4056 board pins:** `IN+/IN−` (or Type-C), `B+/B−` (battery), `OUT+/OUT−` (load).
1. Plug Type-C into TP4056 #1. LEDs: with no battery, red/blue may flicker or both glow — that's normal.
2. Meter DC volts on `B+`/`B−` → about **4.2 V** (may wander without a battery).
3. `OUT+`/`OUT−`: may read ~4.2 V or 0 V without a battery (the protection chip needs a cell) — not a failure.
4. Repeat for TP4056 #2.
5. Slide switch: continuity between **middle** pin and one side pin; flip → beeps on the other side. Test all 3.

**Pass:** B+ ≈ 4.1–4.25 V on both boards; every switch beeps middle↔side and swaps when flipped.

**Before the LiPos arrive (safety):** the TP4056 charges at **1 A** (PROG resistor `R3`, marked `122` = 1.2 kΩ). Your LiPo is 500 mAh → 1 A is 2C, too much. Change it to **~2.4 kΩ (≈ 500 mA)**: desolder the `122` SMD resistor and solder a 2.2–2.4 kΩ resistor between the PROG pad and GND (a through-hole one is easier). Measure it with the meter (Ω mode) before use.

## Results
| # | Part | Test | Result (✅/❌ + note) | Date |
|---|---|---|---|---|
| 1 | ESP32-C3 #1 | 5V/3V3 volts, blink + serial | | |
| 2 | ESP32-C3 #2 (spare) | 5V/3V3 volts, blink + serial | | |
| 3 | OLED #1 | I2C 0x3C, HELLO, mirror | | |
| 4 | OLED #2 | I2C 0x3C, HELLO | | |
| 5 | Wi-Fi + UDP | `send_test.py` text on OLED, IP + glasses.local | | |
| 6 | TP4056 #1 | B+ ≈ 4.2 V | | |
| 7 | TP4056 #2 | B+ ≈ 4.2 V | | |
| 8 | Slide switch ×3 | continuity swap | | |
| 9 | Type-C cable | data (upload works) | | |
| 10 | Breadboard / jumpers | used in steps 4–6 without faults | | |
