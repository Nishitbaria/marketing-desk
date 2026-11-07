#!/usr/bin/env bash
# assemble_final.sh — ONE command that turns block clips + per-block voice lines into
# ONE finished video. Deterministic, weak-agent-proof: the agent calls this once and
# never hand-rolls ffmpeg. Guarantees:
#   * fixed length  = N × clip-seconds (default 10) — video is NEVER shortened to audio
#     (asserted on the output; the script FAILS if the final duration is off by > 1s)
#   * one file out   (never part1/part2)
#   * NO time-stretch (no atempo / no speed change) — a voice line whose SPEECH is
#     longer than the window is a HARD ERROR (rewrite + regenerate upstream)
#   * a clip shorter than the window by > 0.5s is a HARD ERROR (regenerate the block)
#   * each block's voice is centered by its SPEECH, not by file length: leading and
#     trailing silence in the TTS file is measured (silencedetect) and ignored, so a
#     padded take can't shift the words off their scene
#   * pair sanity: if the numbers in a clip filename and its voice filename disagree
#     (block03 + voice05), you get a WARNING — the #1 cause of "audio on the wrong block"
#   * NO leading freeze (first ~1.5s checked with freezedetect) and no long frozen
#     TAIL (last ~2s checked) — a WARNING means regenerate that block
#   * LEVEL LAW — voice 1.0 always; the clips' own diegetic SFX are KEPT under
#     the voice at 0.12 (--sfx-vol, clamped <=0.20); the optional music bed sits
#     at 0.10 (--music-vol, clamped <=0.20); final loudnorm -16 LUFS
#
# Usage:
#   scripts/assemble_final.sh --out final.mp4 [--clip-seconds 10] [--music bed.mp3]
#       [--music-vol 0.10] [--sfx-vol 0.12] block01.mp4 voice01.wav block02.mp4 voice02.wav ...
#
# Pass clip/voice PAIRS in block order. Requires: ffmpeg, ffprobe, awk.
set -euo pipefail

OUT="final.mp4"; CLIP=10; MUSIC=""; MVOL="0.10"; SFXVOL="0.12"; ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --out) OUT="$2"; shift 2 ;;
    --clip-seconds) CLIP="$2"; shift 2 ;;
    --music) MUSIC="$2"; shift 2 ;;
    --music-vol) MVOL="$2"; shift 2 ;;
    --sfx-vol) SFXVOL="$2"; shift 2 ;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) ARGS+=("$1"); shift ;;
  esac
