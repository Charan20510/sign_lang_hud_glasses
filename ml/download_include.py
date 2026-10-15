"""Download ONLY the INCLUDE-50 videos from Zenodo (record in config.yaml).

The full INCLUDE dataset is ~57 GB split into 44 category zips. We only need
the 50 words of INCLUDE-50, so instead of downloading whole zips we:

1. Open each remote zip with Python's `zipfile` through `RangeFile`, a tiny
   file object that fetches only the bytes zipfile asks for (HTTP Range).
   Reading a zip's table of contents costs a few KB, not GBs.
2. Fetch the official INCLUDE-50 train/val/test split lists (see SPLIT_URL).
3. Match every split row to a video inside a zip -> include50_index.csv.
4. Dry run (default): print classes, counts and total download size.
   --download: extract only the needed videos, again via HTTP Range.
   If a whole zip is already in <include_zips> (config.yaml), videos are
   extracted from that local copy instead (no network).

Usage:
    python ml/download_include.py            # dry run: plan + sizes only
    python ml/download_include.py --download --workers 4
"""
import argparse
import csv
import io
import json
import os
import re
import shutil
import time
import urllib.request
import zipfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import yaml
from tqdm import tqdm

ROOT = Path(__file__).resolve().parent.parent
VIDEO_EXT = (".mov", ".mp4", ".avi", ".mkv")


class RangeFile(io.RawIOBase):
    """Read-only, seekable file over HTTP. Each read() = one Range request."""

    def __init__(self, url, size):
        self.url, self.size, self.pos = url, size, 0

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=io.SEEK_SET):
        base = {io.SEEK_SET: 0, io.SEEK_CUR: self.pos, io.SEEK_END: self.size}[whence]
        self.pos = base + offset
        return self.pos

    def readinto(self, buf):
        if self.pos >= self.size:
            return 0
        end = min(self.pos + len(buf), self.size) - 1
        req = urllib.request.Request(self.url, headers={"Range": f"bytes={self.pos}-{end}"})
        with urllib.request.urlopen(req, timeout=60) as r:
            if r.status != 206:  # server ignored Range -> would send the whole file
                raise IOError(f"HTTP Range not honoured ({r.status}) for {self.url}")
            data = r.read()
        buf[: len(data)] = data
        self.pos += len(data)
        return len(data)


def open_remote_zip(info, buffer_bytes=1 << 16):
    """Open a remote zip (Zenodo file entry) as a normal zipfile.ZipFile.

    buffer_bytes = bytes fetched per HTTP request: small (64 KB) for reading
    listings, large (8 MB) for downloading videos (fewer, bigger requests).
    """
    raw = RangeFile(info["links"]["self"], info["size"])
    return zipfile.ZipFile(io.BufferedReader(raw, buffer_bytes))


def zenodo_files(record):
    """Return {zip name: Zenodo file entry} for every .zip in the record."""
    url = f"https://zenodo.org/api/records/{record}"
    with urllib.request.urlopen(url, timeout=60) as r:
        files = json.load(r)["files"]
    return {f["key"]: f for f in files if f["key"].endswith(".zip")}


def read_listings(files, cache, workers=8):
    """Table of contents of every zip: {zip: [[member, compress_size, file_size], ...]}.

    Cached to `cache` so later runs make no network calls for this step.
    """
    if cache.exists():
        return json.loads(cache.read_text())

    def one(key):
        with open_remote_zip(files[key]) as z:
            return key, [[i.filename, i.compress_size, i.file_size] for i in z.infolist()]

    listing = {}
    with ThreadPoolExecutor(workers) as pool:
        jobs = [pool.submit(one, k) for k in files]
        for job in tqdm(as_completed(jobs), total=len(jobs), desc="Reading zip listings"):
            key, members = job.result()
            listing[key] = members
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(listing, indent=1, sort_keys=True))
    return listing


