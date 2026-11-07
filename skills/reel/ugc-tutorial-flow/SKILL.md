---
name: ugc-tutorial-flow
description: |
  A UGC-style tutorial video — a creator demonstrates step-by-step use of a specific product, with on-screen "Step N" captions.
  Triggers only with ALL: (a) tutorial/how-to/step-by-step intent, (b) UGC framing (UGC/creator/tiktok/"video of me"), (c) a specific product (image/URL/"this/our/my X").
---
# Tutorial Product Workflow

One pipeline for all UGC tutorial + product videos, all durations. Each board slot is ONE physical step of using the product, with a "Step N — Heading" caption rendered on the slot.

## Mandatory Reference Resolution

This workflow is self-contained. Use ONLY the references in this table. Do NOT substitute legacy references — they belong to deprecated paths and will conflict with this workflow's rules.

**Loading rule:** load each reference with `skill_view(name, file_path)` using the skill name and file path columns below. Do NOT pass `..` relative paths — `file_path` is always relative to the named skill's directory.

| Step | Skill | File path | Do NOT substitute |
| --- | --- | --- | --- |
| Generate the storyboard board | `image-generation` | `references/ugc-tutorial-boards.md` | NOT `ugc-boards.md` (talking-head flow), NOT `ugc-unboxing-boards.md` (unboxing flow) |
| Write the Seedance prompt for each clip | `video-generation` | `references/ugc-tutorial-clip-prompt.md` | NOT `ugc-clip-prompt.md` (talking-head flow), NOT `ugc-unboxing-clip-prompt.md` (unboxing flow), NOT `ugc-try-on-clip-prompt.md` (try-on flow) |
| Generate the character | `image-generation` | `references/soul-v2-ugc-character.md` | (only this — no override) |
| Product URL extraction (URL case) | `product-analyzer` | `references/url-extract.md` | — |
| Product visual analysis (photo case) | `product-analyzer` | `references/visual-analysis.md` | — |

If you find yourself reading `ugc-boards.md`, `ugc-clip-prompt.md`, `ugc-unboxing-boards.md`, or `ugc-unboxing-clip-prompt.md` (sibling-flow references), or any other clip-prompt reference, while inside this workflow — STOP, return to this SKILL.md, and use the references in the table above.

## Architecture

- Each **board** is a 21:9 strip with 4 vertical 9:16 slots — four sequential tutorial steps inside ONE Seedance clip. Each slot carries a `Step N — Heading` text caption rendered with consistent typography across all four slots of the same board.
- Each board → ONE Seedance call. Inputs: board image + character + product, all as `medias` with role `image`.
- Within the clip, the prompt describes hard cuts between the 4 slots.
- For >15s: N boards generated sequentially (each conditioned on the previous for consistency), N Seedance clips run in parallel, ffmpeg concat with hard cuts.
- **Total tutorial steps = 4 × N_boards.** Step numbering is global across the whole video — Board 1 has Steps 1-4, Board 2 has Steps 5-8, Board 3 has Steps 9-12, etc.
- **CTA tail (mandatory, video-level only):** the final ~0.5-1 second of the FINAL cut of the FINAL board ends with a brief talking-head selfie + downward hand gesture and a short English CTA phrase ("Link in bio", "Follow me", "Subscribe!"). The CTA is NOT a fifth step. The CTA is NOT a separate slot. The CTA is NOT rendered as a caption anywhere on the board image. It is a video-level audio/visual tail handled inside the Seedance prompt for the last cut of the last board.

## Duration → N boards → per-clip durations

| Total D | N | Clip durations | Total tutorial steps |
| --- | --- | --- | --- |
| 4-15 | 1 | D | 4 |
| 16-19 | 2 | balance to ≥4s each (D=18 → 14+4) | 8 |
| 20-30 | 2 | 15, D-15 | 8 |
| 31-45 | 3 | 15, 15, D-30 | 12 |
| 46-60 | 4 | 15, 15, 15, D-45 | 16 |
| >60 | ceil(D/15) | 15 each, last = remainder ≥4s | 4 × ceil(D/15) |

