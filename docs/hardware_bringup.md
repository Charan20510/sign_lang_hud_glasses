# Hardware bring-up — test every part before building the glasses

**Printable step-by-step guide with diagrams:** [hardware_bringup.pdf](hardware_bringup.pdf) (source `docs/guide/bringup.html`, rebuild with `sh docs/guide/build_pdf.sh`).

Branch: `testout`. Do the steps in order. Each one has a pass/fail check.
Write your result in the table at the bottom and in today's `docs/handoff/YYYY-MM-DD.md`.

Steps 1–11 ✅ (done by 2026-10-31). Next: Step 12 optics bench + measurements for printing. Charging = bench DC supply only (Step 8).

**Never plug USB into a TP4056 that has a LiPo on it** (stock board = 1 A, too much for 600 mAh). Never hold battery wires on the pads by hand — solder them (Step 9).

## Step 1 — Visual check + multimeter basics
**Goal:** spot damaged parts; learn the 2 meter modes you'll use.
1. Look at each board: no cracked chips, bent pins, burnt marks. OLED glass not cracked.
2. Multimeter **continuity** (diode/beep symbol): touch both probes together → beep. That's your "is it connected?" test.
3. Multimeter **DC volts** (V⎓, 20 V range): plug the ESP32-C3 into the Mac with the Type-C cable. Black probe on a `G` pin, red on `5V` → ~5.0 V. Red on `3V3` → ~3.3 V.

**Pass:** beep works, 5V ≈ 4.8–5.2 V, 3V3 ≈ 3.2–3.4 V. (No pins yet — just touch the pads gently.)

## Step 2 — No-solder breadboard setup (friction-fit)
**Goal:** sit the ESP32-C3 on the breadboard without soldering. Soldering comes last (see "Final build").
The SuperMini has bare holes, so it needs pins under it to reach the breadboard.
1. Break two 8-pin pieces off the male berg strip.
2. Push both pieces into the breadboard, long side down, one on each side of the middle gap. Spacing = the ESP32-C3's two rows of holes.
3. Press ESP32-C3 #1 down onto the pins (USB-C port pointing out of the breadboard edge).
4. Tilt it very slightly so the pins press against the sides of the holes.
5. OLED: if its 4 pins are already soldered, it plugs straight in. If they're loose, use the same trick.

**Pass:** Step 3 (`t1_blink`) uploads and runs while the board sits on the pins.
**Tip:** random resets, upload errors or "no I2C devices" → press the board down first, before debugging code.

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
**LiPo already on a charger (red LED)?** Unplug USB, take the wires off the pads, keep red/black apart. Warm or puffy cell → set aside on a tile, don't use it.

**TP4056 board pins:** `IN+/IN−` (or Type-C), `B+/B−` (battery), `OUT+/OUT−` (load).
1. Plug Type-C into TP4056 #1. LEDs: with no battery, red/blue may flicker or both glow — that's normal.
2. Meter DC volts on `B+`/`B−` → about **4.2 V** (may wander without a battery).
3. `OUT+`/`OUT−`: may read ~4.2 V or 0 V without a battery (the protection chip needs a cell) — not a failure.
4. Repeat for TP4056 #2.
5. Slide switch: continuity between **middle** pin and one side pin; flip → beeps on the other side. Test all 3. The 2 end tabs are mounting only (not wired) — bend/cut if in the way.

**Pass:** B+ ≈ 4.1–4.25 V on both boards; every switch beeps middle↔side and swaps when flipped.

## Step 8 — Charge the LiPo with the bench DC supply (no R3 mod)
Only when the cell is below ~3.9 V. Only a lab supply with **both V and A knobs** — never a phone adapter / fixed 5 V / USB straight to the cell.
1. Leads off the battery: set **4.20 V** (check with meter: 4.18–4.20 V). Short the leads, set the limit to **0.30 A** (never > 0.6 A).
2. OUTPUT OFF → red → battery red (or B+), black → black (or B−) → OUTPUT ON. Shows ~0.30 A (CC).
3. Cell on a tile, stay next to it, touch every 10 min; warm → OUTPUT OFF, stop.
4. Current drops in CV; at **0.03–0.05 A** → OUTPUT OFF, unclip. Rest 5 min → 4.15–4.20 V.
5. Below 3.0 V: start at 0.05 A until it passes 3.0 V.

