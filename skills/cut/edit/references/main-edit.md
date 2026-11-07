# Main Edit

The global single-edit workflow for video: add, remove, replace, or modify ONE
element in a supplied video (≤15s) while preserving everything else — subjects,
motion, camera, timing, and audio.

## When to use

The user supplies a video and asks for ONE concrete change: add something /
someone, remove an object, replace an element, or modify an attribute. An
optional reference image supplies the look of the element to insert / replace.

Out of scope (for now): more than one edit in a request (future: hard-edit),
source videos longer than 15s (future: cropping).

## Inputs

- source video (required) — the clip to edit;
- the user's edit request (text, any language);
- optional reference image — a character / object / frame to insert or replace.

## Step 1 — Analyze the video and compile the edit prompt

Follow `content-analyzer/references/edit-video-analyze.md`:

    video_analyze(
      video_source = "<source video>",
      category     = "simple-edit",
      prompt       = "<the user's edit request; state if a reference image is provided>"
    )

Runs on `google/gemini-3.5-flash` (bound to the `simple-edit` category). The
model watches the video and returns `result.analysis` — the finished Seedance 2
video-to-video edit prompt: a PRESERVE segment plus an
ADD / REMOVE / REPLACE / MODIFY segment, with the video's full timing written in.

## Step 2 — Render the edited video

Pass `result.analysis` verbatim as the generation prompt. Match the output to
the source:

- duration — use the `duration` that `upload` returns for the source
  video (the backend-measured length of the real clip), rounded to a whole
  second (4–15). Do NOT take the duration from `result.analysis` — that is
  edit-prompt timing, not the clip's measured length;
- aspect_ratio — the source video's aspect ratio (use `auto` if unknown; the
  source clip is passed as the `video` reference, so the framing is preserved);
- resolution — default to `1080p` (the highest tier). Seedance supports only
  `480p` / `720p` / `1080p`, so the source's exact resolution cannot be matched —
  use the top tier. Keep `mode` at its `std` default; `fast` cannot do 1080p.

Media are passed by their uploaded-input **UUID**, never a raw URL.

- Source video → role `video` with `ref_type: "video_input"`. If you already
  have its `video_input` id (e.g. from an earlier upload), pass it directly. If
  you have an https URL or a local/sandbox file path, register it first with
  `upload(files=["<source video URL or path>"])` — for a video it
  returns `uploads[0]` with `{id, media: {id, type:"video_input", ...}, duration,
  frame_rate, ...}`. Use `uploads[0].id` here in `medias` and `uploads[0].duration`
  for the generation duration (above). Do NOT pass a raw URL into `medias` —
  always the `video_input` UUID.
- Reference image → role `image`; its type resolves automatically. Pass the
  image UUID (upload it with `upload` if you only have a file).

      generate_video(requests=[{
        model:        "seedance_2_0",
        prompt:       "<result.analysis>",
        duration:     <source duration, whole seconds 4-15>,
        aspect_ratio: "<source aspect ratio, else auto>",
        resolution:   "1080p",
        medias: [
          { "value": "<source video uuid>",    "role": "video", "ref_type": "video_input" },
          { "value": "<reference image uuid>", "role": "image" }   # ONLY if the user supplied one
        ]
      }])

## Result

The edited video — the single requested edit applied, the rest of the clip
preserved (subjects, motion, timing, audio), same duration and framing as the
source.