---
name: audio-generation
description: Always read this SKILL.md before any audio task — text-to-speech voiceover, swapping the voice in an existing video, dubbing/translating a video into another language, or Seed Audio text-to-audio (speech, sound effects, music, ambience, and multi-speaker scenes, with optional voice/audio or image reference). Covers mode selection, voice picker usage, TTS model picks, async/sync polling, and ask_question rules.
---
# Audio Generation

Pick the mode, ask for a voice only when the mode needs one, submit via `audio_generate`. The tool is **batch-shaped** — always pass `requests: [...]` even for one job. It returns `job_ids` immediately for internal tracking — don't show them to the user and don't block the chat.

## User-facing style

Keep chat text relaxed and non-technical. Do not narrate routing decisions, parsed intent, tool names, language codes, source types, job IDs, payload fields, or JSON values to the user.

When you need the user to pick something, call `ask_question` directly. Do not send a prose setup first. The question itself is enough.

For clear requests with a selected voice, submit the tool call directly with no preamble. If at least one job starts, say one short plain-language line:
- Voiceover: "Started the voiceover."
- Change voice: "Started changing the voice."
- Translate / dub: "Started dubbing this into Chinese."
- Seed Audio (speech / SFX / music / ambience): "Started generating the audio."

If no jobs start, explain the failure in plain language and ask the user to retry or adjust the request. If some jobs start and some fail, mention the successful work first, then briefly say which items need retrying without exposing job IDs, payload fields, raw error arrays, or implementation wording.

If a call fails because of request shape and the fix is obvious, retry silently. After a successful retry, only say the plain-language success line.

Do not say phrases like "The intent is clear" or "I'll use...". Do not mention skill rules, routing, raw ids, field names, tool requirements, or implementation reasons. Do not expose internal values like `cmn`, `type: "video_input"`, `target_language`, or `input_video`. Those are internal details. The approval card handles technical display and result delivery.

Job IDs, language codes, source types, model names, and payload keys are for downstream tool calls only. Describe the requested audio in plain language, not the returned tool payload.

All JSON examples and tool names below are tool-call instructions only. Never copy request fields, parameter names, codes, tool names, or response payloads into chat text.

## When to use this skill

Trigger when the user's intent is one of:

- **Voiceover (Seed Audio speech with optional selected voice reference):** "make audio in Mark's voice", "voiceover this script with Ava", "read this aloud using my saved voice".
- **Change voice:** "swap the voice in this video", "replace the narrator", "use Mark's voice for this clip".
- **Translate / dub:** "translate this video to Spanish", "dub this clip into French".
- **Seed Audio (default text-to-audio):** "generate audio of ...", "read this text", "say this", sound effects ("gunshot", "door creak", "whoosh"), music ("background track", "jingle", "instrumental"), ambient soundscapes, multi-speaker scenes, voice-clone from a clip, or when the user names "Seed Audio". ByteDance text-to-audio — no preset-voice picker for generic SFX/music/ambience.

Users may write in any language — detect intent, run the task, respond in the user's language.

Do NOT trigger for:
- Speech-to-text / transcription (different domain).
- Audio **inside a video clip** when the user wants Seedance native in-clip audio — use video-generation skills instead. Use this skill when the deliverable is a **standalone audio file**.

## Mode selection

Pick `type` from the user's intent — do not ask when it's clear:

| User intent | `type` |
|---|---|
| "Make audio of X saying Y" / "read this" / "say this" with no preset/custom voice | `seed_audio` |
| "Make audio of X saying Y" / "voiceover for ..." with a preset/custom voice | `voiceover` (defaults to Seed Audio) |
| "Change the voice in this video" / "swap narrator" | `change_voice` |
| "Translate this video to <language>" / "dub into ..." | `translate` |
| Sound effect (one isolated sound) | `seed_audio` |
| Music / instrumental track / jingle | `seed_audio` |
| Voice-clone from a clip, multi-speaker scene, ambient audio, or the user names "Seed Audio" | `seed_audio` |