## Canonical Tutorial Arc — 4 slots per board

Every board carries a 4-slot tutorial arc. Each slot = one physical step of using the product. Step numbering is global:

| Slot in Board J | Global step number   |
| --------------- | -------------------- |
| Slot 1          | Step (4 × (J−1) + 1) |
| Slot 2          | Step (4 × (J−1) + 2) |
| Slot 3          | Step (4 × (J−1) + 3) |
| Slot 4          | Step (4 × (J−1) + 4) |

The arc is tutorial-progressive: opening setup → core action → application → wrap-up / result. Specific step content is derived from the product + user request in the **Product Usage Analysis** stage (Pipeline / 1).

For multi-board (N > 1) videos: Boards 2..N continue the tutorial from where Board K-1 left off — chronological progression of usage steps. The previous-board reference is used to preserve identity, location, lighting, wardrobe, and product state.

## Pipeline

### 1. Parse request + Product Usage Analysis

Extract product (URL or photo) + duration + optional product instructions / manual / usage notes from the user.

### TikTok selected-handoff truth mode (conditional)

This mode is active only when the incoming structured brief contains `truth_contract`; otherwise this section changes nothing. In truth mode:

- `truth_contract` overrides every generic example, phrase bank, product-analysis inference, specificity rewrite, and rule asking for a concrete number, time, comparison, result, purchase count, or measurement.
- `allowed_product_claims` is the complete allowlist. Use an allowed product claim only as its exact verbatim string. Never paraphrase, strengthen, combine, or derive another claim. An empty allowlist means claim-free consumer copy.
- Forward `truth_contract` unchanged in every board prompt input and clip-writer metadata object. Product descriptions and usage steps stay visual/mechanical unless they contain an exact allowlisted claim.
- When unsupported numbers are forbidden, tutorial step numbers and durations remain production metadata, but must never become unsupported spoken or displayed product claims.
- Forward `brief.duration_policy` on every final video request when present.

### TikTok handoff product continuity

When the incoming brief contains `truth_contract`, non-empty
`brief.product_references` are already supplied product images/media and
`brief.requested_product_url` is already supplied URL input. Resolve/upload
those references as needed, but never ask the user to provide the same product
again and never require it to be attached in the current turn. Ask only when
the handoff explicitly lists the product prerequisite as missing.

- URL → `skill_view("product-analyzer", "references/url-extract.md")`
- Photo only → `skill_view("product-analyzer", "references/visual-analysis.md")`
- Compute N + per-clip durations + total step count = `4 × N`

**Product Usage Analysis (mandatory):** before generating any board, build a sequence of `total_step_count` realistic usage steps for the actual product. Inputs: product category, container/applicator type, user-supplied instructions/manual (if any), user request text.

Rules:

- Steps must be physically realistic for the actual product. Never invent steps the product cannot perform.
- Steps are chronological — the order matches how a real user would actually use the product.
- If the natural number of usage steps is fewer than `total_step_count`, expand by adding setup/preparation steps at the start and finishing/cleanup steps at the end.
- If the natural number of steps is more than `total_step_count`, condense by merging adjacent micro-actions into single steps.
- If the user provides explicit Director-tier step list, map their steps 1:1 to slots in their order; do not re-derive.

Output of this stage: an array `step_captions[1..total_step_count]` of strings, each formatted as `"Step N — Heading"`:

- `Step N` — global step number (Title Case, en-dash separator)
- `Heading` — short Title Case English phrase describing the action (1-4 words; e.g., `"Step 1 — Apply Primer"`, `"Step 5 — Pat It In"`, `"Step 8 — Final Mist"`)
- English only. No other languages.

This array is split into per-board groups of 4 and passed to each board generation as the `step_captions` input.

