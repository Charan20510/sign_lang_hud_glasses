"""Print and save a table of how many clips we have per word.

INCLUDE part : reads <raw_include>/include50_index.csv (made by ml/download_include.py)
               and counts train / test rows per word + how many files are on disk.
Custom part  : counts <raw_custom>/<word>/*.mp4 and distinct signers per word.
Output       : printed table + <reports>/data_summary.csv

Example:
    python tools/data_summary.py
"""
import argparse
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parent.parent
COLUMNS = ["source", "word", "train", "test", "downloaded", "custom_clips", "signers"]


def signer_of(mp4):
    """File name is <signer>_<YYYYmmdd>_<HHMMSS>.mp4 -> drop the last two '_' parts.
    rsplit keeps signer names that themselves contain '_' (e.g. 'ravi_k')."""
    return mp4.stem.rsplit("_", 2)[0]


def include_rows(index_csv):
    """One row per INCLUDE word: train/test counts and files actually downloaded."""
    if not index_csv.exists():
        print(f"[INCLUDE] {index_csv} not found -> run: python ml/download_include.py")
        return []
    df = pd.read_csv(index_csv)
    df["downloaded"] = [(ROOT / p).exists() for p in df["local_path"]]
    rows = []
    for word, g in df.groupby("word"):
        rows.append({"source": "include", "word": word,
                     "train": int((g["split"] == "train").sum()),
                     "test": int((g["split"] == "test").sum()),
                     "downloaded": int(g["downloaded"].sum()),
                     "custom_clips": 0, "signers": 0})
    return rows


def custom_rows(custom_dir):
    """One row per custom word folder: clip count and number of distinct signers."""
    rows = []
    for word_dir in sorted(p for p in custom_dir.glob("*") if p.is_dir()):
        clips = list(word_dir.glob("*.mp4"))
        if clips:
            rows.append({"source": "custom", "word": word_dir.name, "train": 0, "test": 0,
                         "downloaded": 0, "custom_clips": len(clips),
                         "signers": len({signer_of(c) for c in clips})})
    if not rows:
        print(f"[custom] no clips in {custom_dir} yet -> record with tools/record_custom.py")
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default=str(ROOT / "config.yaml"), help="path to config.yaml")
    args = ap.parse_args()
    paths = yaml.safe_load(open(args.config))["paths"]
    # Relative paths are relative to the project root; absolute paths are used as-is.
    include_dir, custom_dir, reports = (ROOT / paths[k] for k in ("raw_include", "raw_custom", "reports"))

    table = pd.DataFrame(include_rows(include_dir / "include50_index.csv") + custom_rows(custom_dir),
                         columns=COLUMNS)
    pd.set_option("display.max_rows", None)
    print(table.to_string(index=False))
    totals = table[COLUMNS[2:]].sum()
    print(f"\nTOTAL words={len(table)}  " + "  ".join(f"{k}={v}" for k, v in totals.items()))

    reports.mkdir(parents=True, exist_ok=True)
    out = reports / "data_summary.csv"
    table.to_csv(out, index=False)
    print(f"saved {out}")


if __name__ == "__main__":
    main()