**Voiceover vs Seed Audio:** plain speech with a chosen preset/custom voice → `voiceover` (uses the voice picker; with no explicit model it submits Seed Audio with `voice_id` + resolved `voice_type`). Generated speech without a preset/custom voice, SFX, music, clone-from-clip, multi-speaker, ambience, or an explicit "Seed Audio" ask → `seed_audio` (no voice picker). When in doubt for ordinary "generate/read/say this text" requests, prefer `seed_audio`.

**Do not decline music or SFX** — route both through `seed_audio` with a descriptive prompt. Do not tell the user this model is "TTS only."

Only ask when the request is genuinely ambiguous ("do something with audio").

## Voiceover workflow

Required params:
- `type: "voiceover"`
- `prompt`: the exact text the voice should speak — verbatim, no narration framing ("She said:" etc.).
- `voice_id`: optional UUID returned by the voice picker. If present, the tool resolves its type and forwards `voice_id` + `voice_type`. Required when the user explicitly asks for a legacy voiceover model such as ElevenLabs, Minimax, Seed Speech, or Vibe Voice.

With no explicit `model` (or `model: "seed_audio"`), a voiceover submits through the Seed Audio engine carrying the resolved `voice_id` + `voice_type`. Only an explicit legacy model (`elevenlabs`/`minimax`/`seed_speech`/`vibe_voice`) routes to the legacy text-to-speech engine.

Defaults to async — the tool returns `job_ids` immediately for internal tracking. Announce in plain language and stop. Poll `job_status(job_ids=[...], poll=true)` only when the user asks for the result.

### Example (single job)
```json
{
  "requests": [
    {
      "type": "voiceover",
      "prompt": "Welcome to our daily roundup.",
      "voice_id": "<selected_voice_uuid>"
    }
  ]
}
```

### Example (batch — N voiceovers in one call)
```json
{
  "requests": [
    {"type": "voiceover", "prompt": "Hook line.",      "voice_id": "<selected_voice_uuid>"},
    {"type": "voiceover", "prompt": "Body section.",   "voice_id": "<selected_voice_uuid>"},
    {"type": "voiceover", "prompt": "Call to action.", "voice_id": "<selected_voice_uuid>"}
  ]
}
```

## Change voice workflow

Required params:
- `type: "change_voice"`
- `voice_id`: UUID returned by the voice picker.
- `input_video`: `{"id": "<uuid>", "type": "<source-type>"}`
  - For a prior video-generation result, pass the originating `job_id` and `type` matching the source job kind (e.g. `seedance_job`, `veo3_job`, `kling_job`).
  - For a user-uploaded video, use `type: "video_input"` with the upload's id.

Use when the user wants to keep an existing video and replace only its narration with a different voice. The job preserves background SFX/music and auto-derives the output resolution from the source video.

### Example
```json
{
  "requests": [
    {
      "type": "change_voice",
      "voice_id": "<selected_voice_uuid>",
      "input_video": {"id": "<job_or_upload_uuid>", "type": "seedance_job"}
    }
  ]
}
```

## Translate workflow

Required params:
- `type: "translate"`
- `target_language`: ISO 639-3 code (e.g. `"spa"`, `"fra"`, `"cmn"`). English names like `"Spanish"` or `"Mandarin Chinese"` are also accepted; the tool resolves them to the code. Keep the resolved code internal.
- `input_video`: same shape as change_voice — `{"id": "<uuid>", "type": "<source-type>"}`.

The dubbed voice is inherent to the target language. Do not pass `voice_id` for translate.

### Example
```json
{
  "requests": [
    {
      "type": "translate",
      "target_language": "spa",
      "input_video": {"id": "<job_or_upload_uuid>", "type": "seedance_job"}
    }
  ]
}
```

### Supported languages

