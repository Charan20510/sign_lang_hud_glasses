"""Sends words and sentences to the HUD glasses (ESP32-C3 + OLED) over UDP. Standard library + pyyaml.

Packet (docs/interface.md):  {"text": "hello", "conf": 0.92}   one UDP datagram per word, < 256 bytes.
Host/port default to config.yaml `network:` (glasses.local:4210).

  python glasses.py                                 # self-check (loopback, no glasses needed)
  python glasses.py --host 192.168.43.57 --text hi  # send one line to the real glasses
"""
import json
import socket
import sys
import threading
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
MAX_BYTES = 255                                   # firmware buffer is char packet[256]


def load_network():
    return yaml.safe_load(open(ROOT / "config.yaml"))["network"]


def make_packet(text, conf=1.0):
    """UDP payload for one word/line, text cut short so the whole packet stays < 256 bytes."""
    conf = round(float(conf), 2)
    while True:
        data = json.dumps({"text": text, "conf": conf}).encode("utf-8")
        if len(data) <= MAX_BYTES:
            return data
        text = text[:-1]


class Glasses:
    """Fire-and-forget sender. Resolving glasses.local (mDNS) can take seconds, so it runs in a background
    thread and retries until the glasses are on the hotspot; until then packets are dropped (never blocks)."""

    def __init__(self, host=None, port=None):
        net = load_network()
        self.host, self.port = host or net["glasses_host"], port or net["udp_port"]
        self.addr = None
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        threading.Thread(target=self._resolve, daemon=True, name="glasses-dns").start()

    def _resolve(self):
        warned = False
        while self.addr is None:
            try:
                self.addr = (socket.gethostbyname(self.host), self.port)
                print(f"[glasses] sending to {self.host} = {self.addr[0]}:{self.port}", flush=True)
            except OSError:
                if not warned:
                    print(f"[glasses] cannot find {self.host} yet (same hotspot? glasses on?). Retrying...",
                          file=sys.stderr, flush=True)
                    warned = True
                time.sleep(3)

    def send(self, text, conf=1.0):
        text = text.strip()
        if not text or self.addr is None:
            return False
        try:
            self.sock.sendto(make_packet(text, conf), self.addr)
            return True
        except OSError:          # Wi-Fi blip: drop this word, the next one tries again
            return False

    def close(self):
        self.sock.close()


def selftest():
    rx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    rx.bind(("127.0.0.1", 0))
    rx.settimeout(2)
    g = Glasses("127.0.0.1", rx.getsockname()[1])
    for _ in range(50):                            # wait for the resolver thread
        if g.addr:
            break
        time.sleep(0.02)
    assert g.send("hello", 0.923)
    assert json.loads(rx.recv(512)) == {"text": "hello", "conf": 0.92}
    assert g.send("नमस्ते " * 40)                     # long UTF-8 sentence is cut, never overflows
    assert len(rx.recv(512)) <= MAX_BYTES
    assert not g.send("   ")                       # nothing to show -> nothing sent
    g.close()
    print("glasses.py self-check OK")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host")
    ap.add_argument("--port", type=int)
    ap.add_argument("--text")
    a = ap.parse_args()
    if a.text is None:
        selftest()
    else:
        g = Glasses(a.host, a.port)
        while g.addr is None:
            time.sleep(0.1)
        g.send(a.text)
        print(f"sent {a.text!r}")