**Product staging contract (fixed once, reused VERBATIM in every downstream call):** from the analyzer output write ONE canonical product description: shape, material, color, hand-relative size ("palm-sized, fits entirely in one hand, ~15 cm tall" — never object comparisons, they drift), mechanism anatomy (which part is where, what moves, where the output exits), absent features stated visually ("cordless, smooth body, no buttons"), the label (mode-dependent, below), plus one imperfection. Label: when a product PHOTO is uploaded (the standard path), the label keeps its real text — the reference image + the enhancers' Product Angle Lock carry it; write nothing that calls it illegible. Description-only mode (no photo): describe the label as "small label, turned slightly away, too small to read". In BOTH modes, never stage other props with legible text or numbers. Photo-mode caveat: if the photo shows a big readable logo — warn the user once (wordmarks render as gibberish or a real competitor brand — production data) and keep it angled away in prompts only if they agree.

### 1.4 Accent & quirk (OPT-IN)

If the brief names an identifiable origin for the creator, or asks for "weird"/"viral" character energy, ask ONE combined optional question (accent consent + one quirk offer) — bundled into the same single `ask_question` call as the other creative gaps, never a separate extra call. Never add an accent the user didn't approve; default = neutral English, no quirk. If opted in: write the persona/quirk sentence ONCE (identity + attitude, e.g. "a young Korean it-girl — English is her second language and you hear it in every sentence") and restate it VERBATIM in this flow's real channels (there are no enhancers here): the Step 2 Soul 2.0 character prompt, every board prompt (Step 5), and every board's `monologue_segment` delivery framing (Step 6). Accent reality check (production data): text-only accent enforcement lands ~1 render in 3 — if the user can drop a 5–10s voice sample, attach it to the Seedance generation as an audio reference (`@voice: accent and vocal delivery reference only — do not copy words, only the accent, melody, and timbre. Reference.`); offer this once at intake, don't block on it.

### 1.5. Persona source — detect character_provided

Set `character_provided = true` if the user attached one or more person photos alongside the product brief (any framing — close-up face, full-body, any pose). Otherwise `character_provided = false`.

If `character_provided == true`:

- Upload the user-provided person photo via `upload(...)` → capture `(character_media_id, character_url)` from `uploads[0].id` + `uploads[0].url`.
- **SKIP Step 2 entirely** (no Soul 2.0 generation, no character prompt building). The user's photo IS the character.
- Proceed directly to Step 3.

If `character_provided == false`:

- Proceed to Step 2 as written below — generate the character via Soul 2.0.

This is a hard gate, not a question to the user. Do NOT call `ask_question` to confirm — if a person photo is attached, treat it as the character. Quality / framing / pose of the user's photo is the user's own responsibility.

### 2. Character (Soul 2.0) — only when character_provided == false

Follow `skill_view("image-generation", "references/soul-v2-ugc-character.md")`. Generate once via `generate_image(params={"model":"text2image_soul_v2", ...})`. Poll job_status to terminal state. Capture `(character_media_id, character_url)` where `character_media_id` is the `job_id` returned by `generate_image` and `character_url` is `result.url` on terminal status. NO download, NO `upload` round-trip — Soul outputs chain forward via the `job_id` reference (verified across `motion-design-flow:625-626` and `soul-id:106`). Outfit fixed across boards unless story demands a change (e.g., outdoor + rain → raincoat).

### 3. Upload product

`upload(files=[product.png])` → capture `product_media_id` from `uploads[0].id`. Skip if no product. Product entries in downstream `medias[]` are referenced by their uploaded id as `value`.

### 4. Draft full monologue

Word density: ≤10s ~ 12-20 words, 11-12s ~ 20-28, 13-15s ~ 28-35. Sum across clips for total.

Split into N board-segments, then each into 4 slot-segments (one per tutorial step). The slot-segment for each step explains WHAT the character is doing in that step — concise, instructional, conversational ("Now I press the pump twice.", "I rub it in like this.").

Greetings + product introduction allowed ONLY in Board 1 / Slot 1. Other slots continue mid-thought.