ISO 639-3 codes: `afr` Afrikaans, `ara` Arabic, `hye` Armenian, `asm` Assamese, `aze` Azerbaijani, `bel` Belarusian, `ben` Bengali, `bos` Bosnian, `bul` Bulgarian, `cat` Catalan, `ceb` Cebuano, `nya` Chichewa, `hrv` Croatian, `ces` Czech, `dan` Danish, `nld` Dutch, `eng` English, `est` Estonian, `fil` Filipino, `fin` Finnish, `fra` French, `glg` Galician, `kat` Georgian, `deu` German, `ell` Greek, `guj` Gujarati, `hau` Hausa, `heb` Hebrew, `hin` Hindi, `hun` Hungarian, `isl` Icelandic, `ind` Indonesian, `gle` Irish, `ita` Italian, `jpn` Japanese, `jav` Javanese, `kan` Kannada, `kaz` Kazakh, `kir` Kyrgyz (alias: Kirghiz), `kor` Korean, `lav` Latvian, `lin` Lingala, `lit` Lithuanian, `ltz` Luxembourgish, `mkd` Macedonian, `msa` Malay, `mal` Malayalam, `cmn` Mandarin Chinese (alias: Chinese), `mar` Marathi, `nep` Nepali, `nor` Norwegian, `pus` Pashto, `fas` Persian, `pol` Polish, `por` Portuguese, `pan` Punjabi, `ron` Romanian, `rus` Russian, `srp` Serbian, `snd` Sindhi, `slk` Slovak, `slv` Slovenian, `som` Somali, `spa` Spanish, `swa` Swahili, `swe` Swedish, `tam` Tamil, `tel` Telugu, `tha` Thai, `tur` Turkish, `ukr` Ukrainian, `urd` Urdu, `vie` Vietnamese, `cym` Welsh.

## Seed Audio workflow

ByteDance text-to-audio. Use for generated speech without a preset voice, **sound effects**, **music**, voice-cloning from reference clips, multi-speaker scenes, or ambient audio from a description.

### Prompt shape for SFX and music

Seed Audio has no separate `duration` field — describe length and intent in the prompt when it matters:

- **SFX:** one isolated sound per job (not a whole scene). Be explicit: `"Single dry pistol shot, no reverb, no music, no voice, about one second"`.
- **Music:** instrumental unless the user asked for lyrics. Be explicit: `"Warm lo-fi instrumental, slow tempo, no vocals, cozy background bed, about thirty seconds"`.
- **Ambience:** loop-friendly when requested: `"Gentle rain on a window, loopable, no thunder, no music"`.

Do not open the voice picker for SFX, music, or ambience unless the user asked for a specific preset voice on speech.

Required params:
- `type: "seed_audio"`
- `prompt`: the text/script to synthesize (≤ 2048 chars). Cite audio references positionally as `@Audio1`, `@Audio2`, `@Audio3`.

Optional params (omit unless the user asks — backend defaults are sensible):
- `voice_id` / `speaker` / `speaker_id`: optional selected voice id. The tool resolves its type and forwards `voice_id` + `voice_type` to Seed Audio.
- `medias`: references — **either** up to 3 audio clips **or** exactly one image (mutually exclusive). Each item is `{"role": "audio"|"image", "data": {"id": "<uuid>", "type": "<source-type>"}}`. Audio `type`: `audio_input` (uploaded) or `text2speech_job`; a reference-element type (`reference_element`/`element`/`voice_element`/`audio_reference_element`) is resolved to its backing `audio_input`. Image `type`: `media_input` (uploaded) or a prior image-job type.
- `format` (`wav` default / `mp3` / `pcm` / `ogg_opus`), `sample_rate` (default `24000`), `speech_rate` / `loudness_rate` (−50..100), `pitch_rate` (−12..12).

Do not pass `model` for seed_audio.

### Example (prompt only — speech + ambience)
```json
{
  "requests": [
    {"type": "seed_audio", "prompt": "A calm narrator welcomes the listener over soft rain."}
  ]
}
```

### Example (sound effect)
```json
{
  "requests": [
    {"type": "seed_audio", "prompt": "Single dry pistol shot, no reverb, no music, no voice, about one second"}
  ]
}
```

### Example (instrumental music)
```json
{
  "requests": [
    {"type": "seed_audio", "prompt": "Warm lo-fi instrumental, slow tempo, no vocals, cozy background bed, about thirty seconds"}
  ]
}
```

