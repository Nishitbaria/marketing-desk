#!/bin/bash
# Turns a beats file into one WAV per beat. Tries Kokoro, then macOS say, then
# no audio, so a missing voice tool never stops the chain.
# Usage: skills/voice/make-voice.sh <slug>
# Reads renders/<slug>-voice/beats.txt, one "start|end|spoken line" per beat.
# Set VOICE_TIER to kokoro, say or none to force a tier.
# Kokoro runs through the hyperframes tts command. Renders stay on Remotion.
set -u

root="$(cd "$(dirname "$0")/../.." && pwd)"
slug="${1:-}"
out="$root/renders/$slug-voice"
if [ -z "$slug" ] || [ ! -f "$out/beats.txt" ]; then
  echo "ERROR: need renders/<slug>-voice/beats.txt" >&2
  exit 2
fi

py="${HYPERFRAMES_PYTHON:-$root/.venv/bin/python}"
[ -x "$py" ] || py="$root/.venv/Scripts/python.exe"
[ -x "$py" ] || py=python3
kokoro_speed="${VOICE_SPEED:-0.8}"

speak() { # tier, text, wav
  case "$1" in
    kokoro) HYPERFRAMES_PYTHON="$py" npx --yes hyperframes@0.9.19 tts "$2" \
      --voice af_heart --speed "$kokoro_speed" --output "$3" >/dev/null 2>&1 ;;
    say) say -v Samantha -r 140 -o "$3" --data-format=LEI16@44100 "$2" ;;
  esac
}

available() { # tier
  case "$1" in
    kokoro) "$py" -c 'import kokoro_onnx' >/dev/null 2>&1 ;;
    say) command -v say >/dev/null 2>&1 ;;
    none) true ;;
    *) false ;;
  esac
}

generate() { # tier: writes every beat, fails if any beat fails
  n=0 over=0 skipped=0
  while IFS='|' read -r start end text || [ -n "${start:-}" ]; do
    [ -n "${text:-}" ] || continue
    n=$((n + 1))
    case "$text" in *'[need:'*)
      skipped=$((skipped + 1))
      echo "skipped beat $n: placeholder, not spoken" >&2
      continue ;;
    esac
    wav="$(printf '%02d' "$n").wav"
    speak "$1" "$text" "$out/$wav" || return 1
    [ -s "$out/$wav" ] || return 1
    len=$(python3 -c 'import sys,wave; w=wave.open(sys.argv[1]); print(w.getnframes()/w.getframerate())' "$out/$wav") || return 1
    room=$(awk -v a="$start" -v b="$end" 'BEGIN { print b - a }')
    fits=$(awk -v l="$len" -v r="$room" 'BEGIN { print (l <= r) ? "ok" : "over" }')
    [ "$fits" = ok ] || over=$((over + 1))
    echo "$start|$len|$wav|$fits" >> "$out/manifest.txt"
  done < "$out/beats.txt"
}

n=0 over=0 skipped=0 used=none
rm -f "$out"/*.wav
: > "$out/manifest.txt"
for tier in ${VOICE_TIER:-kokoro say none}; do
  available "$tier" || continue
  rm -f "$out"/*.wav
  : > "$out/manifest.txt"
  [ "$tier" = none ] && break
  if generate "$tier"; then used=$tier; break; fi
  echo "$tier failed, trying the next tier" >&2
  rm -f "$out"/*.wav
  : > "$out/manifest.txt"
  over=0 skipped=0
done

# ponytail: over-length beats are only reported, Voice asks Quill to trim them.
echo "VOICE tier=$used beats=$(wc -l < "$out/manifest.txt" | tr -d ' ') skipped=$skipped over=$over"
