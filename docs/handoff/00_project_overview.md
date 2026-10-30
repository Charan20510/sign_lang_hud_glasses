# Project Handoff — Sign-Language → Smart-Glasses HUD (Semester Project)

> Project overview (stable facts). Day-by-day notes live in `YYYY-MM-DD.md` next to this file.
> Paste this whole file into a new chat with: "Continue my project from this handoff. Next I want to: ____"

## 1. Project in one line
ISL signer in front of me → camera → **laptop** (MediaPipe + PyTorch) recognises the sign → word sent over **Wi-Fi** → **ESP32-C3** on my glasses shows it on a **0.96" OLED**, reflected into my eye (DIY HUD). Combined CS + ECE project.

- Me: Charan, final-year B.Tech ECE (VLSI), IIIT Senapati, Manipur. Dev machine: MacBook Air (Apple Silicon).
- Style: short, simple key points.
- Scope: **isolated words** (INCLUDE-50 + my own words), not full sentences.

## 2. Final architecture
```
[Camera: laptop webcam (now) / ESP32-CAM on glasses (stretch)]
   → [Laptop: MediaPipe landmarks → normalize → GRU/Transformer → smoother → sentence]
   → UDP/WebSocket JSON over phone hotspot
   → [ESP32-C3 SuperMini + SSD1306 OLED → mirror → 25mm lens → 45° acrylic → eye]
```

## 3. Optics design (side view, cm, internal) — drawn in hud_glasses_drawings.pdf
- OLED → mirror (45°): **2.2** | mirror → lens: **1.8** | total u = **4.0 cm** < f = 4.5 cm
- Lens → acrylic (45°): **1.5** | eye relief ≈ **2.0**
- Result: virtual image ≈ 36–38 cm away, ~9× magnified.
- Housing: total length **9.5**, optics head **2.5**, electronics tube **7.0**, height **3.0**, internal width **2.9**, head drops to **6.0**.
- Panels: side ×2 (L-shape 9.5×6.0), top 9.5×2.9, bottom 7.0×2.9, front 3.3×2.9, rear 3.0×2.9 (2 USB-C cut-outs 0.9×0.35), lens plate 2.5×2.9 (hole Ø2.4), mirror 2.5×2.9, acrylic 3.0×2.9, step strip 0.3×2.9.
- Notes: paint interior matte black; thin acrylic (1 mm) avoids double image; text may be flipped → fix in code (setRotation / mirror commands); focus by sliding OLED ±3 mm.
- Based on github.com/perseus784/June_Glasses (concept/optics only; its electronics had flaws: no regulator, ESP8266-01, hardcoded IP).

## 4. Electronics & wiring
**Display unit (glasses):**
- LiPo #1 → TP4056 #1 (B+/B−) → OUT+ → slide switch → ESP32-C3 **5V** pin; OUT− → GND
- ESP32-C3 → OLED: 3V3→VCC, GND→GND, **GPIO8→SDA, GPIO9→SCL**, I2C addr 0x3C

**Camera unit (stretch, opposite arm):**
- LiPo #2 → TP4056 #2 → switch → **MT3608 set to 5.0 V** → ESP32-CAM 5V/GND
- Never feed LiPo directly to ESP32-CAM. Runs hot; ~1 h on 600 mAh.

**Safety / charging (decided 2026-10-29):** TP4056 left stock (1 A = 1.7C for 600 mAh) → its USB is NEVER used with a cell attached (port taped "NO USB"). Charge only with the lab bench supply: 4.20 V CV, 0.30 A limit, stop at ≤ 0.05 A. Battery leads soldered to B+/B−, never hand-held.

## 5. Parts status (as of 24 Oct 2026)
**In hand (Robocraze order 377900, delivered):** ESP32-C3 SuperMini ×2 (unsoldered), 0.96" SSD1306 OLED ×2,
TP4056 Type-C w/ protection ×2, slide switch ×3, veroboard 6×4 ×2, 40×2 male + 40×1 female berg,
Type-C cable, MB102 830 breadboard, jumper wire set, 12-in-1 soldering kit (with multimeter).

**Arrived by 2026-10-29:** LiPo 3.7 V **600 mAh** ×2 (KP 602030P, ~30 × 20 × 6 mm), DOMO 25 mm / f45 lens pair, 1 mm acrylic ×4.
**Still to get:** mirror 25 × 30 mm (local shop), heat-shrink/tape.
**Stretch, not ordered yet:** ESP32-CAM OV3660, ESP32-CAM-MB, MT3608 boost, glue gun.

**Local / already have:**
- Mirror piece 2.5×2.9 cm — local glass shop (₹10–30), thin glass preferred
- Glasses frame — my Lenskart computer glasses (mount with zip ties/velcro, no glue; raise OLED contrast because of blue-cut coating)

## 6. Software plan (full spec in CLAUDE.md — use with Claude Code)
- Dataset: **INCLUDE-50** (AI4Bharat/IIT Madras) — zenodo.org/records/4010759, code github.com/AI4Bharat/INCLUDE. Paper benchmark: 94.5% on INCLUDE-50.
- + my own clips: ~30/word, 2–3 people (tools/record_custom.py).
- Features: MediaPipe hands (2×21×3) + upper-body pose; normalize by shoulder center/width; resample to T = 32.
- Models: GRU baseline → small Transformer (PyTorch, MPS). Run natively on macOS, not Docker.
- Eval: top-1/top-5, macro F1, confusion matrix, signer-independent test, latency, model size → reports/RESULTS.md.
- Live: sliding window, predict every 4 frames, emit if conf ≥ 0.8 + 3/5 vote + 1 s cooldown; demo window for evaluators.
- Link: phone hotspot, UDP JSON `{"text":..,"conf":..}`, mDNS `glasses.local`, `send_test.py` first.
- Phases: 0 Setup → 1 Data → 2 Keypoints → 3 Train → 4 Evaluate → 5 Live app → 6 Firmware → 7 Camera (stretch) → 8 Polish.
- First Claude Code prompt: "Read CLAUDE.md. Do Phase 0 only, show results, stop."

## 7. Files created so far
- `CLAUDE.md` — Claude Code project spec (phases, repo structure, rules)
- `hud_glasses_drawings.pdf` + 2 PNGs — side view with dimensions, optics math, wiring diagram, cut templates

## 8. Open to-dos
1. Hardware bring-up (branch `testout`, `docs/hardware_bringup.md` + PDF, 15 steps): Steps 1–6 ✅ by 2026-10-25. Left: 7 TP4056 + switches (USB only) → 8 bench-supply charge (when < 3.9 V) → 9 solder battery leads + NO-USB tape → 10 ✅ runs on battery 2026-10-29 (3V3, switch, runtime pending) → 11 board #2 / OLED #2 / mirror / glasses.local → 12 optics bench → 13 soldering → 14 enclosure.
2. LiPo #1 = 3.999 V as received (no charge needed yet). Charge only on the bench supply (Step 8).
3. Get mirror piece locally.
4. When LiPo/lens/acrylic arrive: power from battery, build housing, full `glasses_display.ino`.
5. Software Phases 3–4 (train/evaluate) on `S1`.
6. Later: camera unit, latency measurement, report & viva prep.

Daily log: see `docs/handoff/README.md`.