### Example (voice-clone from reference clips)
```json
{
  "requests": [
    {
      "type": "seed_audio",
      "prompt": "@Audio1 reads the intro, then @Audio2 answers.",
      "medias": [
        {"role": "audio", "data": {"id": "<clip1_uuid>", "type": "audio_input"}},
        {"role": "audio", "data": {"id": "<clip2_uuid>", "type": "audio_input"}}
      ]
    }
  ]
}
```

## Voice selection

For voiceover and change_voice, the tool can use `voice_id`. If the user asks for a specific preset/custom voice and the request does not already include one, ask with the `voice` entity picker. The frontend renders presets and custom voices and returns the selected UUID. Pass that UUID as `voice_id`.

Do not pass voice names. Do not pass voice type. Do not fetch or resolve the voice catalog in chat.

For generic speech/audio with no requested voice, do not open the voice picker; use prompt-only `seed_audio`.

## Model picks

Voiceover and generic speech default to Seed Audio. Do not ask for a model when the user did not mention one. If the user explicitly names a supported legacy voiceover model (`elevenlabs`, `minimax`, `seed_speech`, `vibe_voice`), pass that `model`; the runtime submits to that legacy voiceover engine instead of Seed Audio.

## Async vs sync

- **Async (default)**: returns `{"job_ids": ["..."]}` immediately for internal tracking; chat stays responsive.
- **Sync** (`async=false`): blocks up to `timeout_seconds` (default 900) and adds `"results": [...]` with one terminal entry per id. Use only when the caller explicitly wants the URL inline.

## Polling — Fire-and-Forget

The tool returns `{"job_ids": ["..."], "errors"?: [...]}` immediately. **Default: fire-and-forget.** Submit, hold job IDs internally, and announce only after at least one job starts.
Do not paste job IDs, language codes, source types, polling status, or tool payload details into user-facing text. Include a finished URL only when the user explicitly asked for the file/link or sync/polling was requested for that purpose.

If the response has both `job_ids` and `errors`, use a short partial-success reply: "Started the voiceover and one item needs a retry." If `job_ids` is empty, do not say it started; explain the failure in plain language.

**Poll only when:**
- The user explicitly asks for the audio file / URL.
- A downstream skill needs the audio result inside the same turn.

Poll call: `job_status(job_ids=["JOB_ID"], poll=true)`. The finished job's `result.url` is the audio file link.

**Never poll** to "confirm it succeeded" — delivery is handled automatically.

## Error Handling

| Error | Fix |
|---|---|
| `voice_id is required` | Ask the user to choose a voice from the picker. |
| `prompt is required` (voiceover / seed_audio) | Ask the user for the text to speak. |
| seed_audio rejected as unavailable / "type not allowed" | Seed Audio isn't enabled in this environment yet — offer `voiceover` with a legacy model instead, or tell the user it's coming soon. |
| Job `failed` | Explain the generation error in plain language without internal fields; offer to retry with the same prompt. |
| Sync `timeout` | Switch to async (`async=true`) and poll later. |

## ask_question rules

### DO ask
- **Voice** — when `voice_id` is missing for change_voice, or the user asked for a specific preset/custom voice on a voiceover, use the `voice` entity picker (`kind: "entity"`, `entity: {type: "voice"}`). The frontend renders preset and custom voice cards. The picker returns the selected UUID; pass it as `voice_id`.
- **Language** (translate only) — when the user asks to translate/dub but hasn't named a target language, use the `language` entity picker (`kind: "entity"`, `entity: {type: "language"}`). It covers all 74 supported languages and returns an ISO 639-3 code; pass it directly as `target_language`. Don't guess or list a subset in text options.
- **Type** — only when the request is genuinely ambiguous between modes ("do something with audio").

### NEVER ask
- For a model when the user did not mention one — use Seed Audio.
- For a voice on generic speech/audio requests — use `seed_audio`; do not open the voice picker.
- For sync vs async — default to async.
- For confirmation before submitting — the tool renders its own approval card showing mode, prompt, model, and voice. Do not duplicate the preview in chat text.