# The Zenodo record does NOT contain Train_Test_Split.zip (its download_data.sh
# points to it, but the URL is 404). The official splits are published in the
# authors' GitHub repo instead: one "Category/NN. Word/FILE.MOV" path per line.
SPLIT_URL = "https://raw.githubusercontent.com/AI4Bharat/INCLUDE/master/train_test_paths/include50_{}.txt"
SPLITS = ("train", "val", "test")


def fetch_splits(out_dir):
    """Download the INCLUDE-50 split lists (tiny text files). Returns {split: [paths]}."""
    out_dir.mkdir(parents=True, exist_ok=True)
    splits = {}
    for s in SPLITS:
        path = out_dir / f"include50_{s}.txt"
        if not path.exists():
            with urllib.request.urlopen(SPLIT_URL.format(s), timeout=60) as r:
                path.write_bytes(r.read())
        splits[s] = [ln.strip() for ln in path.read_text().splitlines() if ln.strip()]
    return splits


def norm(path):
    """Make paths comparable: lowercase, no spaces/underscores, no extension.

    'Days_and_Time/3. Monday/MVI_1.MOV' and 'Days and Time/3. Monday/mvi_1.mp4'
    both become 'daysandtime/3.monday/mvi_1'.
    Underscores in the FILE name are kept: MVI_0060.MOV and MVI_0060_.MOV are
    different videos (one is train, the other test).
    """
    path = os.path.splitext(path.strip().replace("\\", "/"))[0].lower()
    folders, _, name = path.rpartition("/")
    return re.sub(r"[\s_]+", "", folders) + "/" + re.sub(r"\s+", "", name)


def clean_word(folder):
    """'48. Hello' -> 'hello', 'Big large' stays 'big large'."""
    return re.sub(r"^\d+\.\s*", "", folder).strip().lower()


def build_index(listing, splits):
    """Match every split row to a zip member. Returns (rows, unmatched paths)."""
    full, short = {}, {}  # normalised full path / "word/file" -> (zip, member, size, csize)
    for zip_key, members in listing.items():
        for name, csize, size in members:
            if name.lower().endswith(VIDEO_EXT):
                hit = (zip_key, name, size, csize)
                full[norm(name)] = hit
                short[norm("/".join(name.split("/")[-2:]))] = hit

    rows, unmatched = [], []
    for split, paths in splits.items():
        for p in paths:
            hit = full.get(norm(p)) or short.get(norm("/".join(p.split("/")[-2:])))
            if hit is None:
                unmatched.append(p)
                continue
            zip_key, member, size, csize = hit
            rows.append({
                "word": clean_word(member.split("/")[1]),  # Category/NN. Word/[Extra/]file
                "split": split,
                "zip": zip_key,
                "member": member,
                "local_path": f"{CFG['paths']['raw_include']}/{member}",
                "size_bytes": size,          # uncompressed size on disk
                "_csize": csize,             # bytes to download (not written to CSV)
            })
    return rows, unmatched


def write_index(rows, path):
    """Save the index CSV that later scripts (e.g. tools/data_summary.py) read.

    downloaded = 1 if the video is on disk with the expected size, else 0.
    """
    cols = ["word", "split", "zip", "member", "local_path", "size_bytes", "downloaded"]
    for r in rows:
        dest = ROOT / r["local_path"]
        r["downloaded"] = int(dest.exists() and dest.stat().st_size == r["size_bytes"])
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def print_plan(rows, unmatched):
    """Dry run report: classes, per-class split counts, total download size."""
    counts = Counter((r["word"], r["split"]) for r in rows)
    words = sorted({r["word"] for r in rows})
    print(f"\nClasses: {len(words)}")
    print(f"{'word':<16}" + "".join(f"{s:>7}" for s in SPLITS))
    for w in words:
        print(f"{w:<16}" + "".join(f"{counts[(w, s)]:>7}" for s in SPLITS))
    totals = Counter(r["split"] for r in rows)
    print(f"{'TOTAL':<16}" + "".join(f"{totals[s]:>7}" for s in SPLITS))
    gb = sum(r["_csize"] for r in rows) / 1e9
    zips = len({r["zip"] for r in rows})
    print(f"\nVideos: {len(rows)} from {zips} zips | unmatched split rows: {len(unmatched)}")
    for p in unmatched[:10]:
        print("  unmatched:", p)
    print(f"TOTAL download size: {gb:.2f} GB (only these videos, not the 56.75 GB of zips)")


