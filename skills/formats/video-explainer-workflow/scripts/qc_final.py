#!/usr/bin/env python3
"""qc_final.py — MANDATORY final QC on the assembled explainer (Phase 7).

Deterministically catches the known agent-bypass failure modes (all observed
in production/dev runs, 2026-07-21 matrix):
  hand-rolled assembly   -> no <final>.assembly.json sidecar        FAIL
  hand-rolled composite  -> missing/failed <block>.mp4.qc.json      FAIL
  wrong duration         -> probe vs (N-1)*clip+last                FAIL
  VFR container          -> r_frame_rate != avg_frame_rate          FAIL
  missing music bed      -> per-block audio floor < -50 dBFS        FAIL
  captions in top zone   -> persistent white text rows in top 28%   FAIL
  karaoke captions       -> srt entry rate > 30/min                 FAIL
  wall / over-long chunks-> srt entry > 4 words or > 42 chars       FAIL
  lingering captions     -> caption band ink does NOT drop in the
                            speech gaps the srt declares (>=1.5s)   FAIL

Usage:
  python3 scripts/qc_final.py FINAL.mp4 --blocks N [--clip-seconds 10]
      [--last-seconds R] [--srt subs.srt] [--no-music]
      [--composite-sidecars DIR]   # presenter mode: N PASS qc.json required

Exit 0 only if every applicable check passes. Paste the full output into the
Phase 7 report. If any line says FAIL: fix the cause and re-run — never ship.
"""
import argparse, glob, json, os, re, subprocess, sys
import numpy as np

def sh(args):
    return subprocess.run(args, capture_output=True, text=True).stdout.strip()

def probe(f):
    out = sh(["ffprobe","-v","error","-select_streams","v:0","-show_entries",
              "stream=width,height,r_frame_rate,avg_frame_rate","-show_entries",
              "format=duration","-of","json", f])
    j = json.loads(out); s = j["streams"][0]
    def fr(x):
        n, d = x.split("/"); d = float(d) or 1.0
        return float(n)/d
    return {"w": int(s["width"]), "h": int(s["height"]),
            "rfps": fr(s["r_frame_rate"]), "afps": fr(s.get("avg_frame_rate") or s["r_frame_rate"]),
            "dur": float(j["format"]["duration"])}

def audio_db_100ms(f):
    raw = subprocess.run(["ffmpeg","-v","error","-i",f,"-ac","1","-ar","16000",
                          "-f","s16le","-"], capture_output=True).stdout
    a = np.frombuffer(raw, np.int16).astype(np.float32)/32768.0
    n = len(a)//1600
    rms = np.sqrt((a[:n*1600].reshape(n,1600)**2).mean(1))
    return 20*np.log10(rms+1e-9)

def band_gray(f, crop, fps=8, w=192, h=56):
    raw = subprocess.run(["ffmpeg","-v","error","-i",f,"-vf",
                          f"crop={crop},scale={w}:{h},format=gray,fps={fps}",
                          "-f","rawvideo","-"], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8); m = len(fr)//(w*h)
    return fr[:m*w*h].reshape(m, h, w)