**Craft pass on the monologue (before splitting into segments):** tutorial steps are the spine — do NOT impose a story shape. Apply the anti-slop pass on every line (no `Okay wait / Okay so / OMG / Hey guys` openers; banned anywhere: "literally", "obsessed", "game-changer", "holy grail", "changed my life", "hits different", corporate words). Outside truth mode, every claim carries one concrete (a number, a time, a named comparison). In truth mode, use only exact allowlisted claims and never add a "concrete" to satisfy this craft rule.

**CTA tail (last cut of last board only):** reserve ~0.5-1s of audio at the very end of the final cut for a brief English CTA phrase. Default options: `"Link in bio."`, `"Follow me."`, `"Subscribe!"`. If the monologue runs long and there's no time left, cut the monologue earlier and use the shortest CTA (`"Subscribe!"`). The CTA is appended after the last step's instructional sentence — never replaces a step's content.

### 5. Generate boards sequentially

**Board 1:**

- `medias`: `[product, character]` (omit product if absent) — flat `{value, role}` shape
- `prompt`: built per `skill_view("image-generation", "references/ugc-tutorial-boards.md")`, injecting board index, the 4-string `step_captions` array for this board, product description, and the per-slot tutorial-step intent.
- `aspect_ratio`: `"21:9"`, model `gpt_image_2`

When truth mode is active, include `truth_contract` unchanged in every board prompt input.

All medias entries use the v2 flat shape `{value, role: "image"}` — the backend sniffs the source type from `value`, so no `type` field is needed:

- Product is always uploaded (a `media_input` id).
- Character from Step 1.5 / Step 2 (uploaded id for user-attached, Soul `job_id` for Soul-generated).
- Previous board chain-ref (K>1) is the board `job_id`.

```json
"medias": [
  {"value": "<PRODUCT_MEDIA_ID>", "role": "image"},
  {"value": "<CHARACTER_MEDIA_ID>", "role": "image"}
]
```

Poll job_status to terminal state. Capture `(board_1_media_id, board_1_url)` where `board_1_media_id` is the `job_id` returned by `generate_image` and `board_1_url` is `result.url` on terminal status. NO download, NO `upload` round-trip — `gpt_image_2` outputs chain forward via `job_id`.

**Boards 2..N:** Same call. `medias`: `[product, character, previous_board]`:

```json
"medias": [
  {"value": "<PRODUCT_MEDIA_ID>", "role": "image"},
  {"value": "<CHARACTER_MEDIA_ID>", "role": "image"},
  {"value": "<BOARD_K-1_JOB_ID>", "role": "image"}
]
```

User-message: "Board K of N. Preserve identity / location / lighting / product / wardrobe from the reference board. Tutorial continues from Step (4*(K-1)+1) to Step (4*K). Action picks up chronologically from the last slot of the previous board." Pass the per-board `step_captions` slice for Board K.

After each board K poll, capture `(board_K_media_id, board_K_url)` exactly as for Board 1.

### 5.5 Anti-slop pass (Seedream 5.0 Pro i2i) — MANDATORY, run for EVERY board

`gpt_image_2` holds identity but slops the render (waxy / HDR / over-smoothed skin). **You MUST run EVERY finished board through** a `seedream_v5_pro` instruction-edit (i2i) that de-slops it while keeping faces, composition and product pixel-faithful — the de-slopped output **REPLACES the board downstream** (its `job_id` / `url` feed the clip enhancer `image_refs` and the Seedance `medias`). NOTE: the baked per-slot `Step N` captions must survive unchanged — the prompt below preserves all on-frame layout, so the step text is kept.

**MANDATORY — do it in TWO tool calls, in this exact order (never skip, never shortcut):**

