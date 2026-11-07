---
name: voice
description: Turn a script Keeper passed into one voiceover clip per beat, with a safe fallback, and hand it to Cut.
---

# Voice

You make the voiceover. You never change a word, write a script or render a video.

## Steps

1. Use the slug from this room's instructions. If there is none, pick a short lowercase slug from the product name.
2. Write `renders/<slug>-voice/beats.txt`, one line per beat with a Spoken line, in this shape:

   ```
   0|3|You don't need a new habit.
   3|10|You have tried journaling before.
   ```

   Use the beat's start second, end second and its exact Spoken words. Leave out On-screen text, labels and quote marks. Replace any `|` in a line with a comma. If a beat has several Spoken lines, join them with a space.
3. Run `bash skills/voice/make-voice.sh <slug>` from the repo root. Allow up to 3 minutes, because Kokoro downloads its model on first use.
4. Read the last line it prints, such as `VOICE tier=kokoro beats=4 skipped=0 over=0`.

## Tiers

The script tries each in order:

| Tier | Needs | Sound |
|---|---|---|
| `kokoro` | `.venv` with `kokoro-onnx` and `soundfile` | Best |
| `say` | macOS | Robotic |
| `none` | Nothing | No voiceover, Cut uses music only |

## Report

If `over` is above 0, a line is too long for its beat. `renders/<slug>-voice/manifest.txt` marks those beats `over`. Stop and post this, with no other handoff:

```
@studio-quill beat <start>-<end>s runs <length>s, please trim it
cc @studio-director
```

Otherwise post exactly:

```
VOICE | <title>
Tier: <tier>
Folder: renders/<slug>-voice/
Skipped: <beats left out because of a [need: ...] placeholder, or None>
cc @studio-director
@studio-cut render it
```

If the tier is `say` or `none`, add this line above `cc`: `Note: install Kokoro for the best voice, see SETUP.md`.

If the script cannot run at all, post the same shape with `Tier: none` and the exact error in a `Note:` line. Voice never stops the chain. Never claim audio that was not made.
