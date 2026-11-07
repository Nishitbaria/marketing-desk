#!/usr/bin/env bash
# burn_subtitles.sh — burn stable, styled subtitles onto a FINISHED video from an
# .srt, using ffmpeg + libass. One look: handwritten dark ink on a cream
# "paper-label" box, bottom-centre, soft shadow. Exact timing, zero jitter.
#
# Usage:
#   scripts/burn_subtitles.sh --in video.mp4 --srt subs.srt --out final.mp4
#     [--font "Caveat"] [--fontsdir DIR] [--fontsize N] [--marginv N]
#
# Font: a handwritten font must be available. Bundle one at scripts/fonts/ (e.g.
# Caveat-Regular.ttf, SIL OFL) — the script auto-uses scripts/fonts as fontsdir.
# Without it, libass falls back to a default (not handwritten).
#
# Requires: ffmpeg (with libass).
set -euo pipefail

IN=""; SRT=""; OUT="final_subtitled.mp4"; FONT="Caveat"; FONTSDIR=""; FSIZE=18; MV=60
while [[ $# -gt 0 ]]; do
  case "$1" in
    --in) IN="$2"; shift 2 ;;
    --srt) SRT="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    --font) FONT="$2"; shift 2 ;;
    --fontsdir) FONTSDIR="$2"; shift 2 ;;
    --fontsize) FSIZE="$2"; shift 2 ;;
    --marginv) MV="$2"; shift 2 ;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done
[[ -n "$IN" && -f "$IN" ]] || { echo "ERROR: --in video not found" >&2; exit 1; }
[[ -n "$SRT" && -f "$SRT" ]] || { echo "ERROR: --srt file not found" >&2; exit 1; }
command -v ffmpeg >/dev/null 2>&1 || { echo "ERROR: ffmpeg not found" >&2; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
[[ -z "$FONTSDIR" && -d "$SCRIPT_DIR/fonts" ]] && FONTSDIR="$SCRIPT_DIR/fonts"

# ASS colours are &HAABBGGRR. Ink = warm near-black; label = cream; shadow = soft black.
STYLE="FontName=${FONT},Fontsize=${FSIZE},PrimaryColour=&H00222222&,OutlineColour=&H00E6EFF4&,BackColour=&H66000000&,BorderStyle=3,Outline=10,Shadow=3,Alignment=2,MarginV=${MV},Bold=0"

if [[ -n "$FONTSDIR" ]]; then
  VF="subtitles=${SRT}:fontsdir=${FONTSDIR}:force_style='${STYLE}'"
else
  VF="subtitles=${SRT}:force_style='${STYLE}'"
fi

echo "[burn] $IN + $SRT -> $OUT  (font=$FONT, fontsdir=${FONTSDIR:-<none>})" >&2
ffmpeg -y -loglevel error -i "$IN" -vf "$VF" \
  -c:v libx264 -preset veryfast -crf 20 -c:a copy -movflags +faststart "$OUT"
echo "DONE: $OUT" >&2