**Upload the board to a `media_input` first.** Seedream's `image_references` does NOT accept the board's `gpt_image_2` `job_id` (chain-refs resolve for Seedance `role:"image"` but 404 "Media input not found" on Seedream i2i). Upload the board's `url`:
```json
upload({"files": ["<board_K_url>"]})
```
Capture `uploads[0].id` as `board_K_upload_id`. (`upload` accepts a public URL via safe-fetch — no download needed.)

**Then run Seedream i2i with that upload id** (`board_K_upload_id`, NOT the job_id):
```json
generate_image({
  "requests": [{
    "model": "seedream_v5_pro",
    "prompt": "<ANTI-SLOP PROMPT below, verbatim>",
    "aspect_ratio": "21:9",
    "resolution": "2k",
    "medias": [{"value": "<board_K_upload_id>", "role": "image_references"}]
  }]
})
```

**ANTI-SLOP PROMPT** (fixed, every board — note: keeps the baked Step-N captions):

> KEEP EXACTLY the framing, composition, slot layout, camera distances, poses, subjects, product AND any on-frame step captions of this horizontal storyboard sheet and every one of its side-by-side vertical slots — no reframe, no zoom, no crop, no re-layout, no change to the scene, to any person's face / hair / body, to the product design, or to existing on-frame text. CHANGE ONLY micro-realism, applied identically in every slot: true-to-life pore-level skin with natural texture and fine vellus hair, real material detail, even natural daytime light with gentle highlight roll-off and faint true sensor noise, a flat authentic iPhone photo, deep focus. PRESERVE each face's exact shape / width / proportions 1:1 — do NOT squeeze / narrow / slim / stretch any face. AVOID AI-slop: waxy plastic skin, airbrushed poreless skin, beauty-filter smoothing, over-saturation, HDR glow / bloom / halos, oversharpening, teal-orange grade, shallow depth of field, bokeh, cinematic / DSLR look. Keep the product blank / unbranded, no NEW added text, no watermark.

- Media role **`image_references`** (NOT `image`); `aspect_ratio` = the board's `21:9`.
- Capture the de-slopped `(board_K_media_id, board_K_url)` and OVERWRITE the raw-board refs so the clip step + Seedance chain the cleaned board.
- **Fallback:** moderation block → retry once on `seedream_v5_lite`; total failure → use the raw `gpt_image_2` board (never block).

### 6. Write Seedance prompt per board

**MANDATORY: the system prompt for the LLM call is `skill_view("video-generation", "references/ugc-tutorial-clip-prompt.md")`. Do NOT substitute `ugc-clip-prompt.md` (talking-head flow), `ugc-unboxing-clip-prompt.md` (unboxing flow), `ugc-try-on-clip-prompt.md` (try-on flow), or any other clip-prompt reference. `ugc-tutorial-clip-prompt.md` is self-contained — all rules you need are inside it.**

For each board K, call OpenRouter LLM with system prompt `skill_view("video-generation", "references/ugc-tutorial-clip-prompt.md")`. Inputs: board K image, character image, product image, metadata `{K, N, clip_duration, arc_role, monologue_segment, step_captions, is_last_board, truth_contract}`. Omit `truth_contract` only when the incoming brief has none; otherwise copy it unchanged.

For `arc_role`: pass `BOARD_TUTORIAL_STEPS` for every board (no separate values for first vs. continuation — the only difference is the global step numbers in the captions and the `is_last_board` flag).

For `is_last_board`: pass `true` ONLY when K == N (the final board). The clip-prompt writer adds the CTA tail (~0.5-1s talking-head selfie + downward gesture + brief English CTA phrase) to the end of the final cut ONLY when this flag is true. For all other boards (K < N), no CTA tail.

Output: one Seedance prompt with 4-cut structure inside the clip — Style & Mood / Narrative Summary / Dynamic Description (Cut 1 / Cut 2 / Cut 3 / Cut 4) / Static Description / Audio (with CTA tail if `is_last_board`) / quality suffix.

### 7. Submit Seedance jobs in parallel

