#!/usr/bin/env python3
"""caption_burn.py — word-timed transcription + styled caption burn-in for
video-repurpose. Two subcommands:

  words <audio_or_video> [--json out.json] [--model base]
      Real word-level timestamps. `speech2text` does NOT return
      these (it only returns plain transcript text — checked against
      the speech2text tool, do not assume otherwise), so
      this gets its own backend, same two-tier approach already proven in
      this repo by video-explainer-workflow/scripts/audio_to_captions.py:
        1. OpenAI Whisper (verbose_json, word timestamps) if an API key is in
           env (VOICE_TOOLS_OPENAI_KEY / OPENAI_API_KEY; base via
           STT_OPENAI_BASE_URL);
        2. faster-whisper — local, no key (pip install faster-whisper).

  burn <video> --words words.json --output out.mp4 --width W --height H
       [--margin-v-pct P] [--max-width-pct P] [--position bottom|top|middle]
       [--max-words 4] [--max-chars-per-line 24] [--size-pct 5]
       [--uppercase] [--font "DejaVu Sans"]
      Groups words into short cues (breaks on word count, a real speech gap,
      or a line-length budget — never mid glue-word), wraps each cue to
      --max-chars-per-line, and burns a real ASS style (bold, outlined,
      platform-safe margins) via ffmpeg — not ffmpeg's bare unstyled default.

Placement is deliberately NOT hardcoded: --margin-v-pct/--max-width-pct must
come from the caller (SKILL.md points at the platform-specific numbers in
references/video-platform-formats.md — a 9:16 target needs a much bigger
bottom margin to clear TikTok/Reels/Stories UI than a 1:1 or 16:9 target
does, which has no UI overlay at all).

Requires: ffmpeg (with libass) on PATH. `words` additionally needs either an
OpenAI-compatible key in env, or `pip install faster-whisper` (local, CPU).
"""
import argparse
import json
import os
import re
import subprocess
import sys


# ---------------------------------------------------------------------------
# words: real word-level timestamps
# ---------------------------------------------------------------------------


def _words_openai(path):
    key = os.getenv("VOICE_TOOLS_OPENAI_KEY") or os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    from openai import OpenAI

    base = os.getenv("STT_OPENAI_BASE_URL", "https://api.openai.com/v1")
    client = OpenAI(api_key=key, base_url=base, timeout=120, max_retries=0)
    with open(path, "rb") as f:
        tr = client.audio.transcriptions.create(
            model="whisper-1", file=f,
            response_format="verbose_json", timestamp_granularities=["word"])
    d = tr.model_dump() if hasattr(tr, "model_dump") else json.loads(tr.json())
    return [{"text": str(w["word"]).strip(), "start": float(w["start"]), "end": float(w["end"])}
            for w in (d.get("words") or [])]


def _words_faster(path, model_size):
    from faster_whisper import WhisperModel

    m = WhisperModel(model_size, device="cpu", compute_type="int8")
    segs, _info = m.transcribe(path, word_timestamps=True)
    words = []
    for s in segs:
        for w in (s.words or []):
            words.append({"text": str(w.word).strip(), "start": float(w.start), "end": float(w.end)})
    return words


def get_words(path, model_size="base"):
    try:
        w = _words_openai(path)
        if w:
            return w, "openai"
    except Exception as e:
        print(f"(openai path unavailable: {e}; using faster-whisper)", file=sys.stderr)
    return _words_faster(path, model_size), "faster-whisper"


def cmd_words(args):
    words, provider = get_words(args.input, args.model)
    print(f"provider={provider}  words={len(words)}", file=sys.stderr)
    out = {"words": words}
    payload = json.dumps(out, indent=2, ensure_ascii=False)
    print(payload)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            f.write(payload)


# ---------------------------------------------------------------------------
# burn: group words -> cues -> wrapped lines -> ASS -> ffmpeg
# ---------------------------------------------------------------------------

