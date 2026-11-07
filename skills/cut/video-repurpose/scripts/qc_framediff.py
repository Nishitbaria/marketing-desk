#!/usr/bin/env python3
"""
QC frame-diff check for video-repurpose. Flags a candidate reframe/output that
looks "frozen" (near-static) at points where the source video is actually
moving — this is exactly how the AI-reframe motion warm-up artifact and the
blur-pad fidelity were both verified during skill development.

Method: extract a still frame from SOURCE and CANDIDATE at each timestamp,
compute mean absolute grayscale pixel difference against the PREVIOUS
timestamp's frame for each video independently, then compare the two motion
profiles. A timestamp is flagged when the source shows real motion but the
candidate is anomalously flat there.

Usage:
    python3 qc_framediff.py --source in.mp4 --candidate out.mp4 \
        --timestamps 1,2,3,4,5,8,12 --workdir /tmp/qc

    # or auto-sample N evenly spaced points across the shorter duration:
    python3 qc_framediff.py --source in.mp4 --candidate out.mp4 --samples 12

Requires: ffmpeg on PATH, Pillow + numpy (pip install pillow numpy if missing).
"""
import argparse
import json
import pathlib
import subprocess
import sys
import tempfile

try:
    import numpy as np
    from PIL import Image
except ImportError:
    sys.exit("Requires Pillow and numpy: pip install pillow numpy")


def ffprobe_duration(path: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True,
    )
    return float(out.stdout.strip())


def extract_frame(path: str, t: float, out_path: pathlib.Path) -> bool:
    result = subprocess.run(
        ["ffmpeg", "-y", "-ss", str(t), "-i", path, "-vframes", "1", str(out_path)],
        capture_output=True, text=True,
    )
    return result.returncode == 0 and out_path.exists()


def load_gray(path: pathlib.Path):
    return np.asarray(Image.open(path).convert("L"), dtype=np.int16)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", required=True)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--timestamps", help="Comma-separated seconds, e.g. 1,2,3,4,5")
    ap.add_argument("--samples", type=int, default=10, help="Auto-sample N points if --timestamps omitted")
    ap.add_argument("--flat-threshold", type=float, default=1.5,
                     help="Candidate diff below this is 'flat' (default 1.5)")
    ap.add_argument("--ratio-threshold", type=float, default=3.0,
                     help="Flag when source_diff / candidate_diff exceeds this (default 3.0)")
    ap.add_argument("--workdir", default=None)
    args = ap.parse_args()

    if args.timestamps:
        times = [float(t) for t in args.timestamps.split(",")]
    else:
        dur = min(ffprobe_duration(args.source), ffprobe_duration(args.candidate))
        step = dur / (args.samples + 1)
        times = [round(step * (i + 1), 2) for i in range(args.samples)]

    workdir = pathlib.Path(args.workdir) if args.workdir else pathlib.Path(tempfile.mkdtemp(prefix="qc_framediff_"))
    (workdir / "src").mkdir(parents=True, exist_ok=True)
    (workdir / "cand").mkdir(parents=True, exist_ok=True)

    rows = []
    prev_s = prev_c = None
    flags = []
    for t in times:
        sp = workdir / "src" / f"{t}.jpg"
        cp = workdir / "cand" / f"{t}.jpg"
        ok_s = extract_frame(args.source, t, sp)
        ok_c = extract_frame(args.candidate, t, cp)
        if not (ok_s and ok_c):
            rows.append({"t": t, "error": "frame extraction failed"})
            continue
        gs, gc = load_gray(sp), load_gray(cp)
        ds = None if prev_s is None else float(np.abs(gs - prev_s).mean())
        dc = None if prev_c is None else float(np.abs(gc - prev_c).mean())
        row = {"t": t, "source_diff": ds, "candidate_diff": dc}
        if ds is not None and dc is not None:
            flat = dc < args.flat_threshold
            source_moving = ds > args.flat_threshold
            ratio_bad = ds > 0 and (dc == 0 or ds / max(dc, 1e-6) > args.ratio_threshold)
            if flat and source_moving and ratio_bad:
                row["flag"] = "candidate looks frozen while source is moving"
                flags.append(t)
        rows.append(row)
        prev_s, prev_c = gs, gc

    report = {"timestamps_checked": times, "rows": rows, "flagged_timestamps": flags,
              "verdict": "FAIL — possible freeze/motion-fidelity artifact" if flags else "PASS"}
    print(json.dumps(report, indent=2))
    sys.exit(1 if flags else 0)


if __name__ == "__main__":
    main()
