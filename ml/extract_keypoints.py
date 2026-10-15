"""Video -> raw MediaPipe Holistic landmarks, one .npy per video.

Output mirrors the raw folder:
    data/raw/include/Greetings/48. Hello/MVI_0089.MOV -> data/keypoints/include/Greetings/48. Hello/MVI_0089.npy
Each file: (n_frames, NUM_FEATURES) float32, NOT normalised (ml/normalize.py does that at load time,
so changing normalisation never needs re-extraction). Layout: see ml/normalize.py.

Already-extracted videos are skipped, so the script can be stopped and re-run safely.

Usage:
    python ml/extract_keypoints.py --limit 5        # quick timing test
    python ml/extract_keypoints.py --workers 8      # extract everything
    python ml/extract_keypoints.py --check          # shape check -> reports/keypoints_summary.csv
    python ml/extract_keypoints.py --plot FILE.npy  # -> reports/keypoints_sample.png
"""
import argparse
import os
import time
from multiprocessing import Pool
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import yaml
from tqdm import tqdm

from normalize import FLAGS, KP, LEFT_HAND, NUM_FEATURES, POSE, RIGHT_HAND, C, frame_features, normalize

ROOT = Path(__file__).resolve().parent.parent
CFG = yaml.safe_load((ROOT / "config.yaml").read_text())
RAW_ROOT = (ROOT / CFG["paths"]["raw_include"]).parent   # data/raw
KP_ROOT = ROOT / CFG["paths"]["keypoints"]               # data/keypoints
REPORTS = ROOT / CFG["paths"]["reports"]


def video_list():
    """[(video path, word)] for every downloaded INCLUDE video + every custom clip."""
    df = pd.read_csv(ROOT / CFG["paths"]["raw_include"] / "include50_index.csv")
    df = df[df["downloaded"] == 1]
    videos = [(ROOT / p, w) for p, w in zip(df["local_path"], df["word"])]
    videos += [(p, p.parent.name) for p in sorted((ROOT / CFG["paths"]["raw_custom"]).glob("*/*.mp4"))]
    return videos


def out_path(video):
    """data/raw/<...>/clip.MOV -> data/keypoints/<...>/clip.npy"""
    return KP_ROOT / video.relative_to(RAW_ROOT).with_suffix(".npy")


def extract_one(video):
    """Run Holistic on every frame of one video and save the rows. Returns (status, video)."""
    out = out_path(video)
    if out.exists():
        return "skipped", video
    cap = cv2.VideoCapture(str(video))
    w, h = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    rows = []
    # new Holistic per video: it tracks between frames, so state must not leak from the previous clip
    with mp.solutions.holistic.Holistic(static_image_mode=False,
                                        model_complexity=KP["model_complexity"],
                                        min_detection_confidence=KP["min_detection_conf"],
                                        min_tracking_confidence=KP["min_tracking_conf"]) as holistic:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            res = holistic.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))  # no flip: keep left = left
            rows.append(frame_features(res, w, h))
    cap.release()
    if not rows:
        return "failed", video
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(out.stem + ".tmp.npy")  # write then rename: no half files if interrupted
    np.save(tmp, np.stack(rows))
    tmp.rename(out)
    return "extracted", video


def extract_all(videos, workers):
    """Extract in parallel processes, print a summary, log failures to reports/."""
    start = time.time()
    status, failed = {}, []
    with Pool(workers) as pool:
        for s, video in tqdm(pool.imap_unordered(extract_one, [v for v, _ in videos]),
                             total=len(videos), desc="Extracting keypoints"):
            status[s] = status.get(s, 0) + 1
            if s == "failed":
                failed.append(str(video.relative_to(ROOT)))
    mins = (time.time() - start) / 60
    print(f"{status} in {mins:.1f} min ({mins * 60 / max(len(videos), 1):.1f} s/video)")
    if failed:
        REPORTS.mkdir(exist_ok=True)
        pd.DataFrame({"video": failed}).to_csv(REPORTS / "keypoints_failures.csv", index=False)
        print(f"{len(failed)} failed -> {REPORTS / 'keypoints_failures.csv'}")


