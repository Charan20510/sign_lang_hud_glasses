"""Record my own sign clips with the webcam (or ESP32-CAM stream).

Flow: live preview -> press SPACE -> 3-2-1 countdown -> record a fixed number
of frames -> save mp4 to data/raw/custom/<word>/<signer>_<YYYYmmdd_HHMMSS>.mp4.
Repeat until n clips are saved. Press q or ESC to quit early.

Example:
    python tools/record_custom.py --word hello --signer ravi --n 30
"""
import argparse
import time
from datetime import datetime
from pathlib import Path

import cv2
import yaml

ROOT = Path(__file__).resolve().parent.parent
COUNTDOWN_FROM = 3          # seconds of countdown before each clip
KEY_SPACE, KEY_ESC = 32, 27


def parse_source(text):
    """'0' -> webcam index 0 (int); anything else (a URL) stays a string."""
    return int(text) if str(text).isdigit() else text


def draw_text(frame, text, y, scale=0.8, color=(0, 255, 0)):
    """Write one line of text on the frame at height y (pixels)."""
    cv2.putText(frame, text, (10, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, 2)


def main():
    cfg = yaml.safe_load(open(ROOT / "config.yaml"))
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--word", required=True, help="the word being signed (folder name)")
    ap.add_argument("--signer", default="me", help="who is signing (start of the file name)")
    ap.add_argument("--n", type=int, default=cfg["data"]["clips_per_word"], help="clips to record")
    ap.add_argument("--source", default=str(cfg["camera"]["source"]),
                    help="webcam index (e.g. 0) or MJPEG URL")
    args = ap.parse_args()

    fps = cfg["data"]["record_fps"]
    n_frames = int(cfg["data"]["clip_seconds"] * fps)  # fixed frame count -> every clip same length
    out_dir = ROOT / cfg["paths"]["raw_custom"] / args.word
    out_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(parse_source(args.source))
    if not cap.isOpened():
        raise SystemExit(f"ERROR: cannot open camera '{args.source}'. On macOS, allow camera access for "
                         "your Terminal app: System Settings > Privacy & Security > Camera, then restart it.")
    cap.set(cv2.CAP_PROP_FPS, fps)

    saved = 0
    while saved < args.n:
        # --- 1. preview: wait for SPACE (start) or q/ESC (quit) ---
        ok, frame = cap.read()
        if not ok:
            print("Camera stopped sending frames."); break
        frame = cv2.flip(frame, 1)  # mirror the preview only, feels natural
        draw_text(frame, f"word: {args.word}   clip {saved + 1}/{args.n}", 30)
        draw_text(frame, "SPACE = record, q = quit", 60, 0.6, (255, 255, 255))
        cv2.imshow("record", frame)
        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), KEY_ESC):
            break
        if key != KEY_SPACE:
            continue

        # --- 2. countdown 3-2-1 drawn on live frames ---
        start = time.time()
        while (left := COUNTDOWN_FROM - (time.time() - start)) > 0:
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]
            cv2.putText(frame, str(int(left) + 1), (w // 2 - 40, h // 2 + 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 4, (0, 0, 255), 8)
            cv2.imshow("record", frame)
            cv2.waitKey(1)

        # --- 3. record exactly n_frames frames ---
        path = out_dir / f"{args.signer}_{datetime.now():%Y%m%d_%H%M%S}.mp4"
        writer, written = None, 0
        for i in range(n_frames):
            ok, frame = cap.read()
            if not ok:
                break
            if writer is None:  # create writer once we know the frame size
                h, w = frame.shape[:2]
                writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
            writer.write(frame)  # save the clean, UN-mirrored frame (same as INCLUDE / live app)
            written += 1
            preview = cv2.flip(frame, 1)
            draw_text(preview, f"REC {i + 1}/{n_frames}", 30, color=(0, 0, 255))
            cv2.imshow("record", preview)
            cv2.waitKey(1)
        if writer is not None:
            writer.release()
        if written == n_frames:
            saved += 1
            print(f"saved {path}")
        else:
            path.unlink(missing_ok=True)  # incomplete clip -> don't keep it
            print("Camera dropped out during recording; clip discarded.")

    cap.release()
    cv2.destroyAllWindows()
    print(f"Done: {saved} clip(s) saved in {out_dir}")


if __name__ == "__main__":
    main()