```json
generate_video({
  "params": {
    "model": "seedance_2_0",
    "prompt": "<board K prompt>",
    "duration": <per-clip>,
    "aspect_ratio": "9:16",
    "resolution": "1080p",
    "medias": [
      {"value": "<BOARD_K_MEDIA_ID>", "role": "image"},
      {"value": "<CHARACTER_MEDIA_ID>", "role": "image"},
      {"value": "<PRODUCT_MEDIA_ID>", "role": "image"}
    ]
  }
})
/* one call per board, all issued in parallel */
```

One `generate_video` call per board, all issued in parallel — they run concurrently. In TikTok truth mode, forward `brief.duration_policy` without changing this per-board submission cadence.

Per-entry medias (same sources as Step 5), all as `{value, role: "image"}` — backend sniffs type from `value`:

- Board chain-ref → the board `job_id` (a `gpt_image_2` output from Step 5; chain-ref into `seedance_2_0`, no re-upload).
- Character → uploaded id for user-attached, Soul `job_id` for Soul-generated.
- Product → uploaded id (always uploaded).

**Frozen-frame QA (every rendered clip, BEFORE stitching / showing the user):** step through the finished clip's frames (evenly spaced stills + every product close-up + 2–3 mid-word frames) and check by eye: exactly ONE hero product (no clones); hands ≤ 2 per person (check mirrors/edges); absent features stayed absent (no cord/button/port on a product sold on their absence); prop states consistent (a cap is ON or OFF, never both); label not gibberish / mirrored / a real brand; product scale matches the holding hand; lips free of doubled edges / smears on mid-word frames; faces match their references; no baked text or subtitles. Staging failures → fix the prompt inputs and re-roll THAT clip; lip slop → cut spoken words first; baked text → one re-roll, then remove in post. Motion-pass AI review misses frozen-frame defects — this check is human-eye, non-negotiable.

### 8. Poll, download, stitch (MANDATORY)

Poll each job. Download each clip to `output/clip_<K>.mp4` — the numeric suffix MUST equal the board index (clip_1 from Board 1, clip_K from Board K). Strict order, no gaps.

Stitch:

- If N == 1: copy `output/clip_1.mp4` → `output/final.mp4`. Done.
- If N >= 2: invoke the `montage` skill. Pass the clip paths in board order (clip_1.mp4 → clip_N.mp4) and target `output/final.mp4`. Hard cuts only, no transitions. The pipeline is NOT complete until `output/final.mp4` exists on disk.

### 8.5 On-video text + delivery options (ask once, at the end)

On-video text is **OFF by default** — the no-baked-text generation ban always stands; ANY text here is strictly post-render. After `output/final.mp4` exists, ask the user ONCE (a single `ask_question`, bundling both) — UNLESS the brief already answered (then honor it, skip the ask):

1. **On-video text?** — **Subtitles** (the spoken dialogue) · **Hook** (a short top headline) · **Both** · **No text** (default on decline).
2. **Post package?** — caption + hashtags + first comment + loop note (yes / no). See Step 9.

**Subtitles** run through the `montage` skill's **§3 Burned captions (TikTok-style `.ass`)** — the canonical word-level path: timing comes from a **word-level Whisper transcript of the FINAL stitched audio** (montage §3 Steps 1–5: `audio_to_captions.py` → `make_captions.py`), so captions lip-sync to playback and **silence carries no caption** — never planned-beat timings. The **Hook** does NOT use §3 — it renders separately via `make_hook.py` (see the Hook bullet). Per pick:

- **Subtitles** (or **Both**): follow montage §3 Steps 1–5 — extract `output/final_audio.wav`, transcribe word-level, render `output/captions.ass`, burn. Bottom safe-zone, natural sentence case, white + black outline, auto-fit — all baked into `make_captions.py`. No speech → burn NO subtitles; never guess timing.
- **Hook** (or **Both**): render the ≤6-word top headline with **`make_hook.py`** (NOT the montage §3 `.ass` hook) — follow `skill_view("montage", "references/hook.md")`. FIRST ask the user the hook STYLE (box / outline / script) per that reference, in one `ask_question` (skip if the brief named a look); then `make_hook.py "<hook>" --style <chosen> --start 0 --end 2 -o output/hook.png` and overlay the PNG top-centre over the opening beat (the script prints the ffmpeg overlay command). Colour emoji ARE supported (bundled Noto) — keep any the user wants.
- **No text**: skip the burn, deliver `output/final.mp4`.