def check(videos):
    """Shape check every .npy + per-word detection rates -> reports/keypoints_summary.csv."""
    rows, problems = [], []
    for video, word in tqdm(videos, desc="Checking"):
        f = out_path(video)
        if not f.exists():
            problems.append(f"missing: {f.relative_to(ROOT)}")
            continue
        a = np.load(f)
        ok = a.ndim == 2 and a.shape[1] == NUM_FEATURES and len(a) > 0 and np.isfinite(a).all()
        if not ok or normalize(a).shape != (KP["T"], NUM_FEATURES):
            problems.append(f"bad shape {a.shape}: {f.relative_to(ROOT)}")
            continue
        rows.append({"word": word, "frames": len(a),
                     "hand_rate": a[:, FLAGS].max(1).mean(),          # frames with >= 1 hand seen
                     "pose_rate": a[:, POSE].any(1).mean()})          # frames with body seen
    df = pd.DataFrame(rows)
    summary = df.groupby("word").agg(clips=("frames", "size"), mean_frames=("frames", "mean"),
                                     hand_rate=("hand_rate", "mean"), pose_rate=("pose_rate", "mean"))
    REPORTS.mkdir(exist_ok=True)
    summary.round(3).to_csv(REPORTS / "keypoints_summary.csv")

    print(f"\nfiles OK: {len(df)} / {len(videos)} | problems: {len(problems)}")
    for p in problems[:20]:
        print("  ", p)
    print(f"frames per clip: min {df.frames.min()}, mean {df.frames.mean():.0f}, max {df.frames.max()}")
    print(f"hand seen in {df.hand_rate.mean():.1%} of frames, body in {df.pose_rate.mean():.1%}")
    low = summary[summary.hand_rate < 0.6]
    print(f"words with hand rate < 60%: {', '.join(low.index) if len(low) else 'none'}")
    print(f"saved {REPORTS / 'keypoints_summary.csv'}")
    return not problems


def plot(npy):
    """Save 8 of the T normalised frames as scatter plots -> reports/keypoints_sample.png."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    seq = normalize(np.load(npy))
    picks = np.linspace(0, len(seq) - 1, 8).round().astype(int)
    fig, axes = plt.subplots(2, 4, figsize=(14, 7), sharex=True, sharey=True)
    parts = ((LEFT_HAND, "tab:blue", "left hand"), (RIGHT_HAND, "tab:orange", "right hand"),
             (POSE, "tab:gray", "pose"))
    for ax, t in zip(axes.flat, picks):
        for where, colour, label in parts:
            pts = seq[t, where].reshape(-1, C)
            pts = pts[pts.any(1)]                      # skip missing (all-zero) points
            ax.scatter(pts[:, 0], -pts[:, 1], s=10, c=colour, label=label)  # -y: image y points down
        ax.set_title(f"frame {t + 1}/{len(seq)}")
        ax.set_aspect("equal")
    axes.flat[0].legend(loc="lower left", fontsize=8)
    fig.suptitle(f"{Path(npy).parent.name}/{Path(npy).name} (normalised: shoulder midpoint = 0, width = 1)")
    REPORTS.mkdir(exist_ok=True)
    fig.savefig(REPORTS / "keypoints_sample.png", dpi=100, bbox_inches="tight")
    print(f"saved {REPORTS / 'keypoints_sample.png'}")


def main():
    """Parse CLI args and run extract / check / plot."""
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2),
                    help="parallel processes (default: CPU cores - 2)")
    ap.add_argument("--limit", type=int, help="only the first N videos (timing test)")
    ap.add_argument("--check", action="store_true", help="verify every .npy and write the summary")
    ap.add_argument("--plot", metavar="NPY", help="plot one keypoint file")
    args = ap.parse_args()

    if args.plot:
        return plot(args.plot)
    videos = video_list()[: args.limit]
    if args.check:
        return check(videos)
    print(f"{len(videos)} videos, {args.workers} workers -> {KP_ROOT}")
    extract_all(videos, args.workers)


if __name__ == "__main__":
    main()
