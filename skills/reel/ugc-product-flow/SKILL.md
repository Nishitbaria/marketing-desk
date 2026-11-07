---
name: ugc-product-flow
description: |
  A UGC-style product-only video — the product is the sole focus, voiceover only, no creator speaking on camera (person only as auxiliary hands/POV). Fire only on an explicit product-only / no-creator brief; any ambiguity → ugc-flow.
  Triggers: "only the product", "product-only video", "no talking head", "no creator on camera", "product is the hero", "remove the model", "just the product on screen".
---
# UGC Product Workflow

One pipeline for all UGC product-focused review videos, all durations.

## Mandatory Reference Resolution

This workflow is self-contained. Use ONLY the references in this table. Do NOT substitute legacy references — they belong to deprecated paths and will conflict with this workflow's rules.

**Loading rule:** load each reference with `skill_view(name, file_path)` using the skill name and file path columns below. Do NOT pass `..` relative paths — `file_path` is always relative to the named skill's directory.

| Step | Skill | File path | Do NOT substitute |
| --- | --- | --- | --- |
| Generate the storyboard board | `image-generation` | `references/ugc-product-boards.md` | NOT `ugc-boards.md` (talking-head flow), NOT `ugc-unboxing-boards.md` (unboxing flow), NOT `ugc-tutorial-boards.md` (tutorial flow), NOT `ugc-try-on-boards.md` (try-on flow) |
| Write the Seedance prompt for each clip | `video-generation` | `references/ugc-product-clip-prompt.md` | NOT `ugc-clip-prompt.md` (talking-head flow), NOT `ugc-unboxing-clip-prompt.md` (unboxing flow), NOT `ugc-tutorial-clip-prompt.md` (tutorial flow), NOT `ugc-try-on-clip-prompt.md` (try-on flow) |
| Product URL extraction (URL case) | `product-analyzer` | `references/url-extract.md` | — |
| Product visual analysis (photo case) | `product-analyzer` | `references/visual-analysis.md` | — |

If you find yourself reading `ugc-boards.md`, `ugc-clip-prompt.md`, `ugc-unboxing-boards.md`, `ugc-unboxing-clip-prompt.md`, `ugc-tutorial-boards.md`, `ugc-tutorial-clip-prompt.md`, `ugc-try-on-boards.md`, `ugc-try-on-clip-prompt.md`, or `soul-v2-ugc-character.md` (sibling-flow / character-generation references), or any other clip-prompt reference, while inside this workflow — STOP, return to this SKILL.md, and use the references in the table above.

## Architecture

- Each **board** is a 21:9 strip with 4 vertical 9:16 slots — four sequential narrative moments inside ONE Seedance clip. The 4-slot structure (vs 3 for talking-head) gives the canonical product-demo arc room for four distinct beats: product intro → demo angle A → demo angle B → result state.
- Each board → ONE Seedance call. Inputs: board image + product, all as `medias` with role `image`.
- Within the clip, the prompt describes hard cuts between the 4 slots.
- For >15s: N boards generated sequentially (each conditioned on the previous for consistency), N Seedance clips run in parallel, ffmpeg concat with hard cuts.

## Duration → N boards → per-clip durations

| Total D | N          | Clip durations                    |
| ------- | ---------- | --------------------------------- |
| 4-15    | 1          | D                                 |
| 16-19   | 2          | balance to ≥4s each (D=18 → 14+4) |
| 20-30   | 2          | 15, D-15                          |
| 31-45   | 3          | 15, 15, D-30                      |
| 46-60   | 4          | 15, 15, 15, D-45                  |
| >60     | ceil(D/15) | 15 each, last = remainder ≥4s     |

## Canonical Product Arc — 4 slots per board

**Board 1** follows the canonical 4-slot arc — slots 1–4 always represent these four beats:

| Slot | Role | Frame content |
| --- | --- | --- |
| 1 | PRODUCT-INTRO | Product in its native context — on a surface / in environment / first establishing frame. Person may be entirely absent or only hand / POV-suggestion at edge. |
| 2 | PRODUCT-DEMO-A | Product in active use — first demonstration angle. LLM picks based on product category (e.g., vacuum on carpet, perfume mist on wrist, blender pouring). Person, when in frame, is auxiliary — cropped framing, hands-only, partial body, or first-person POV. |
| 3 | PRODUCT-DEMO-B | Product in active use — second demonstration angle. Different from Slot 2: different action OR different scale OR different context (e.g., vacuum on ceiling vs carpet, macro of texture vs wide functional shot). |
| 4 | PRODUCT-RESULT | Product in result / outcome state — visible result of demo (cleaned floor, styled hair, finished pour) OR product hero shot in final settled context. |

