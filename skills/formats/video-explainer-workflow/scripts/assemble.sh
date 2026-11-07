#!/usr/bin/env bash
# assemble.sh — concatenate explainer clips and center the narration on top.
#
# Usage:
#   scripts/assemble.sh --out FILE --audio <url|file> [--clip-seconds N] CLIP1 CLIP2 ... CLIPN
#
# Args:
#   --out FILE        output path (default: explainer.mp4)
#   --audio SRC       narration audio, URL or local file (required)
#   --clip-seconds N  force every clip to exactly N seconds (default: 10)
#   CLIP1..N          clip URLs or local files, IN STORY ORDER (>=1)
#
# Behavior:
#   - downloads any http(s) inputs to a temp dir
#   - forces every clip to exactly --clip-seconds (clones last frame if a clip
#     is short, trims if long) so total video = N * clip-seconds exactly
#   - normalizes all clips to the first clip's resolution, 30fps, h264/yuv420p
#   - concatenates the clips in order (clip audio is dropped)
#   - lays the narration on as the master audio, CENTERED over the video:
#     pads silence on both sides if the narration is short, trims it
#     symmetrically if it is long
#
# Requires: ffmpeg, ffprobe, curl
set -euo pipefail

OUT="explainer.mp4"
AUDIO=""
CLIP_SECONDS=10
CLIPS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --out)          OUT="$2"; shift 2 ;;
    --audio)        AUDIO="$2"; shift 2 ;;
    --clip-seconds) CLIP_SECONDS="$2"; shift 2 ;;
    -h|--help)      grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *)              CLIPS+=("$1"); shift ;;
  esac
done

for bin in ffmpeg ffprobe curl awk; do
  command -v "$bin" >/dev/null 2>&1 || { echo "ERROR: '$bin' not found in PATH" >&2; exit 1; }
done
[[ -n "$AUDIO" ]] || { echo "ERROR: --audio is required" >&2; exit 1; }
[[ ${#CLIPS[@]} -ge 1 ]] || { echo "ERROR: pass at least one clip (in order)" >&2; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

fetch() { # $1=src $2=dest
  local src="$1" dest="$2"
  if [[ "$src" == http://* || "$src" == https://* ]]; then
    echo "  downloading $src" >&2
    curl -fsSL "$src" -o "$dest"
  else
    [[ -f "$src" ]] || { echo "ERROR: file not found: $src" >&2; exit 1; }
    cp "$src" "$dest"
  fi
}

echo "[1/4] fetching ${#CLIPS[@]} clips + narration" >&2
i=0; RAW=()
for c in "${CLIPS[@]}"; do
  dst="$TMP/raw_$(printf '%02d' "$i").mp4"; fetch "$c" "$dst"; RAW+=("$dst"); i=$((i+1))
done
AUD="$TMP/narration_src"; fetch "$AUDIO" "$AUD"

# Target geometry = first clip's resolution.
DIMS="$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "${RAW[0]}")"
W="${DIMS%%,*}"; H="${DIMS##*,}"
echo "[2/4] normalizing ${#RAW[@]} clips to ${W}x${H}, 30fps, ${CLIP_SECONDS}s each" >&2

LIST="$TMP/concat.txt"; : > "$LIST"
i=0
for r in "${RAW[@]}"; do
  norm="$TMP/norm_$(printf '%02d' "$i").mp4"
  # tpad clones the last frame to reach CLIP_SECONDS if short; -t trims if long.
  ffmpeg -y -loglevel error -i "$r" \
    -vf "scale=${W}:${H}:force_original_aspect_ratio=decrease,pad=${W}:${H}:(ow-iw)/2:(oh-ih)/2:black,fps=30,format=yuv420p,setsar=1,tpad=stop_mode=clone:stop_duration=${CLIP_SECONDS}" \
    -t "$CLIP_SECONDS" -an -c:v libx264 -preset veryfast -crf 20 "$norm"
  echo "file '$norm'" >> "$LIST"; i=$((i+1))
done

echo "[3/4] concatenating clips" >&2
SILENT="$TMP/silent.mp4"
ffmpeg -y -loglevel error -f concat -safe 0 -i "$LIST" -c copy "$SILENT"

V="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$SILENT")"
A="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$AUD")"

# Warn on large mismatches: trimming loses words, big pads leave silence.
awk -v v="$V" -v a="$A" 'BEGIN{
  d=a-v;
  if (d>2)       printf "WARNING: narration is %.1fs LONGER than the video; centering will trim %.1fs from each end (may cut the hook/payoff). Shorten the script, or add clips so total = ceil(audio/clip-seconds).\n", d, d/2 > "/dev/stderr";
  else if (d<-8) printf "WARNING: narration is %.1fs SHORTER than the video; %.1fs of silence will pad each end. Lengthen the script or reduce clips.\n", -d, -d/2 > "/dev/stderr";
}'

# Center the narration over the video.
#   pad_start = max(0, (V-A)/2)  -> silence before narration if it's short
#   audio_ss  = max(0, (A-V)/2)  -> trim narration head if it's long
PAD_MS="$(awk -v v="$V" -v a="$A" 'BEGIN{d=(v-a)/2; if(d<0)d=0; printf "%d", d*1000}')"
AUDIO_SS="$(awk -v v="$V" -v a="$A" 'BEGIN{d=(a-v)/2; if(d<0)d=0; printf "%.3f", d}')"
echo "[4/4] muxing narration centered (video ${V}s, audio ${A}s, pad ${PAD_MS}ms, trim ${AUDIO_SS}s) -> $OUT" >&2

ffmpeg -y -loglevel error -i "$SILENT" -ss "$AUDIO_SS" -i "$AUD" \
  -filter_complex "[1:a]adelay=${PAD_MS}:all=1,apad[a]" \
  -map 0:v:0 -map "[a]" \
  -c:v copy -c:a aac -b:a 192k -t "$V" \
  -movflags +faststart "$OUT"

echo "DONE: $OUT" >&2