**Pass:** current tapered, 4.15–4.20 V, never warm.
Optional later (USB charging via TP4056): replace R3 `122` (1.2 kΩ = 1 A) with 2.2–2.4 kΩ (≈ 500 mA).

## Step 9 — Solder battery wires to the TP4056
1. LiPo volts (wire ends apart): 3.0–4.2 V OK; < 3.0 V → bench charge first (Step 8). Cell flat, not puffy.
2. Solder **one wire at a time**: red → **B+**, black → **B−**. Never hand-held. Re-check polarity. Tape the joints.
3. Tape over the TP4056 USB-C port, write **NO USB**. OUT+/OUT− ≈ battery voltage.
4. To charge later: cell stays soldered, clip the bench supply to B+/B− (Step 8). Repeat for LiPo #2 / TP4056 #2.

**Pass:** both cells soldered + taped, USB ports taped.

## Step 10 — ESP32-C3 on battery
Wiring: `OUT+` → switch middle, switch side → ESP32-C3 **5V**; `OUT−` → **G**. OLED as Step 4.
**Never plug the ESP32 USB-C while the switch is ON. TP4056 USB stays taped.**
1. Switch ON → `WIFI...` → `READY` + IP (`t4_wifi_udp`). 3V3 pin ≈ 3.3 V. (5V pin = battery voltage on battery, 3.7–4.2 V — normal.)
2. `venv/bin/python tools/send_test.py --host <IP> --text battery` → word on OLED. Switch OFF/ON works.
3. Runtime: full cell, note hours until the OLED goes off. Recharge with the bench supply (Step 8).

**Pass:** works on battery, switch toggles it, runtime noted.
**If 0 V on OUT:** touch the bench supply (4.20 V, 0.3 A) to B+/B− for 2 s to wake the protection chip.

## Step 11 — Leftover checks
ESP32-C3 #2 `t1_blink`; OLED #2 `t2_i2c_scan` + `t3_oled_hello`; OLED #1 `MIRROR_X 1` mirror check; `send_test.py --text hello` via `glasses.local`.

## Step 12 — Optics bench test + measurements for printing
No mirror: OLED (screen down) → lens 22 mm → acrylic 45° 25 mm → eye. Fill-in sheet: [step12_measure.pdf](step12_measure.pdf) (source `docs/guide/step12_measure.html`).
1. `t3_oled_hello` on USB. Slide the OLED until the text through the lens is sharpest; note u (bench: 22 mm works).
2. Acrylic at 45° ~25 mm behind the lens → text floats in view. Backwards/upside down → flip `MIRROR_X` / rotation.
3. Write down every number below; they go into `hardware/enclosure/hud_enclosure.scad` before printing.

| # | Measure (mm) | Variable |
|---|---|---|
| O1 | Best focus u: OLED screen → lens centre | `d_oled_lens = u` (slots at u − 3 / u / u + 3) |
| O2–O4 | Sharp with acrylic at 25? / `MIRROR_X` / readable in room light? | checks |
| O5 | Lens real focal length (project a window onto paper) | explains u = 22 |
| Acrylic | L × W × thickness (width 29–30.4) | `acr_t` |
| Lens | diameter, centre thickness | `lens_d`, `lens_t` |
| OLED | PCB W × L × thickness, glass thickness, glass start/end along the PCB | `oled_*`, `oled_glass_x` |
| TP4056 / ESP32-C3 / switch / LiPo | L × W × H (tallest part) | `tp`, `tp_h`, `esp`, `pcb_t`, `sw_body`, `lipo` |
| Temple arm | width × height, ~2 cm behind the hinge (measured 7 × 7) | `temple_w`, `temple_h` |
| Pupil → temple-arm centre | up/down `dv` (+ above), sideways `dh` | `temple_dv`, `temple_dh` (raw values; measured 10, 37) |
| Frame top rim above pupil | `frame_rim` (measured 13; must be < 26) | check |