done
# LEVEL LAW: voice is ALWAYS 1.0; music defaults to 0.10 and SFX to 0.12, both
# hard-clamped at 0.20 so no caller can bury the narration in mush.
MVOL="$(awk -v v="$MVOL" 'BEGIN{v=v+0; if(v<0)v=0; if(v>0.2){print "WARN: --music-vol clamped to 0.20 (voice stays 1.0)" > "/dev/stderr"; v=0.2} printf "%.3f", v}')"
SFXVOL="$(awk -v v="$SFXVOL" 'BEGIN{v=v+0; if(v<0)v=0; if(v>0.2){print "WARN: --sfx-vol clamped to 0.20 (voice stays 1.0)" > "/dev/stderr"; v=0.2} printf "%.3f", v}')"
for b in ffmpeg ffprobe awk; do command -v "$b" >/dev/null 2>&1 || { echo "ERROR: '$b' not found" >&2; exit 1; }; done
n=${#ARGS[@]}
(( n >= 2 && n % 2 == 0 )) || { echo "ERROR: pass clip/voice PAIRS: clip1 voice1 clip2 voice2 ..." >&2; exit 1; }
pairs=$(( n / 2 ))
[[ -n "$MUSIC" && ! -f "$MUSIC" ]] && { echo "ERROR: --music file not found: $MUSIC" >&2; exit 1; }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
c0="${ARGS[0]}"
DIMS="$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0 "$c0")"
W="${DIMS%%,*}"; H="${DIMS##*,}"
FPS_RAW="$(ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of csv=p=0 "$c0")"
FPS="$(awk -F/ '{ if(NF==2 && $2>0) printf "%.4f",$1/$2; else print $1 }' <<< "$FPS_RAW")"; [ -z "$FPS" ] && FPS=30
echo "[1/3] ${pairs} blocks -> ${W}x${H} @ ${FPS}fps, fixed ${CLIP}s each; speech-centered, no atempo" >&2

LIST="$TMP/list.txt"; : > "$LIST"
for ((i=0;i<pairs;i++)); do
  clip="${ARGS[i*2]}"; voice="${ARGS[i*2+1]}"
  [[ -f "$clip"  ]] || { echo "ERROR: clip not found: $clip" >&2; exit 1; }
  [[ -f "$voice" ]] || { echo "ERROR: voice not found: $voice" >&2; exit 1; }
  # Pair sanity: numbers in the two filenames should match (block03 <-> voice03).
  cn="$(basename "$clip"  | grep -Eo '[0-9]+' | tail -1 || true)"
  vn="$(basename "$voice" | grep -Eo '[0-9]+' | tail -1 || true)"
  if [[ -n "$cn" && -n "$vn" ]] && (( 10#$cn != 10#$vn )); then
    echo "WARN: pair $((i+1)) mixes numbers: $(basename "$clip") + $(basename "$voice") — check the argument order (audio on the wrong block?)." >&2
  fi
  A="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$voice")"
  D="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$clip")"
  # SPEECH bounds: ignore leading/trailing silence of the TTS file when centering.
  EVENTS="$(ffmpeg -i "$voice" -af silencedetect=noise=-45dB:d=0.25 -f null - 2>&1 | grep -Eo 'silence_(start|end): *-?[0-9.]+' || true)"
  read -r SS SE <<< "$(awk -v A="$A" '
    /silence_start/ { s=$NF+0; if(first==""){first=s}; last=s; open=1; next }
    /silence_end/   { e=$NF+0; if(first!="" && first<0.1 && ssdone==""){ss=e; ssdone=1};
                      e_last=e; s_before=last; open=0 }
    END {
      if (open==1)                      se=last;        # file ended inside silence
      else if (e_last>0 && A-e_last<0.2) se=s_before;   # EOF auto-closed the tail silence
      else                               se=A;          # speech runs to the end
      printf "%.3f %.3f", ss+0, se+0 }' <<< "$EVENTS")"
  [[ -z "${SS:-}" ]] && SS=0; [[ -z "${SE:-}" ]] && SE="$A"
  SPEECH="$(awk -v a="$SS" -v b="$SE" 'BEGIN{d=b-a; if(d<=0)d=0; printf "%.3f", d}')"
  # A degenerate detect (all-silence or no events) falls back to the full file.
  awk -v s="$SPEECH" 'BEGIN{exit (s<0.3)?0:1}' && { SS=0; SE="$A"; SPEECH="$A"; }
  # Pausey-take probe: internal silences >=0.8s INSIDE the speech (a flowing line has
  # none; every full stop the TTS honours costs ~0.7s of dead air on screen).
  read -r IPN IPMAX <<< "$(awk -v lo="$SS" -v hi="$SE" '
    /silence_start/ { s=$NF+0; open=1; next }
    /silence_end/   { e=$NF+0; if(open==1 && s>lo+0.1 && e<hi-0.1 && e-s>=0.8){n++; if(e-s>mx)mx=e-s}; open=0 }
    END{ printf "%d %.2f", n+0, mx+0 }' <<< "$EVENTS")"
  [[ "${IPN:-0}" != "0" ]] && echo "WARN: voice $((i+1)) ($voice) has ${IPN} internal pause(s) >=0.8s (longest ${IPMAX}s) — pausey take: rewrite the line as ONE flowing clause (fewer full stops) and regenerate." >&2
  # HARD checks — the golden rules, enforced (no atempo, no shortened video):
  awk -v s="$SPEECH" -v c="$CLIP" 'BEGIN{exit (s > c+0.25) ? 0 : 1}' && {
    echo "ERROR: voice $((i+1)) ($voice) carries ${SPEECH}s of speech > ${CLIP}s window — REWRITE the line shorter and regenerate (never atempo/speed-up)." >&2; exit 1; }
  awk -v d="$D" -v c="$CLIP" 'BEGIN{exit (d < c-0.5) ? 0 : 1}' && {
    echo "ERROR: clip $((i+1)) ($clip) is only ${D}s (<${CLIP}s) — REGENERATE the block; a held still frame is not a scene." >&2; exit 1; }
  # Freeze probes: head (first ~1.5s) and tail (last ~2s). Warnings — regenerate per rule 21.
  FRZH="$(ffmpeg -v info -t 1.5 -i "$clip" -vf "freezedetect=n=-60dB:d=1.0" -an -f null - 2>&1 | grep -c freeze_start || true)"
  [[ "$FRZH" != "0" ]] && echo "WARN: clip $((i+1)) ($clip) opens on ~static frames — regenerate this block (rule 21)." >&2
  FRZT="$(ffmpeg -v info -sseof -2 -i "$clip" -vf "freezedetect=n=-60dB:d=1.2" -an -f null - 2>&1 | grep -c freeze_start || true)"
  [[ "$FRZT" != "0" ]] && echo "WARN: clip $((i+1)) ($clip) ends on ~static frames (frozen tail) — consider regenerating." >&2
  # Center the SPEECH in the fixed window: put speech start at (CLIP - speech)/2,
  # compensating for the file's own leading silence. NO atempo.
  PAD_MS="$(awk -v ss="$SS" -v sp="$SPEECH" -v c="$CLIP" 'BEGIN{t0=(c-sp)/2; if(t0<0)t0=0; d=t0-ss; if(d<0)d=0; printf "%d", d*1000}')"
  out="$TMP/b_$(printf '%03d' "$i").mp4"
  # Keep the clip's own diegetic SFX under the voice (whooshes, sparkles, paper):
  # clip audio at SFXVOL (default 0.12), voice at 1.0. Clips without an audio
  # stream fall back to voice-only.
  HASAUD="$(ffprobe -v error -select_streams a:0 -show_entries stream=codec_type -of csv=p=0 "$clip" | head -1)"
  if [[ "$HASAUD" == "audio" ]]; then
    FC="[0:v]scale=${W}:${H}:force_original_aspect_ratio=decrease,pad=${W}:${H}:(ow-iw)/2:(oh-ih)/2:black,fps=${FPS},format=yuv420p,setsar=1,tpad=stop_mode=clone:stop_duration=${CLIP}[v];[1:a]adelay=${PAD_MS}:all=1,apad[vo];[0:a]volume=${SFXVOL},apad[sfx];[sfx][vo]amix=inputs=2:duration=first:normalize=0[a]"
  else
    FC="[0:v]scale=${W}:${H}:force_original_aspect_ratio=decrease,pad=${W}:${H}:(ow-iw)/2:(oh-ih)/2:black,fps=${FPS},format=yuv420p,setsar=1,tpad=stop_mode=clone:stop_duration=${CLIP}[v];[1:a]adelay=${PAD_MS}:all=1,apad[a]"
  fi
  ffmpeg -y -loglevel error -i "$clip" -i "$voice" \
    -filter_complex "$FC" \
    -map "[v]" -map "[a]" -t "$CLIP" -c:v libx264 -preset veryfast -crf 20 -c:a aac -b:a 192k "$out"
  echo "file '$out'" >> "$LIST"
  printf '  block %02d: clip %.2fs, file %.2fs, speech %.2fs (%.2f..%.2f) -> speech starts at %.2fs\n' \
    "$((i+1))" "$D" "$A" "$SPEECH" "$SS" "$SE" "$(awk -v p="$PAD_MS" -v ss="$SS" 'BEGIN{printf "%.2f", p/1000+ss}')" >&2
done

VOTRACK="$TMP/joined.mp4"
echo "[2/3] concat -> single track" >&2
ffmpeg -y -loglevel error -f concat -safe 0 -i "$LIST" -c:v libx264 -preset veryfast -crf 20 -c:a aac -movflags +faststart "$VOTRACK"

echo "[3/3] finalize -> $OUT" >&2
# Two-pass LINEAR loudnorm: one constant gain for the whole file, so the
# voice/SFX/music ratios set above are PRESERVED (single-pass dynamic loudnorm
# pumps quiet SFX-only stretches up toward the voice = mush).
ln2_args() { # $1 = input file -> prints measured loudnorm args
  ffmpeg -hide_banner -i "$1" -af "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json" -f null - 2>&1 \
  | awk '/"input_i"/{i=$3}/"input_tp"/{t=$3}/"input_lra"/{l=$3}/"input_thresh"/{h=$3}/"target_offset"/{o=$3}
         {gsub(/[",]/,"",i);gsub(/[",]/,"",t);gsub(/[",]/,"",l);gsub(/[",]/,"",h);gsub(/[",]/,"",o)}
         END{printf "measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s", i,t,l,h,o}'
}
if [[ -n "$MUSIC" ]]; then
  MIXED="$TMP/mixed.mp4"
  ffmpeg -y -loglevel error -i "$VOTRACK" -stream_loop -1 -i "$MUSIC" \
    -filter_complex "[1:a]volume=${MVOL}[m];[0:a][m]amix=inputs=2:duration=first:normalize=0[a]" \
    -map 0:v -map "[a]" -shortest -c:v copy -c:a aac -b:a 192k "$MIXED"
  SRC="$MIXED"
else
  SRC="$VOTRACK"
fi
LNARGS="$(ln2_args "$SRC")"
if [[ "$LNARGS" == *measured_I=-* ]]; then
  ffmpeg -y -loglevel error -i "$SRC" -af "loudnorm=I=-16:TP=-1.5:LRA=11:${LNARGS}:linear=true" -c:v copy -c:a aac -b:a 192k "$OUT"
else
  echo "WARN: loudness measurement failed — falling back to single-pass loudnorm." >&2
  ffmpeg -y -loglevel error -i "$SRC" -af "loudnorm=I=-16:TP=-1.5:LRA=11" -c:v copy -c:a aac -b:a 192k "$OUT"
fi

# Assert the fixed-length guarantee (GATE 6): |actual - N*CLIP| <= 1s.
TOT="$(awk -v n="$pairs" -v c="$CLIP" 'BEGIN{printf "%g", n*c}')"
FDUR="$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")"
awk -v d="$FDUR" -v e="$TOT" 'BEGIN{x=d-e; if(x<0)x=-x; exit (x<=1)?0:1}' || {
  echo "ERROR: final duration ${FDUR}s != expected ${TOT}s (±1s) — do NOT deliver; investigate the inputs." >&2; exit 1; }

# Integrity: the final must have an audio stream spanning the video, and must FULLY
# DECODE with zero errors (catches corrupted/truncated streams that stream-copy hides).
ADUR="$(ffprobe -v error -select_streams a:0 -show_entries stream=duration -of csv=p=0 "$OUT" | head -1)"
[[ -z "$ADUR" || "$ADUR" == "N/A" ]] && { echo "ERROR: final has no readable audio stream — do NOT deliver." >&2; exit 1; }
awk -v a="$ADUR" -v d="$FDUR" 'BEGIN{x=a-d; if(x<0)x=-x; exit (x<=1.5)?0:1}' || {
  echo "ERROR: audio stream ${ADUR}s vs video ${FDUR}s — mismatched/truncated audio; do NOT deliver." >&2; exit 1; }
DERR="$( (ffmpeg -v error -xerror -i "$OUT" -f null - ) 2>&1 | head -3 || true)"
[[ -n "$DERR" ]] && { echo "ERROR: final failed decode validation — corrupted stream; do NOT deliver:" >&2; echo "$DERR" >&2; exit 1; }
echo "DONE: $OUT  (ONE file, ${pairs} blocks x ${CLIP}s = ${TOT}s, actual ${FDUR}s; decode-validated)" >&2