# Words that must glue to the NEXT word — a cue/line must never end (or a
# wrap never break) right after one of these (articles / prepositions /
# conjunctions). Small and deliberately not exhaustive.
GLUE_FORWARD = {
    "a", "an", "the", "in", "on", "at", "to", "of", "for", "with", "by", "from",
    "as", "and", "or", "but", "nor", "so", "if", "than", "per", "via", "into",
    "onto", "over", "under", "about", "after", "before", "between", "during",
    "against", "across", "around", "near", "up",
}


def is_glue(word):
    return re.sub(r"[^\w]", "", word, flags=re.UNICODE).lower() in GLUE_FORWARD


def group_cues(words, max_words=4, max_gap=0.5, max_chars=42):
    """Word-count + natural-pause + rough-length grouping (same shape as
    video-explainer-workflow's group_captions), with a glue-word guard: never
    end a cue on a glue word — pull the boundary back one word instead."""
    cues, cur = [], []

    def flush():
        if not cur:
            return
        text = " ".join(w["text"] for w in cur).strip()
        text = re.sub(r"\s+([,.!?])", r"\1", text)
        cues.append({"text": text, "start": cur[0]["start"], "end": cur[-1]["end"], "words": list(cur)})
        cur.clear()

    for w in words:
        if not w["text"]:
            continue
        if cur:
            gap = w["start"] - cur[-1]["end"]
            proj = len(" ".join(x["text"] for x in cur)) + 1 + len(w["text"])
            if gap >= max_gap or len(cur) >= max_words or proj > max_chars:
                # Don't end the cue on a glue word (or a run of them, e.g.
                # "... put them on the") — pop the whole trailing run off
                # first and carry it into the next cue instead of flushing
                # it away. If EVERY word so far is glue, cur empties out and
                # nothing is flushed yet — the run keeps growing until a
                # real word anchors it, rather than emitting a lone "the".
                carried = []
                while cur and is_glue(cur[-1]["text"]):
                    carried.insert(0, cur.pop())
                if cur:
                    flush()
                cur.extend(carried)
        cur.append(w)
        if re.search(r"[.!?]$", w["text"].strip()):
            flush()
    flush()
    return cues


def wrap_lines(text, max_chars):
    """Wrap at word boundaries, <= max_chars per line, never leaving a glue
    word dangling at a line end (carries it to the next line instead)."""
    if max_chars <= 0:
        return [text]
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > max_chars:
            parts = cur.split(" ")
            carried = []
            while parts and is_glue(parts[-1]):
                carried.insert(0, parts.pop())
            if parts:
                lines.append(" ".join(parts))
            cur = " ".join([*carried, w])
        else:
            cur = f"{cur} {w}" if cur else w
    if cur:
        lines.append(cur)
    return lines