def parse_srt(p):
    out = []
    for b in re.split(r"\n\s*\n", open(p, encoding="utf-8").read().strip()):
        m = re.search(r"(\d\d:\d\d:\d\d[,.]\d+)\s*-->\s*(\d\d:\d\d:\d\d[,.]\d+)", b)
        if not m: continue
        def sec(t):
            t = t.replace(",", "."); hh, mm, ss = t.split(":")
            return int(hh)*3600 + int(mm)*60 + float(ss)
        lines = [l for l in b.splitlines() if "-->" not in l and not l.strip().isdigit()]
        text = " ".join(lines).strip()
        if text: out.append((sec(m.group(1)), sec(m.group(2)), text))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("final")
    ap.add_argument("--blocks", type=int, required=True)
    ap.add_argument("--clip-seconds", type=float, default=10.0)
    ap.add_argument("--last-seconds", type=float, default=None)
    ap.add_argument("--srt", default="")
    ap.add_argument("--no-music", action="store_true",
                    help="skip the music-bed check (voice-only mix was intended)")
    ap.add_argument("--composite-sidecars", default="",
                    help="presenter mode: dir that must hold one PASS *.qc.json per block")
    ap.add_argument("--assembly-sidecar", default="",
                    help="path to the assembly sidecar (default: <final>.assembly.json — "
                         "pass the PRE-subtitle one when checking a subbed file)")
    a = ap.parse_args()
    fails = []
    def check(name, ok, detail):
        print(f"[qc] {name}: {'PASS' if ok else 'FAIL'} — {detail}")
        if not ok: fails.append(name)

    try:
        p = probe(a.final)
    except (KeyError, ValueError, IndexError):
        print(f"[qc] readable: FAIL — {a.final} has no video stream (truncated/corrupt file?)")
        print("[qc] VERDICT: FAIL (readable)")
        sys.exit(1)
    last = a.last_seconds if a.last_seconds is not None else a.clip_seconds
    expect = (a.blocks-1)*a.clip_seconds + last

    # 1. assembly sidecar — proof assemble_blocks.sh ran (hand-assembly has none)
    side = a.assembly_sidecar or (a.final + ".assembly.json")
    if os.path.exists(side):
        try:
            j = json.load(open(side, encoding="utf-8"))
            ok = (j.get("script") == "assemble_blocks.sh" and int(j.get("blocks", -1)) == a.blocks)
            check("assembly-sidecar", ok,
                  f"{os.path.basename(side)} blocks={j.get('blocks')} gate='{j.get('gate','?')[:40]}...'")
        except (ValueError, KeyError) as e:
            check("assembly-sidecar", False, f"unreadable sidecar: {e}")
    else:
        check("assembly-sidecar", False,
              f"{os.path.basename(side)} missing — the final was NOT built by assemble_blocks.sh")

    # 2. duration + 3. CFR
    check("duration", abs(p["dur"]-expect) < 0.30, f"{p['dur']:.2f}s vs expected {expect:.1f}s")
    check("cfr", abs(p["rfps"]-p["afps"]) < 0.05, f"r={p['rfps']:.3f} avg={p['afps']:.3f} fps")

    # 4. music bed under/around the voice in EVERY block
    if not a.no_music:
        db = audio_db_100ms(a.final)
        floors = [float(np.percentile(db[int(b*a.clip_seconds*10):int((b+1)*a.clip_seconds*10)] , 15))
                  for b in range(a.blocks)]
        check("music-bed", min(floors) > -50,
              f"per-block floor15 {['%.0f' % f for f in floors]} dBFS (silent block = no bed)")

    # 5. captions must never sit in the top zone (white text rows, top 28%)
    top = band_gray(a.final, "in_w*0.55:in_h*0.28:in_w*0.225:0")
    white_top = float(((top > 235).mean((1, 2)) > 0.01).mean())
    check("no-top-captions", white_top < 0.50, f"white text rows in top band on {white_top*100:.0f}% of frames")

    # 6. captions vs their own srt
    if a.srt:
        caps = parse_srt(a.srt)
        rate = len(caps)/max(p["dur"]/60.0, 0.01)
        bad = [t for _, _, t in caps if len(t.split()) > 4 or len(t) > 42]
        check("caption-chunking", not bad, f"{len(caps)} entries, {len(bad)} over 4 words / 42 chars")
        check("caption-rate", rate <= 30, f"{rate:.0f} entries/min (karaoke word-highlight is 60+)")
        # release: in every srt-declared speech gap >=1.5s the caption band must
        # drop its ink vs the on-caption level (lingering/wall keeps it equal)
        band = band_gray(a.final, "in_w*0.55:in_h*0.32:in_w*0.225:in_h*0.60")
        ink = (band > 200).mean((1, 2)); fps = 8
        on = [ink[int((s+e)/2*fps)] for s, e, _ in caps if int((s+e)/2*fps) < len(ink)]
        gaps = [(e, caps[i+1][0]) for i, (s, e, _) in enumerate(caps[:-1])
                if caps[i+1][0]-e >= 1.5]
        off = [ink[int((g0+g1)/2*fps)] for g0, g1 in gaps if int((g0+g1)/2*fps) < len(ink)]
        if len(off) >= 2:
            ratio = (np.mean(off)+1e-6)/(np.mean(on)+1e-6)
            check("caption-release", ratio < 0.75,
                  f"band ink in {len(off)} declared gaps = {ratio:.2f}x of on-caption level (>=0.75 means captions linger)")
        else:
            print(f"[qc] caption-release: SKIP — only {len(off)} usable speech gaps >=1.5s in the srt")

    # 7. presenter composites must each carry a PASS matte-QC sidecar
    if a.composite_sidecars:
        scs = sorted(glob.glob(os.path.join(a.composite_sidecars, "*.qc.json")))
        good = 0
        for s in scs:
            try:
                if json.load(open(s, encoding="utf-8")).get("result") == "PASS": good += 1
            except ValueError:
                pass
        check("composite-sidecars", good >= a.blocks,
              f"{good} PASS sidecars in {a.composite_sidecars} (need {a.blocks}) — missing = hand-rolled composite")

    print(f"[qc] VERDICT: {'PASS' if not fails else 'FAIL (' + ', '.join(fails) + ')'}")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