**Tutorial-specific:** the per-slot `Step N` captions are ALREADY baked into the board frames (top-center). The burned subtitles here stay in the bottom safe-zone (`make_captions.py` default) so they never collide. A top **Hook** would overlap the baked top Step captions — prefer **Subtitles** for tutorials, and only add a Hook if it visibly clears the baked step text.

Deliverable becomes `output/final_captioned.mp4`; keep `output/final.mp4` alongside. Captions are timed to the REAL audio (word-level Whisper), never planned beats.

### 9. Report (+ optional post package)

Only after `output/final.mp4` exists on disk: Show the final deliverable path (`output/final_captioned.mp4` if Step 8.5 burned text, else `output/final.mp4`, with `output/final.mp4` kept alongside) + total duration. Optional: N board paths. Hide: job_ids, element_id, intermediate steps.

**Post package — ONLY if the user opted in at Step 8.5.** Emit a `POST PACKAGE` block as chat text — NEVER baked into the video: **Caption** (one line, comment-bait open loop; anti-slop; truth mode = no unsupported claims) · **Hashtags** (3–5 · 2 niche + 1–2 broad) · **First comment** (pinned; answers the loop / extra proof) · **Loop note** (how the clip loops).

If `output/final.mp4` is missing — Step 8 has not finished. Do not present individual clip paths as the final deliverable.

## `ask_question` — what to ask, what to NEVER ask

`ugc-tutorial-flow` already pins every workflow parameter (model per step, aspect ratio, resolution, audio, `medias` shape, board structure). Duration is a user input, but **everything else is non-negotiable**. Use `ask_question` **only** to fill **creative gaps** the brief left blank — never to "confirm" defaults, offer pipeline forks, or downgrade the chain.

### NEVER ask via `ask_question` (anti-flow forks — defaults are already set)

- **Aspect ratio** (`9:16` vs `16:9` vs `1:1`) — locked to `9:16`. UGC final video is always vertical 9:16 (TikTok / Instagram Reels / YouTube Shorts). Never _"what format do you need?"_, never offer `16:9` / `1:1` forks. Boards are generated horizontal (16:9 for `ugc-flow`; 21:9 for `ugc-product-flow` / `ugc-try-on-flow` / `ugc-tutorial-flow` / `ugc-unboxing-flow`) as an internal pipeline detail — that is the **board** aspect, not the **output** aspect; the user never sees the board format. Do NOT confuse the two.
- **Resolution / quality** (`720p` / `1080p`, image `quality`) — Seedance / `gpt_image_2` defaults are pinned per step. Never ask.
- **Model selection** (_"realistic or stylized?"_, _"which video model?"_, _"nano-banana or seedance?"_) — locked: `seedance_2_0` for video, `gpt_image_2` for boards. Never ask.
- **Audio generation** — audio is always on; Seedance renders native audio (no `generate_audio` flag). Never ask _"with or without audio?"_, _"silent variant?"_, _"music?"_. Voiceover / on-camera dialogue is built into every clip per the pipeline.
- **Identity / Soul ID training** — not applicable to UGC flows. Identity is either the user-provided photo (Step 1.5 `character_provided == true`) or a fresh Soul 2.0 generation (Step 2). Never offer _"train Soul ID"_ as a branch — Soul ID training takes ~30 min, longer than the entire video, and provides no benefit for one-shot UGC ads.
- **N boards / split into N clips** — derived automatically from duration via the Duration → N table. Never ask _"single clip or split into segments?"_, _"long version or short version?"_.
- **Stitch with `montage`** — pinned for `N >= 2`. Never offer _"with hard cuts / without cuts"_ / _"with transitions?"_ forks. Hard cuts only, no transitions, always via the `montage` skill.

