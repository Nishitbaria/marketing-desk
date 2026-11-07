#!/bin/bash
# Run from anywhere. Exercises each tier, the placeholder skip and the over check.
set -eu
root="$(cd "$(dirname "$0")/../.." && pwd)"
out="$root/renders/voicetest-voice"
trap 'rm -rf "$out"' EXIT
mkdir -p "$out"
cat > "$out/beats.txt" <<'B'
0|3|You need one minute.
3|4|This line is far too long to fit inside a single second of video at any calm pace.
4|8|Try it at [need: CTA link].
B
run() { VOICE_TIER="$1" "$root/skills/voice/make-voice.sh" voicetest 2>/dev/null | tail -1; }

r=$(run say); echo "$r"
[ "$r" = "VOICE tier=say beats=2 skipped=1 over=1" ]
grep -q '|ok$' "$out/manifest.txt"; grep -q '|over$' "$out/manifest.txt"

r=$(run none); echo "$r"
[ "$r" = "VOICE tier=none beats=0 skipped=0 over=0" ]
[ ! -f "$out/01.wav" ]

# A broken Python must fall through to say, not stop the chain.
r=$(HYPERFRAMES_PYTHON=/usr/bin/false VOICE_TIER="kokoro say none" "$root/skills/voice/make-voice.sh" voicetest 2>/dev/null | tail -1); echo "$r"
[ "${r%% beats*}" = "VOICE tier=say" ]

# No tier available still ends cleanly with no audio.
r=$(HYPERFRAMES_PYTHON=/usr/bin/false VOICE_TIER=kokoro "$root/skills/voice/make-voice.sh" voicetest 2>/dev/null | tail -1); echo "$r"
[ "$r" = "VOICE tier=none beats=0 skipped=0 over=0" ]

if "$root/skills/voice/make-voice.sh" 2>/dev/null; then echo "no slug must fail"; exit 1; fi
echo PASS
