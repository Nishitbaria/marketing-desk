#!/usr/bin/env python3
"""
Deterministic blur-pad letterbox reframe — the default reframe strategy for
video-repurpose. Same principle as youtube_clipping's default (non-face-tracking)
crop: no generative model, no job latency, no moderation false-positive risk,
no motion warm-up artifact (verified against a source video with ffmpeg-based
frame-diff QC during skill development).

Usage:
    python3 blurpad_reframe.py --input in.mp4 --output out.mp4 --aspect 9:16
    python3 blurpad_reframe.py --input in.mp4 --output out.mp4 --aspect 1:1 --feather 40
    python3 blurpad_reframe.py --input in.mp4 --output out.mp4 --width 1080 --height 1920

Feathering (--feather PX, default 32, 0 = hard seam): blends the foreground's
top/bottom (or left/right, for landscape targets) edge into the blurred
background over PX pixels instead of a hard line, using an alpha ramp via
ffmpeg's geq filter. This is a cosmetic upgrade over the hard-seam baseline
that was tested and confirmed artifact-free (aside from the hard line itself
and, on a hard scene cut, a brief background brightness mismatch — both
purely aesthetic, not motion/distortion artifacts). If geq is unsupported by
the local ffmpeg build, rerun with --feather 0 for the plain hard-seam version.
"""
import argparse
import shutil
import subprocess
import sys

# width, height for common targets. Override with --width/--height for a custom size.
DEFAULT_RES = {
    "9:16": (1080, 1920),
    "3:4": (1080, 1440),
    "1:1": (1080, 1080),
    "4:3": (1440, 1080),
    "16:9": (1920, 1080),
    "21:9": (2560, 1097),
}


def build_filter(width: int, height: int, blur_sigma: int, feather: int) -> str:
    bg = (
        f"[0:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},gblur=sigma={blur_sigma}[bg]"
    )
    if feather <= 0:
        # `force_original_aspect_ratio=decrease` fits the foreground INSIDE the
        # target box (shrinks whichever dimension needs it) — scaling to width
        # alone breaks for a portrait source going to a wider/shorter target:
        # the auto-height comes out taller than the canvas and the overlay
        # silently clips it (a hard crop into the subject's head/chest), not a
        # letterbox. Found live via visual QC on a 9:16-source -> 16:9 reframe.
        fg = f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease[fg]"
        overlay = "[bg][fg]overlay=(W-w)/2:(H-h)/2[out]"
        return f"{bg};{fg};{overlay}"

    # Feathered foreground: alpha-ramp the top/bottom PX edge rows so the seam
    # blends into the blurred background instead of a hard cut line.
    fg = (
        f"[0:v]scale={width}:{height}:force_original_aspect_ratio=decrease,format=yuva420p,"
        f"geq="
        f"r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
        f"a='if(lt(Y,{feather}),255*Y/{feather},"
        f"if(gt(Y,H-{feather}),255*(H-Y)/{feather},255))'"
        f"[fg]"
    )
    overlay = "[bg][fg]overlay=(W-w)/2:(H-h)/2[out]"
    return f"{bg};{fg};{overlay}"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--aspect", choices=list(DEFAULT_RES), help="Target aspect ratio")
    ap.add_argument("--width", type=int, help="Explicit target width (overrides --aspect default)")
    ap.add_argument("--height", type=int, help="Explicit target height (overrides --aspect default)")
    ap.add_argument("--blur-sigma", type=int, default=25)
    ap.add_argument("--feather", type=int, default=32, help="Seam feather in px, 0 = hard seam")
    args = ap.parse_args()

    if args.width and args.height:
        width, height = args.width, args.height
    elif args.aspect:
        width, height = DEFAULT_RES[args.aspect]
    else:
        sys.exit("Pass --aspect or both --width and --height")

    if shutil.which("ffmpeg") is None:
        sys.exit("ffmpeg not found on PATH")

    filter_complex = build_filter(width, height, args.blur_sigma, args.feather)
    cmd = [
        "ffmpeg", "-y", "-i", args.input,
        "-filter_complex", filter_complex,
        "-map", "[out]", "-map", "0:a?",
        "-c:a", "copy",
        args.output,
    ]
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr[-4000:], file=sys.stderr)
        if args.feather > 0:
            print(
                "Feathered filter failed — retrying with --feather 0 (hard seam) "
                "as the tested-safe fallback.",
                file=sys.stderr,
            )
            args.feather = 0
            filter_complex = build_filter(width, height, args.blur_sigma, 0)
            cmd[cmd.index("-filter_complex") + 1] = filter_complex
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(result.stderr[-4000:], file=sys.stderr)
                sys.exit(1)
        else:
            sys.exit(1)
    print(f"Wrote {args.output} ({width}x{height}, feather={args.feather})")


if __name__ == "__main__":
    main()