MAX_TRIES = 10     # attempts per video before giving up
RETRY_WAIT_S = 30  # base wait between attempts (grows each try)


def download_one(row, files):
    """Extract one video from its remote zip. Skips files already complete."""
    dest = ROOT / row["local_path"]
    if dest.exists() and dest.stat().st_size == row["size_bytes"]:
        return "skipped"
    dest.parent.mkdir(parents=True, exist_ok=True)
    part = dest.with_name(dest.name + ".part")
    local_zip = ROOT / CFG["paths"]["include_zips"] / row["zip"]
    if local_zip.exists():  # whole zip already on disk (e.g. via a download manager) -> no network
        try:
            with zipfile.ZipFile(local_zip) as z, z.open(row["member"]) as src, open(part, "wb") as out:
                shutil.copyfileobj(src, out, 1 << 20)  # zipfile also checks the CRC
            if part.stat().st_size != row["size_bytes"]:
                raise IOError(f"size mismatch for {row['member']}")
            part.rename(dest)
            return "extracted"
        except Exception as e:  # a bad local zip will not fix itself -> no retries
            part.unlink(missing_ok=True)
            return f"FAILED: {row['member']} ({e})"
    for attempt in range(1, MAX_TRIES + 1):
        try:
            with open_remote_zip(files[row["zip"]], 1 << 23) as z, z.open(row["member"]) as src, open(part, "wb") as out:
                shutil.copyfileobj(src, out, 1 << 20)  # zipfile also checks the CRC
            if part.stat().st_size != row["size_bytes"]:
                raise IOError(f"size mismatch for {row['member']}")
            part.rename(dest)
            return "downloaded"
        except Exception as e:  # network hiccup / server throttling -> wait, then try again
            err = e
            tqdm.write(f"retry {attempt}/{MAX_TRIES} {row['member']}: {e}")
            time.sleep(RETRY_WAIT_S * attempt)  # wait longer each time (30 s, 60 s, ...)
    part.unlink(missing_ok=True)
    return f"FAILED: {row['member']} ({err})"


def download_all(rows, files, workers):
    """Download every row in parallel threads, then print a summary."""
    results = Counter()
    failures = []
    with ThreadPoolExecutor(workers) as pool:
        jobs = [pool.submit(download_one, r, files) for r in rows]
        for job in tqdm(as_completed(jobs), total=len(jobs), desc="Downloading videos"):
            res = job.result()
            results[res.split(":")[0]] += 1
            if res.startswith("FAILED"):
                failures.append(res)
    print(dict(results))
    for f in failures:
        print(f)


def main():
    """Parse CLI args, build the INCLUDE-50 index, then dry-run or download."""
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--download", action="store_true", help="actually download the videos")
    ap.add_argument("--dry-run", action="store_true", help="only print the plan (default)")
    ap.add_argument("--workers", type=int, default=4, help="parallel downloads (default 4)")
    args = ap.parse_args()

    out = ROOT / CFG["paths"]["raw_include"]
    files = zenodo_files(CFG["data"]["zenodo_record"])
    listing = read_listings(files, out / "listing.json")
    splits = fetch_splits(out / "Train_Test_Split")
    rows, unmatched = build_index(listing, splits)
    write_index(rows, out / "include50_index.csv")
    print(f"Index written: {out / 'include50_index.csv'}")
    print_plan(rows, unmatched)

    if args.download and not args.dry_run:
        download_all(rows, files, args.workers)
        write_index(rows, out / "include50_index.csv")  # refresh the downloaded column
    else:
        print("\nDry run only. Re-run with --download to fetch the videos.")


CFG = yaml.safe_load((ROOT / "config.yaml").read_text())

if __name__ == "__main__":
    main()