### DO ask via `ask_question` (creative gaps only)

Bundle these into **one** `ask_question` call when more than one is missing — do **not** fire a separate question per gap.

| Question | Ask when | Notes |
| --- | --- | --- |
| **Duration** | Brief did not specify a target length. | Offer common UGC picks: `10s` / `15s` / `30s` / `45s` + `Other` (freeform seconds). The agent computes `N` from the Duration → N table — never ask the user how many segments / how long each clip is. |
| **Product** | Brief did not provide a product URL or photo. | Freeform — _"share the product URL or attach a photo of it"_. The agent extracts via `product-analyzer` (URL → `url-extract.md`, photo → `visual-analysis.md`). |

If the brief already contains these answers, **do not re-ask** — proceed silently.

## Critical rules

- Character identity locked via single `character_media_id`. No mid-pipeline regeneration.
- Product Angle Lock in every board prompt — only front-facing side from reference.
- Cut markers (`Hard cut to.`) appear only in Seedance video prompts, never in board prompts.
- No greetings / re-introductions in clips 2..N — continuous monologue, mid-thought entry.
- Hand allocation per slot — two-handed actions force STATIC (locked-off static camera) POV.
- **English-only output everywhere:** step captions, monologue, CTA tail, all examples, all prompt content. No other languages.
- **Step caption rule (mandatory):** each slot displays exactly one caption in the format `"Step N — Heading"`, English Title Case, en-dash separator. Identical typography (font family, size, color, position) across all four slots of one board. Font family is selected per product category (see clip-prompt and boards references for the matrix). No other on-image text of any kind.
- **CTA tail rule (mandatory, only for K == N):** the final ~0.5-1 second of the final cut is a talking-head selfie + downward hand gesture + brief English CTA. Use `"Link in bio."` / `"Follow me."` / `"Subscribe!"` — pick the shortest if monologue is tight. CTA is video-level only; never rendered as a board caption; never numbered as a step.
- **Product Usage Analysis is mandatory:** every board generation must be preceded by a real-world step derivation (Pipeline / 1). Never invent steps the product cannot perform; never skip the analysis.
- **Weight & grip physics (mandatory):** assess product real-world weight before describing how the character holds it.
  - Heavy (large appliance, bottle ≥1L, toolbox-class): two hands required + facial strain (jaw set, slight brow furrow, controlled exhale). Never one-handed.
  - Bulky but light (large box / oversized but not heavy): two hands for stability, but no facial strain.
  - Light (cosmetics, phone, small bottle): one hand, relaxed grip.
  - Tiny (single earring, pill): pinched between thumb and index finger close to lens.

## NOT for this workflow

- Talking-head UGC review with product (creator speaking about product, no step structure) → `ugc-flow`.
- Unboxing / opening the package / reveal moment → `ugc-unboxing-flow`.
- Cinematic / scripted long-form (>15s, non-UGC) → `cinematic-flow`.
- Multiple separate UGC clips (3 × 10s ad variants) → `video-generation`, one `generate_video` call per clip in parallel.
- Product-only no-creator → `product-review-flow` (when it exists).

## References

Load each via `skill_view(name, file_path)`:

- skill `image-generation`, file `references/ugc-tutorial-boards.md` — board generation prompt (GPT Image 2), with Step caption rendering rules.
- skill `video-generation`, file `references/ugc-tutorial-clip-prompt.md` — Seedance prompt writer, with CTA tail logic.
- skill `image-generation`, file `references/soul-v2-ugc-character.md` — character generation.
- skill `product-analyzer`, file `references/url-extract.md` — product extraction from e-commerce URL (URL case).
- skill `product-analyzer`, file `references/visual-analysis.md` — product photo analysis (no-URL case).