def ass_color(hex_color, opacity=1.0):
    """#RRGGBB (+ opacity 0..1) -> ASS &HAABBGGRR& (BGR order, alpha inverted:
    00 = opaque, FF = transparent)."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    a = round((1 - max(0.0, min(1.0, opacity))) * 255)
    return f"&H{a:02X}{b:02X}{g:02X}{r:02X}&"


def _ass_time(t):
    t = max(0.0, t)
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h:d}:{m:02d}:{s:05.2f}"


def build_ass(cues, width, height, *, size_pct=5.0, margin_v_pct=8.0, max_width_pct=90.0,
              position="bottom", max_chars_per_line=24, uppercase=False,
              font="DejaVu Sans", text_color="#FFFFFF", outline_color="#000000"):
    size = max(12, int(height * (size_pct / 100.0)))
    # Outline scales with font size (not a fixed px) so it stays legible at
    # any target resolution — thin at 5% size looked bad in practice, ~8% of
    # the font size reads as a solid, TikTok-caption-style stroke.
    outline_w = max(2, round(size * 0.08))
    alignment = {"top": 8, "middle": 5, "bottom": 2}.get(position, 2)
    margin_v = int(height * (margin_v_pct / 100.0))
    side_pct = max(0.0, (100.0 - max_width_pct) / 2.0)
    margin_side = int(width * (side_pct / 100.0))

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
ScaledBorderAndShadow: yes
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{font},{size},{ass_color(text_color)},{ass_color(text_color)},{ass_color(outline_color)},&H00000000&,-1,0,0,0,100,100,0,0,1,{outline_w},0,{alignment},{margin_side},{margin_side},{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    max_width_chars = max_chars_per_line
    lines_out = []
    for cue in cues:
        text = cue["text"].upper() if uppercase else cue["text"]
        wrapped = "\\N".join(wrap_lines(text, max_width_chars))
        lines_out.append(
            f"Dialogue: 0,{_ass_time(cue['start'])},{_ass_time(cue['end'])},Cap,,0,0,0,,{wrapped}"
        )
    return header + "\n".join(lines_out) + "\n"


def cmd_burn(args):
    with open(args.words, encoding="utf-8") as f:
        payload = json.load(f)
    words = payload["words"] if isinstance(payload, dict) else payload
    cues = group_cues(words, max_words=args.max_words, max_gap=args.max_gap,
                       max_chars=args.max_chars_per_line * 2)
    if not cues:
        sys.exit("no words to caption — check the transcript input")

    ass_text = build_ass(
        cues, args.width, args.height,
        size_pct=args.size_pct, margin_v_pct=args.margin_v_pct,
        max_width_pct=args.max_width_pct, position=args.position,
        max_chars_per_line=args.max_chars_per_line, uppercase=args.uppercase,
        font=args.font, text_color=args.text_color, outline_color=args.outline_color,
    )
    ass_path = args.output + ".ass"
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write(ass_text)

    escaped = ass_path.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    cmd = ["ffmpeg", "-y", "-i", args.input, "-vf", f"ass='{escaped}'",
           "-c:a", "copy", args.output]
    print("Running:", " ".join(cmd), file=sys.stderr)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr[-4000:], file=sys.stderr)
        sys.exit(1)
    print(f"Wrote {args.output} ({len(cues)} cues, ass={ass_path})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_words = sub.add_parser("words", help="Extract real word-level timestamps.")
    p_words.add_argument("input", help="Audio or video file.")
    p_words.add_argument("--json", help="Write the words JSON here too.")
    p_words.add_argument("--model", default="base", help="faster-whisper model size (fallback path only).")
    p_words.set_defaults(func=cmd_words)

    p_burn = sub.add_parser("burn", help="Group words into cues and burn a styled caption track.")
    p_burn.add_argument("input", help="Video file to caption.")
    p_burn.add_argument("--words", required=True, help="words JSON from the `words` subcommand.")
    p_burn.add_argument("--output", required=True)
    p_burn.add_argument("--width", type=int, required=True)
    p_burn.add_argument("--height", type=int, required=True)
    p_burn.add_argument("--margin-v-pct", type=float, default=8.0,
                         help="Bottom (or top) margin as %% of height. Look this up per target in "
                              "references/video-platform-formats.md — do not leave at the default "
                              "for a 9:16 target.")
    p_burn.add_argument("--max-width-pct", type=float, default=90.0,
                         help="Caption block max width as %% of frame width.")
    p_burn.add_argument("--position", choices=["top", "middle", "bottom"], default="bottom")
    p_burn.add_argument("--max-words", type=int, default=4)
    p_burn.add_argument("--max-gap", type=float, default=0.5)
    p_burn.add_argument("--max-chars-per-line", type=int, default=24)
    p_burn.add_argument("--size-pct", type=float, default=5.0)
    p_burn.add_argument("--uppercase", action="store_true", default=False)
    p_burn.add_argument("--font", default="DejaVu Sans")
    p_burn.add_argument("--text-color", default="#FFFFFF")
    p_burn.add_argument("--outline-color", default="#000000")
    p_burn.set_defaults(func=cmd_burn)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
