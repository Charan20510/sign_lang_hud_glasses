# Run guide: signs → laptop → ESP32 Wi-Fi → OLED

Short version. Do the steps in order; each one proves one more link.

## 1. One-time setup
- Phone hotspot on **2.4 GHz** (the ESP32-C3 cannot join 5 GHz). Mac joins the same hotspot.
- Wiring: OLED `SDA` → GPIO8, `SCK` → GPIO9, `VDD` → 3V3, `GND` → GND. Address 0x3C.
- `firmware/glasses_display/secrets.h` = hotspot name + password (copy of `t4_wifi_udp/secrets.h`;
  or copy `secrets.h.example` → `secrets.h` and fill it in).
- Arduino IDE → **File → Open** `firmware/glasses_display/glasses_display.ino`.
- Tools → Board **ESP32C3 Dev Module**, **USB CDC On Boot: Enabled**, Port `/dev/cu.usbmodem…` → Upload.

## 2. Check the Wi-Fi link
- OLED shows `WIFI...`, then `READY` + the glasses' IP. Note the IP.
- On the Mac:
  ```bash
  cd ~/projects/sign_lang_hud_glasses && source venv/bin/activate
  python tools/send_test.py --text hello
  ```
- Pass: `hello` on the OLED. If `glasses.local` fails, add `--host <IP>`.

## 3. Simulated signing (no camera, no model)
- ```bash
  python software/run.py --simulate
  ```
- Pass: each word in the middle of the OLED, big (size 2), 2 s apart — `IT`, `IS`, `HOT`, `TODAY` —
  then the full sentence `It is hot today.` scrolling right-to-left on one line, looping until the next word.
- Scroll speed: `SCROLL_PX_PER_S` in `glasses_display.ino` (same value in `software/run.py`).
- `The HTTP server did not start` → port 8000 is busy (e.g. another app): add `--port 9000`.
- Terminal prints `[glasses] sending to glasses.local = <IP>:4210`. Ctrl+C stops it.

## 4. Live camera (real signs)
- One-time install, **about 1 GB or more** (torch, mediapipe, opencv):
  ```bash
  cd software
  pip install -r requirements.txt
  python download_models.py          # MediaPipe models -> software/mp_models/
  ```
- Put a trained model in `software/model/` (`sign_model.pt`, or `words/` + `letters/`); see `software/RUNBOOK.md`.
- From `software/`:
  ```bash
  python run.py
  ```
- Sign in front of the camera: each word appears on the OLED, then the full sentence after a short pause.

## Troubleshooting
| Symptom | Fix |
|---|---|
| OLED stuck on `WIFI...` | Hotspot is 5 GHz or the password is wrong in `secrets.h` |
| OLED blank | Check SDA/SCK wires; run `firmware/tests/t2_i2c_scan` (expect 0x3C) |
| `cannot find glasses.local yet` | Use the IP from the OLED: `python software/run.py --simulate --glasses <IP>` |
| Nothing arrives | Mac and glasses on the same hotspot? Port 4210 in `config.yaml` and the sketch? |
| `No trained model found` | Step 4 needs a model; use `--simulate` until then |
| Don't want the glasses | `python software/run.py --no-glasses` |