For multi-board (K > 1) videos: Board 1 carries the canonical arc above. Boards 2..N continue with additional product-demo angles through 4 slots each, conditioned on the previous board's final slot.

## Pipeline

### 1. Parse request

Extract product (URL or photo) + duration. URL → `skill_view("product-analyzer", "references/url-extract.md")`. Photo only → `skill_view("product-analyzer", "references/visual-analysis.md")`. Compute N + per-clip durations.

### TikTok selected-handoff truth mode (conditional)

This mode is active only when the incoming structured brief contains `truth_contract`; otherwise this section changes nothing. In truth mode:

- `truth_contract` overrides every generic example, phrase bank, product-analysis inference, specificity rewrite, and rule asking for a concrete number, time, comparison, result, purchase count, or measurement.
- `allowed_product_claims` is the complete allowlist. Use an allowed product claim only as its exact verbatim string. Never paraphrase, strengthen, combine, or derive another claim. An empty allowlist means claim-free consumer copy.
- Forward `truth_contract` unchanged in every board prompt input and clip-writer metadata object. Product descriptions passed downstream stay visual/mechanical unless they contain an exact allowlisted claim.
- When unsupported numbers are forbidden, use observable actions, framing, materials, body placement, and visible mechanics for specificity. Production metadata such as board/clip indices and durations must never become spoken or displayed claims.
- Forward `brief.duration_policy` on every final video request when present.

### TikTok handoff product continuity

When the incoming brief contains `truth_contract`, non-empty
`brief.product_references` are already supplied product images/media and
`brief.requested_product_url` is already supplied URL input. Resolve/upload
those references as needed, but never ask the user to provide the same product
again and never require it to be attached in the current turn. Ask only when
the handoff explicitly lists the product prerequisite as missing.

**Product staging contract (fixed once, reused VERBATIM in every downstream call):** from the analyzer output write ONE canonical product description: shape, material, color, hand-relative size ("palm-sized, fits entirely in one hand, ~15 cm tall" — never object comparisons, they drift), mechanism anatomy (which part is where, what moves, where the output exits), absent features stated visually ("cordless, smooth body, no buttons"), the label (mode-dependent, below), plus one imperfection. Label: when a product PHOTO is uploaded (the standard path), the label keeps its real text — the reference image + the enhancers' Product Angle Lock carry it; write nothing that calls it illegible. Description-only mode (no photo): describe the label as "small label, turned slightly away, too small to read". In BOTH modes, never stage other props with legible text or numbers. Photo-mode caveat: if the photo shows a big readable logo — warn the user once (wordmarks render as gibberish or a real competitor brand — production data) and keep it angled away in prompts only if they agree.

**Derive `voice_gender`** from product analysis:

- Female-coded product (women's cosmetics, women's apparel, female-tailored fragrance) → `female`.
- Male-coded product (men's grooming, men's apparel, male-tailored fragrance) → `male`.
- Unclear / unisex / category-neutral (electronics, food, kitchen, fitness, cars, home goods, etc.) → `random` (pick female / male randomly downstream).

`voice_gender` drives BOTH the off-screen voiceover voice AND the gender of any auxiliary person rendered in frame.

### 2. Upload product

`upload(files=[product.png])` → capture `product_media_id` from `uploads[0].id`. A product is REQUIRED for this flow — it's the hero of every board. The product is referenced in every downstream `medias[]` array by its uploaded id (it's the only `upload` call in this pipeline; everything else chains forward via job-id reference).

## Reference IDs (no re-upload for generated outputs)

`generate_image` / `generate_video` outputs are passed forward via job-id chain-reference — NO download, NO `upload` round-trip. Per-source mapping:

| Source | id field (→ `medias[].value`) |
| --- | --- |
| `upload` (this Step 2 product photo) | `uploads[0].id` |
| `generate_image` board K (Step 4 below) | `job_id` returned by the call |

