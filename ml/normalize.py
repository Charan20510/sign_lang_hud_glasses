"""Landmark layout + normalisation. USED BY TRAINING AND THE LIVE APP (never duplicate this).

Per-frame feature row (149 values with the default config.yaml):

    [ left hand 21 x (x,y,z) | right hand 21 x (x,y,z) | pose 7 x (x,y,z) | left flag, right flag ]
       0:63                    63:126                    126:147            147:149

- x and z are multiplied by width/height, so x, y, z share the same units
  (INCLUDE videos are 16:9, a webcam is 4:3 -> both look the same after this).
- Missing hand -> 21 zero points + flag 0. Missing pose -> zero points.

normalize(seq) makes a clip independent of where the signer stands and how big they look:
  1. centre x,y on the shoulder midpoint,
  2. divide by shoulder width,
  3. resample to T frames (config.yaml keypoints.T, default 32).

Usage:
    python ml/normalize.py "data/keypoints/include/Greetings/48. Hello/MVI_0089.npy"
"""
import argparse
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parent.parent
KP = yaml.safe_load((ROOT / "config.yaml").read_text())["keypoints"]
assert KP["num_hands"] == 2 and KP["use_presence_flags"], "layout below assumes 2 hands + presence flags"

C = KP["coords"]                                    # 3 = x, y, z
HAND_POINTS = KP["hand_landmarks"]                  # 21
HAND_DIM = HAND_POINTS * C                          # 63
POSE_NAMES = list(KP["pose_landmarks"])             # nose, left_shoulder, ...
POSE_IDS = list(KP["pose_landmarks"].values())      # their MediaPipe pose indices
L_SH, R_SH = POSE_NAMES.index("left_shoulder"), POSE_NAMES.index("right_shoulder")

LEFT_HAND = slice(0, HAND_DIM)
RIGHT_HAND = slice(HAND_DIM, 2 * HAND_DIM)
POSE = slice(2 * HAND_DIM, 2 * HAND_DIM + len(POSE_IDS) * C)
FLAGS = slice(POSE.stop, POSE.stop + 2)             # [left flag, right flag]
NUM_FEATURES = FLAGS.stop                           # 149


def _points(landmarks, ids, aspect):
    """MediaPipe landmark list -> flat [x, y, z, x, y, z, ...] with x, z in height units."""
    return np.array([[landmarks[i].x * aspect, landmarks[i].y, landmarks[i].z * aspect] for i in ids],
                    np.float32).ravel()


def frame_features(results, width, height):
    """One MediaPipe Holistic result -> one feature row of NUM_FEATURES values."""
    aspect = width / height
    row = np.zeros(NUM_FEATURES, np.float32)
    hands = ((results.left_hand_landmarks, LEFT_HAND, FLAGS.start),
             (results.right_hand_landmarks, RIGHT_HAND, FLAGS.start + 1))
    for hand, where, flag in hands:
        if hand is not None:
            row[where] = _points(hand.landmark, range(HAND_POINTS), aspect)
            row[flag] = 1
    if results.pose_landmarks is not None:
        row[POSE] = _points(results.pose_landmarks.landmark, POSE_IDS, aspect)
    return row


def normalize(seq, T=KP["T"]):
    """Raw (n_frames, NUM_FEATURES) clip -> normalised (T, NUM_FEATURES) clip."""
    seq = np.array(seq, np.float32)  # copy, never change the caller's array
    if seq.ndim != 2 or seq.shape[1] != NUM_FEATURES or len(seq) == 0:
        raise ValueError(f"expected (n>0, {NUM_FEATURES}), got {seq.shape}")
    n = len(seq)

    pose = seq[:, POSE].reshape(n, -1, C)
    seen = np.any(pose != 0, axis=(1, 2))           # frames where the body was detected
    if seen.any():  # no body at all -> nothing to centre on, only resample
        ls, rs = pose[seen, L_SH], pose[seen, R_SH]
        centre = np.median((ls[:, :2] + rs[:, :2]) / 2, axis=0)            # median = robust to bad frames
        width = max(np.median(np.linalg.norm(ls[:, :2] - rs[:, :2], axis=1)), 1e-6)

        pts = seq[:, :POSE.stop].reshape(n, -1, C)  # hands + pose as points
        pts[:, :, :2] -= centre                     # z is already relative (wrist / hips), not centred
        pts /= width
        seq[:, :POSE.stop] = pts.reshape(n, -1)

        # centring moved the zero "missing" points -> put them back to exactly 0
        seq[seq[:, FLAGS.start] == 0, LEFT_HAND] = 0
        seq[seq[:, FLAGS.start + 1] == 0, RIGHT_HAND] = 0
        seq[~seen, POSE] = 0

    # nearest-frame resampling: never blends a missing (zero) frame with a real one
    idx = np.linspace(0, n - 1, T).round().astype(int)
    return seq[idx]


def main():
    """Print raw vs normalised shape and value range of one .npy clip."""
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("npy", help="raw keypoint file made by ml/extract_keypoints.py")
    raw = np.load(ap.parse_args().npy)
    out = normalize(raw)
    print(f"raw {raw.shape} -> normalised {out.shape}")
    print(f"hand seen in {raw[:, FLAGS].max(1).mean():.0%} of frames")
    print(f"normalised x,y range: {out[:, :POSE.stop].min():.2f} .. {out[:, :POSE.stop].max():.2f}")


if __name__ == "__main__":
    main()
