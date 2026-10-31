# Interface: recognizer app → glasses

The contract between the two halves of the project.
Change it only together, and update both sides.

| Side | Owner | Branch |
|---|---|---|
| Recognizer app (camera, MediaPipe, model, smoother, sender) | friend | `S1` |
| Glasses (ESP32-C3 + OLED firmware, optics, enclosure) | Charan | `testout` |

## Network
- Both devices join the same phone hotspot.
- Glasses register mDNS name **`glasses.local`** and show their IP on the OLED at boot.
- Transport: **UDP**, port **4210** (`network.udp_port` in `config.yaml`).

## Packet
One UDP datagram per emitted word, UTF-8 JSON:

```json
{"text": "hello", "conf": 0.92}
```

| Field | Type | Meaning |
|---|---|---|
| `text` | string | word or short line to show |
| `conf` | number 0–1, 2 decimals | model confidence (may be shown small or ignored) |

- Whole packet **< 256 bytes** (firmware buffer is `char packet[256]`).
- A packet that is not JSON is shown raw (handy for debugging).

## Glasses behaviour
- Latest word large (text size 2), history small (size 1), auto-scroll.
- **"NO LINK"** after **10 s** with no packet (`network.no_link_timeout_s`).
- Wi-Fi auto-reconnect.

## Test without the ML app
```bash
python tools/send_test.py --text hello
```