Board → board (K-1 conditioning K) and board → Seedance both use the board `job_id` chain-ref. `upload` DOES accept a public result URL (via safe-fetch), so a board can be re-uploaded to a `media_input` when a step needs one — the chain-ref `job_id` resolves for Seedance `role:"image"` but NOT for Seedream's `image_references` i2i, which needs a real `media_input` (see the anti-slop pass). Board `job_id` chain-refs feed directly into `seedance_2_0` — no download, no re-upload.

### 3. Draft voiceover script

Voice-over only. NO on-camera dialogue, NO lip-sync, NO greetings (ever — even on Board 1). The voiceover describes the product's benefits, features, and use cases in an emotional UGC tone.

Word density: ≤10s ~ 12-20 words, 11-12s ~ 20-28, 13-15s ~ 28-35. Sum across clips for total. Split into N board-segments, then each into 4 slot-segments (one per cut).

**Craft pass on the voiceover:** anti-slop on every line (no "literally / obsessed / game-changer / holy grail / changed my life / hits different", no corporate words — elevate / seamless / effortless; no "Hey guys"-class openers). Outside truth mode, every claim carries one concrete (a number, a time, a named comparison) — praise without a concrete gets cut. In truth mode, use only exact allowlisted claims and never add a "concrete" to satisfy this craft rule. Echoes/repeats carry no info — cut them first.


Content rules:

- Specific sensory / functional language: `the cordless lift is stupid easy`, `the suction holds even on shag`, `dries in seconds, no streaks`.
- Avoid generic praise (`amazing`, `incredible`, `obsessed`, `10/10`).
- Voice gender follows `voice_gender` from Step 1.

### 4. Generate boards sequentially

**Board 1:**

- `medias`: `[product]` — flat `{value, role}` shape.
- `prompt`: built per `skill_view("image-generation", "references/ugc-product-boards.md")`, injecting board index, slot-by-slot intent (PRODUCT-INTRO → PRODUCT-DEMO-A → PRODUCT-DEMO-B → PRODUCT-RESULT), product description, and `voice_gender` (drives gender of any auxiliary person in frame).
- `aspect_ratio`: `"21:9"`, model `gpt_image_2`

When truth mode is active, include `truth_contract` unchanged in every board prompt input.

v2 medias use the flat `{value, role}` shape — the backend sniffs the source type from `value`:

```json
"medias": [
  {"value": "<PRODUCT_MEDIA_ID>", "role": "image"}
]
```

Poll job_status to terminal state. Capture `(board_1_media_id, board_1_url)` where `board_1_media_id` is the `job_id` returned by `generate_image` and `board_1_url` is `result.url` on terminal status. NO download, NO `upload` round-trip — `gpt_image_2` outputs chain forward via `job_id`.

**Boards 2..N:** Same call. `medias`: `[product, previous_board]` — product as the uploaded id, previous board as the board `job_id` chain-ref:

```json
"medias": [
  {"value": "<PRODUCT_MEDIA_ID>", "role": "image"},
  {"value": "<BOARD_K-1_JOB_ID>", "role": "image"}
]
```

User-message: "Board K of N. Preserve product / location / lighting from the reference board. Story continues with arc role {role}. Action picks up from the last slot of the previous board."

After each board K poll, capture `(board_K_media_id, board_K_url)` exactly as for Board 1.

### 4.5 Anti-slop pass (Seedream 5.0 Pro i2i) — MANDATORY, run for EVERY board

`gpt_image_2` holds identity but slops the render (waxy / HDR / over-smoothed skin). **You MUST run EVERY finished board through** a `seedream_v5_pro` instruction-edit (i2i) that de-slops it while keeping composition and product pixel-faithful — the de-slopped output **REPLACES the board downstream** (its `job_id` / `url` feed the clip enhancer `image_refs` and the Seedance `medias`).

**MANDATORY — do it in TWO tool calls, in this exact order (never skip, never shortcut):**

**Upload the board to a `media_input` first.** Seedream's `image_references` does NOT accept the board's `gpt_image_2` `job_id` (chain-refs resolve for Seedance `role:"image"` but 404 "Media input not found" on Seedream i2i). Upload the board's `url`:
```json
upload({"files": ["<board_url>"]})
```
Capture `uploads[0].id` as `board_upload_id`. (`upload` accepts a public URL via safe-fetch — no download needed.)