**Pass:** sharp text through lens + acrylic, right way round; all numbers written down → rebuild (`sh hardware/enclosure/build.sh`) → print `test_fit.stl` first.

## Step 13 — Final build: soldering (later)
Do this once Steps 7, 9–12 pass.
1. Push the 8-pin pieces into the breadboard, lay the ESP32-C3 on top, components facing up. The breadboard holds them straight.
2. Iron at ~330 °C, a little flux. Touch iron to pad + pin together 1 s, feed solder, remove solder, then iron. Shiny cone = good; ball = reheat.
3. OLED: if its 4 pins aren't soldered, do the same.
4. Continuity check every **neighbouring** pin pair → must **not** beep (no solder bridges).
5. Short final wires: LiPo → TP4056 → switch → ESP32 5V/G; OLED → 3V3/G/GPIO8/GPIO9.

**Pass:** all pins shiny cones, no beep between neighbours. Re-run Steps 3, 4 and 10 after soldering.

## Step 14 — Enclosure + mount (later)
Measure the temple arm + part thicknesses → print `hardware/enclosure/stl/test_fit.stl`, tune `clr` → enclosure v2 (plan in `docs/handoff/2026-10-29.md`) → print, paint inside matte black, assemble per `hardware/enclosure/README.md`.
**Pass:** glasses on, switch ON, `send_test.py` word sharp in front of the eye.

## Results
All tests below use friction-fit headers (no solder) until the final build.
| # | Part | Test | Result (✅/❌ + note) | Date |
|---|---|---|---|---|
| 1 | ESP32-C3 #1 | 5V/3V3 volts, blink + serial | ✅ volts: 5V = 5.162 V, 3V3 = 3.302 V; ✅ blink + serial | 2026-10-25 |
| 2 | ESP32-C3 #2 (spare) | 5V/3V3 volts, blink + serial | ✅ volts: 5V = 5.162 V, 3V3 = 3.302 V; ✅ blink (Step 11) | 2026-10-24 |
| 3 | OLED #1 | I2C 0x3C, HELLO, mirror | ✅ 0x3C, text + bitmap shown; ✅ mirror check (Step 11) | 2026-10-25 |
| 4 | OLED #2 | I2C 0x3C, HELLO | ✅ done | 2026-10-31 |
| 5 | Wi-Fi + UDP | `send_test.py` text on OLED, IP + glasses.local | ✅ via IP 10.249.236.231; ✅ glasses.local (Step 11) | 2026-10-25 |
| 6 | TP4056 #1 | B+ ≈ 4.2 V, USB only | ✅ done | 2026-10-31 |
| 7 | TP4056 #2 | B+ ≈ 4.2 V, USB only | ✅ done | 2026-10-31 |
| 8 | Slide switch ×3 | continuity swap | ✅ done | 2026-10-31 |
| 9 | Type-C cable | data (upload works) | ✅ | 2026-10-25 |
| 10 | Breadboard / jumpers | used in steps 4–6 without faults | ✅ after wiring fix | 2026-10-25 |
| 11 | Bench supply | 4.20 V / 0.30 A set + checked with meter | ✅ done | 2026-10-31 |
| 12 | LiPo charge | bench charge tapered, end V, not warm (when needed) | ✅ done | 2026-10-31 |
| 13 | LiPo #1 | volts as received; soldered, NO-USB tape | ✅ 3.999 V (Rigol DM3058E) — ~80 %, no charge needed | 2026-10-29 |
| 14 | LiPo #2 | volts as received; soldered, NO-USB tape | ✅ done | 2026-10-31 |
| 15 | Battery power | READY + send_test.py on battery, switch on/off, 3V3 | ✅ READY + IP 10.249.236.231, words from `send_test.py` shown; 5V pin 3.967 V under load; ✅ 3V3 + switch toggle | 2026-10-29 |
| 16 | Battery life | runtime (hours) | ✅ done | 2026-10-31 |
| 17 | Optics | sharp + right way round (u mm, MIRROR_X) | | |
| 18 | Soldering | final build | | |
| 19 | Enclosure | test_fit, print, assemble | | |
