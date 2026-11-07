#!/usr/bin/env python3
"""audio_to_captions.py — turn a voiceover track into TIMED captions (+ .srt).

Transcribes with word-level timestamps and groups the words into short caption
phrases synced to the speech. Two backends, auto-selected:
  1. OpenAI Whisper (verbose_json + word timestamps) — used if an API key is in
     env (VOICE_TOOLS_OPENAI_KEY / OPENAI_API_KEY; base via STT_OPENAI_BASE_URL);
  2. faster-whisper — local, no key (pip install faster-whisper). Default fallback.

Usage:
  python audio_to_captions.py <audio_file> [--json out.json] [--srt out.srt]
     [--max-words 4] [--max-gap 0.4] [--model base]
Prints the captions JSON to stdout; writes --json / --srt if given.
"""
import sys, os, json, argparse, re


def group_captions(words, *, max_words=4, max_gap=0.5, max_chars=42):
    caps, cur = [], []
    def flush():
        if not cur:
            return
        text = " ".join(w["word"].strip() for w in cur).strip()
        text = re.sub(r"\s+([,.!?])", r"\1", text)
        caps.append({"text": text, "start": round(cur[0]["start"], 2),
                     "end": round(cur[-1]["end"], 2)})
        cur.clear()
    for w in words:
        if cur:
            gap = w["start"] - cur[-1]["end"]
            proj = len(" ".join(x["word"] for x in cur)) + 1 + len(w["word"])
            if gap >= max_gap or len(cur) >= max_words or proj > max_chars:
                flush()
        cur.append(w)
        if re.search(r"[.!?]$", w["word"].strip()):
            flush()
    flush()
    return caps


def _ts(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = int(t % 60); ms = int(round((t - int(t)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def to_srt(caps):
    return "\n".join(f"{i}\n{_ts(c['start'])} --> {_ts(c['end'])}\n{c['text']}\n"
                     for i, c in enumerate(caps, 1))


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
    return [{"word": str(w["word"]).strip(), "start": float(w["start"]), "end": float(w["end"])}
            for w in (d.get("words") or [])]


def _words_faster(path, model_size):
    from faster_whisper import WhisperModel
    m = WhisperModel(model_size, device="cpu", compute_type="int8")
    segs, _info = m.transcribe(path, word_timestamps=True)
    words = []
    for s in segs:
        for w in (s.words or []):
            words.append({"word": str(w.word).strip(), "start": float(w.start), "end": float(w.end)})
    return words


def get_words(path, model_size):
    try:
        w = _words_openai(path)
        if w:
            return w, "openai"
    except Exception as e:
        print(f"(openai path unavailable: {e}; using faster-whisper)", file=sys.stderr)
    return _words_faster(path, model_size), "faster-whisper"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--json"); ap.add_argument("--srt")
    ap.add_argument("--max-words", type=int, default=4)
    ap.add_argument("--max-gap", type=float, default=0.4)
    ap.add_argument("--model", default="base")
    a = ap.parse_args()

    words, provider = get_words(a.audio, a.model)
    caps = group_captions(words, max_words=a.max_words, max_gap=a.max_gap)
    print(f"provider={provider}  words={len(words)}  captions={len(caps)}", file=sys.stderr)

    out = {"captions": caps}
    print(json.dumps(out, indent=2, ensure_ascii=False))
    if a.json:
        open(a.json, "w", encoding="utf-8").write(json.dumps(out, indent=2, ensure_ascii=False))
    if a.srt:
        open(a.srt, "w", encoding="utf-8").write(to_srt(caps))


if __name__ == "__main__":
    main()