**Then run Seedream i2i with that upload id** (`board_upload_id`, NOT the job_id):
```json
generate_image({
  "requests": [{
    "model": "seedream_v5_pro",
    "prompt": "<ANTI-SLOP PROMPT below, verbatim>",
    "aspect_ratio": "21:9",
    "resolution": "2k",
    "medias": [{"value": "<board_upload_id>", "role": "image_references"}]
  }]
})
```

**ANTI-SLOP PROMPT** (fixed, every board):

> KEEP EXACTLY the framing, composition, slot layout, camera distances, poses, subjects and product of this horizontal storyboard sheet and every one of its side-by-side vertical slots — no reframe, no zoom, no crop, no re-layout, no change to the scene, to any person's face / hair / body, or to the product design. CHANGE ONLY micro-realism, applied identically in every slot: true-to-life pore-level skin with natural texture and fine vellus hair, real material detail, even natural daytime light with gentle highlight roll-off and faint true sensor noise, a flat authentic iPhone photo, deep focus. PRESERVE each face's exact shape / width / proportions 1:1 — do NOT squeeze / narrow / slim / stretch any face. AVOID AI-slop: waxy plastic skin, airbrushed poreless skin, beauty-filter smoothing, over-saturation, HDR glow / bloom / halos, oversharpening, teal-orange grade, shallow depth of field, bokeh, cinematic / DSLR look. Keep the product blank / unbranded, no added text, no watermark, no baked slot labels.

- Media role **`image_references`** (NOT `image`); `aspect_ratio` = the board's `21:9`.
- Capture the de-slopped `(board_media_id, board_url)` and OVERWRITE the raw-board refs so the clip step + Seedance chain the cleaned board.
- **Fallback:** moderation block → retry once on `seedream_v5_lite`; total failure → use the raw `gpt_image_2` board (never block).

### 5. Write Seedance prompt per board

**MANDATORY: the system prompt for the LLM call is `skill_view("video-generation", "references/ugc-product-clip-prompt.md")`. Do NOT substitute `ugc-clip-prompt.md` (talking-head flow), `ugc-unboxing-clip-prompt.md` (unboxing flow), `ugc-tutorial-clip-prompt.md` (tutorial flow), `ugc-try-on-clip-prompt.md` (try-on flow), or any other clip-prompt reference. `ugc-product-clip-prompt.md` is self-contained — all rules you need are inside it.**

For each board K, call OpenRouter LLM with system prompt `skill_view("video-generation", "references/ugc-product-clip-prompt.md")`. Inputs: board K image, product image, metadata `{K, N, clip_duration, arc_role, voiceover_segment, voice_gender, truth_contract}`. Omit `truth_contract` only when the incoming brief has none; otherwise copy it unchanged.

