#!/usr/bin/env bash
# trim_static_head.sh IN.mp4 OUT.mp4 [P1_REF.png] — rescue for a "photo start":
# gemini_omni sometimes seeds the person reference as the literal frame 0, so
# the clip opens frozen on the photo for ~0.2–0.5s before motion kicks in
# (probabilistic, server-side).
#
# WITH P1_REF (recommended — safe to run unconditionally on every clip): the
# script first measures frame 0 against the reference (mean abs RGB diff;
# clean clips sit at 25–75, seeded ones < ~15, gate at 20). Clean → prints
# "SEEDCHK: clean" + "TRIM: 0.0s" and copies the file through untouched (a
# live clip's opening speech is never clipped). Seeded → falls through to the
# motion cut below. Seeded AND no motion in the probe window → prints "DEAD"
# — regenerate that P2 block upstream.
#
# WITHOUT P1_REF (legacy): motion cut always runs and trims at least 0.1s —
# only use this form on clips already known to be seeded.
#
# The cut: find where real motion starts (adaptive threshold: 60% of the
# in-window diff peak, bounded [8,15], probe window 1.6s @10fps on a 240px gray
# proxy), cut VIDEO+AUDIO together (lipsync preserved), clone-pad the last
# frame + pad silence back to the original duration. Prints "TRIM: X.Xs".
#
# RUN THIS ON THE VOICE-CHANGED CLIP (after P3), never before: change_voice
# takes server job ids, so a locally trimmed file cannot be revoiced.
#
# Requires: ffmpeg, ffprobe, python3 (+numpy)
set -euo pipefail
IN="$1"; OUT="$2"; REF="${3:-}"
TRIM=$(python3 - "$IN" "$REF" <<'PY'
import subprocess, sys
import numpy as np
inp, ref = sys.argv[1], sys.argv[2]
probe = subprocess.run(["ffprobe","-v","error","-select_streams","v:0",
    "-show_entries","stream=width,height","-of","csv=p=0",inp],
    capture_output=True,text=True,check=True).stdout.strip().split(",")
w0,h0=int(probe[0]),int(probe[1])
h = int(round(h0 * 240 / w0));  h -= h % 2

if ref:
    def rgb0(path):
        r = subprocess.run(["ffmpeg","-v","error","-i",path,"-frames:v","1",
            "-vf",f"scale=240:{h}","-f","rawvideo","-pix_fmt","rgb24","-"],
            capture_output=True, check=True).stdout
        return np.frombuffer(r[:h*240*3],dtype=np.uint8).reshape(h,240,3).astype(int)
    diff = float(np.abs(rgb0(inp)-rgb0(ref)).mean())
    if diff >= 20:
        print(f"SEEDCHK: clean (frame0-vs-ref diff {diff:.1f}) 0.0", file=sys.stderr)
        print("0.0"); sys.exit()
    print(f"SEEDCHK: SEEDED (frame0-vs-ref diff {diff:.1f})", file=sys.stderr)

p = subprocess.run(["ffmpeg","-v","error","-t","1.6","-i",inp,
    "-vf","fps=10,scale=240:-2,format=gray","-f","rawvideo","-"],
    capture_output=True, check=True)
buf = p.stdout
n = len(buf)//(240*h)
fr = np.frombuffer(buf[:n*240*h],dtype=np.uint8).reshape(n,h,240).astype(int)
d = [float(np.abs(fr[i]-fr[0]).mean()) for i in range(1,n)]
if not d: print("0.0"); sys.exit()
peak = max(d)
if peak < 5:  # no motion in the probe window
    if ref: print("DEAD: clip frozen through the probe window — regenerate this block", file=sys.stderr)
    print("0.0"); sys.exit()
thr = min(max(peak*0.6, 8), 15)
t = 0.0
for i,v in enumerate(d):
    if v > thr:
        t = (i+1)/10.0
        break
print(f"{t:.1f}")
PY
)
echo "TRIM: ${TRIM}s"
if [[ "$TRIM" == "0.0" ]]; then cp "$IN" "$OUT"; exit 0; fi
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
ffmpeg -y -v error -ss "$TRIM" -i "$IN" -filter_complex \
  "[0:v]tpad=stop_mode=clone:stop_duration=${TRIM}[v];[0:a]apad=pad_dur=${TRIM}[a]" \
  -map "[v]" -map "[a]" -t "$DUR" -c:v libx264 -crf 18 -preset veryfast -pix_fmt yuv420p -c:a aac "$OUT"
