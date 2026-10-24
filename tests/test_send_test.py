"""Packet format test for tools/send_test.py."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from send_test import make_packet


def test_packet_is_json_with_text_and_conf():
    msg = json.loads(make_packet("hello", 0.917))
    assert msg == {"text": "hello", "conf": 0.92}
    assert len(make_packet("x" * 100)) < 255   # fits the firmware's 256-byte buffer