For `arc_role`: pass `BOARD_1_PRODUCT_DEMO` when K=1 (canonical 4-slot arc PRODUCT-INTRO → PRODUCT-DEMO-A → PRODUCT-DEMO-B → PRODUCT-RESULT). Pass `BOARD_K_PRODUCT_DEMO` when K>1 (additional product-demo angles, conditioned on previous board's final slot). Do NOT pass legacy values (HOOK / MAIN / CLOSER / BOARD_1_CANONICAL_UNBOXING / BOARD_K_POST_REVEAL) — those are not valid for this flow.

Output: one Seedance prompt with 4-cut structure inside the clip — Style & Mood / Narrative Summary / Dynamic Description (Cut 1 / Cut 2 / Cut 3 / Cut 4 with framing variation per the canonical arc) / Static Description / Audio (off-screen voiceover) / quality suffix.

### 6. Submit Seedance jobs in parallel

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
      {"value": "<PRODUCT_MEDIA_ID>", "role": "image"}
    ]
  }
})
/* one call per board, all issued in parallel */
```

One `generate_video` call per board, all issued in parallel — they run concurrently. In TikTok truth mode, forward `brief.duration_policy` without changing this per-board submission cadence. Board chain-refs forward via the board `job_id` (`gpt_image_2` output → `seedance_2_0` input); the product stays the uploaded id (uploaded in Step 2).

**Frozen-frame QA (every rendered clip, BEFORE stitching / showing the user):** step through the finished clip's frames (evenly spaced stills + every product close-up + 2–3 mid-word frames) and check by eye: exactly ONE hero product (no clones); hands ≤ 2 per person (check mirrors/edges); absent features stayed absent (no cord/button/port on a product sold on their absence); prop states consistent (a cap is ON or OFF, never both); label not gibberish / mirrored / a real brand; product scale matches the holding hand; lips free of doubled edges / smears on mid-word frames; faces match their references; no baked text or subtitles. Staging failures → fix the prompt inputs and re-roll THAT clip; lip slop → cut spoken words first; baked text → one re-roll, then remove in post. Motion-pass AI review misses frozen-frame defects — this check is human-eye, non-negotiable.

### 7. Poll, download, stitch (MANDATORY)

Poll each job. Download each clip to `output/clip_<K>.mp4` — the numeric suffix MUST equal the board index (clip_1 from Board 1, clip_K from Board K). Strict order, no gaps.

Stitch:

- If N == 1: copy `output/clip_1.mp4` → `output/final.mp4`. Done.
- If N >= 2: invoke the `montage` skill. Pass the clip paths in board order (clip_1.mp4 → clip_N.mp4) and target `output/final.mp4`. Hard cuts only, no transitions. The pipeline is NOT complete until `output/final.mp4` exists on disk.

### 7.5 On-video text + delivery options (ask once, at the end)

On-video text is **OFF by default** — the no-baked-text generation ban always stands; ANY text here is strictly post-render. After `output/final.mp4` exists, ask the user ONCE (a single `ask_question`, bundling both) — UNLESS the brief already answered (then honor it, skip the ask):

1. **On-video text?** — **Subtitles** (the spoken voiceover) · **Hook** (a short top headline) · **Both** · **No text** (default on decline).
2. **Post package?** — caption + hashtags + first comment + loop note (yes / no). See Step 8.

**Subtitles** run through the `montage` skill's **§3 Burned captions (TikTok-style `.ass`)** — the canonical word-level path: timing comes from a **word-level Whisper transcript of the FINAL stitched audio** (montage §3 Steps 1–5: `audio_to_captions.py` → `make_captions.py`), so captions lip-sync to playback and **silence carries no caption** — never planned-beat timings. The **Hook** does NOT use §3 — it renders separately via `make_hook.py` (see the Hook bullet). Per pick:

- **Subtitles** (or **Both**): follow montage §3 Steps 1–5 — extract `output/final_audio.wav`, transcribe word-level, render `output/captions.ass`, burn. Bottom safe-zone, natural sentence case, white + black outline, auto-fit — all baked into `make_captions.py`. No speech → burn NO subtitles; never guess timing.
- **Hook** (or **Both**): render the ≤6-word top headline with **`make_hook.py`** (NOT the montage §3 `.ass` hook) — follow `skill_view("montage", "references/hook.md")`. FIRST ask the user the hook STYLE (box / outline / script) per that reference, in one `ask_question` (skip if the brief named a look); then `make_hook.py "<hook>" --style <chosen> --start 0 --end 2 -o output/hook.png` and overlay the PNG top-centre over the opening beat (the script prints the ffmpeg overlay command). Colour emoji ARE supported (bundled Noto) — keep any the user wants.
- **No text**: skip the burn, deliver `output/final.mp4`.

Deliverable becomes `output/final_captioned.mp4`; keep `output/final.mp4` alongside. Captions are timed to the REAL audio (word-level Whisper), never planned beats.

### 8. Report (+ optional post package)

Only after `output/final.mp4` exists on disk: Show the final deliverable path (`output/final_captioned.mp4` if Step 7.5 burned text, else `output/final.mp4`, with `output/final.mp4` kept alongside) + total duration. Optional: N board paths. Hide: job_ids, element_id, intermediate steps.

**Post package — ONLY if the user opted in at Step 7.5.** Emit a `POST PACKAGE` block as chat text — NEVER baked into the video: **Caption** (one line, comment-bait open loop; anti-slop; truth mode = no unsupported claims) · **Hashtags** (3–5 · 2 niche + 1–2 broad) · **First comment** (pinned; answers the loop / extra proof) · **Loop note** (how the clip loops).

If `output/final.mp4` is missing — Step 7 has not finished. Do not present individual clip paths as the final deliverable.

## `ask_question` — what to ask, what to NEVER ask

`ugc-product-flow` already pins every workflow parameter (model per step, aspect ratio, resolution, audio, `medias` shape, board structure). Duration is a user input, but **everything else is non-negotiable**. Use `ask_question` **only** to fill **creative gaps** the brief left blank — never to "confirm" defaults, offer pipeline forks, or downgrade the chain.

### NEVER ask via `ask_question` (anti-flow forks — defaults are already set)

- **Aspect ratio** (`9:16` vs `16:9` vs `1:1`) — locked to `9:16`. UGC final video is always vertical 9:16 (TikTok / Instagram Reels / YouTube Shorts). Never _"what format do you need?"_, never offer `16:9` / `1:1` forks. Boards are generated horizontal (16:9 for `ugc-flow`; 21:9 for `ugc-product-flow` / `ugc-try-on-flow` / `ugc-tutorial-flow` / `ugc-unboxing-flow`) as an internal pipeline detail — that is the **board** aspect, not the **output** aspect; the user never sees the board format. Do NOT confuse the two.
- **Resolution / quality** (`720p` / `1080p`, image `quality`) — Seedance / `gpt_image_2` defaults are pinned per step. Never ask.
- **Model selection** (_"realistic or stylized?"_, _"which video model?"_, _"nano-banana or seedance?"_) — locked: `seedance_2_0` for video, `gpt_image_2` for boards. Never ask.
- **Audio generation** — audio is always on; Seedance renders native audio (no `generate_audio` flag). Never ask _"with or without audio?"_, _"silent variant?"_, _"music?"_. Off-screen voiceover is built into every clip per the pipeline.
- **Identity / Soul ID training** — not applicable. `ugc-product-flow` does not generate a character (product is the hero, no Soul 2.0 person). Identity / Soul ID training is irrelevant to this flow — never offer _"train Soul ID"_ or any persona-identity fork.
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

- Product Angle Lock in every board prompt — only front-facing side from reference.
- **Product is the hero** in every board prompt — person, when present in frame, is auxiliary (cropped framing, hands-only, partial body, or first-person POV) and never focal. Person's identity is not preserved or enforced — different boards may show different incidental people, or no person at all.
- **Voiceover only**. No on-camera dialogue, no lip-sync, no on-camera mouth movement. Person in frame stays silent. Voice-over describes product benefits / features / use cases.
- **Voice gender match**: `voice_gender` (`female` / `male` / `random`) drives BOTH the off-screen voiceover voice AND the gender of any auxiliary person rendered in frame. Never mix in one prompt.
- Cut markers (`Hard cut to.`) appear only in Seedance video prompts, never in board prompts.
- No greetings / re-introductions in voiceover (this is voice-over, not on-camera dialogue — greetings never apply).
- Hand allocation per slot — two-handed actions force STATIC (locked-off static camera) POV. Selfie POV (when used) means one hand holds phone (off-frame), only one free.
- **Weight & grip physics (mandatory):** assess product real-world weight before describing how the auxiliary person (when in frame) holds it.
  - Heavy (large appliance, bottle ≥1L, toolbox-class): two hands required + facial strain (jaw set, slight brow furrow, controlled exhale). Never one-handed.
  - Bulky but light (large box / oversized but not heavy): two hands for stability, but no facial strain.
  - Light (cosmetics, phone, small bottle): one hand, relaxed grip.
  - Tiny (single earring, pill): pinched between thumb and index finger close to lens.

## NOT for this workflow

- Talking-head UGC review with product (creator speaks about product, creator-as-hero) → `ugc-flow`.
- Unboxing / opening the package / reveal moment as the climax → `ugc-unboxing-flow`.
- How-to / step-by-step usage → `ugc-tutorial-flow`.
- Wearing / fitting / applying transformation → `ugc-try-on-flow`.
- Cinematic / scripted long-form (>15s, non-UGC) → `cinematic-flow`.
- Multiple separate UGC clips (3 × 10s ad variants) → `video-generation`, one `generate_video` call per clip in parallel.
- Generic UGC-with-product framing (talking-head creator on camera speaking about the product) → `ugc-flow`. This flow is ONLY for product-as-sole-focal-hero / no-talking-head briefs.

## References

Load each via `skill_view(name, file_path)`:

- skill `image-generation`, file `references/ugc-product-boards.md` — board generation prompt (GPT Image 2).
- skill `video-generation`, file `references/ugc-product-clip-prompt.md` — Seedance prompt writer.
- skill `product-analyzer`, file `references/url-extract.md` — product extraction from e-commerce URL (URL case).
- skill `product-analyzer`, file `references/visual-analysis.md` — product photo analysis (no-URL case).