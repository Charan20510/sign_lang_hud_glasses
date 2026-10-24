"""Send typed text to the glasses over UDP (no ML) — checks the Wi-Fi link + OLED.

Packet format (same one the live app will use): {"text": "...", "conf": 0.92}

Examples:
    python tools/send_test.py --text hello                 # host/port from config.yaml
    python tools/send_test.py --host 192.168.43.57 --text hello
    python tools/send_test.py --host 192.168.43.57         # interactive: type lines, Ctrl+C to quit
"""
import argparse
import json
import socket
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def make_packet(text, conf=1.0):
    """Build the UDP payload bytes for one word/line."""
    return json.dumps({"text": text, "conf": round(float(conf), 2)}).encode("utf-8")


def main():
    net = yaml.safe_load(open(ROOT / "config.yaml"))["network"]
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default=net["glasses_host"], help="glasses IP or mDNS name")
    ap.add_argument("--port", type=int, default=net["udp_port"])
    ap.add_argument("--text", help="send once and exit; omit for interactive mode")
    ap.add_argument("--conf", type=float, default=1.0)
    args = ap.parse_args()

    addr = (socket.gethostbyname(args.host), args.port)   # resolves glasses.local via mDNS
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    lines = [args.text] if args.text else iter(lambda: input("> "), None)
    try:
        for line in lines:
            sock.sendto(make_packet(line, args.conf), addr)
            print(f"sent to {addr[0]}:{addr[1]} -> {line!r}")
    except (KeyboardInterrupt, EOFError):
        print()


if __name__ == "__main__":
    main()
