---
name: ugc-unboxing-flow
description: |
  A UGC-style unboxing video — a creator opens a package on camera with the product reveal as the climax (first-reaction / haul / PR-drop energy).
  Triggers only with ALL: (a) unboxing/reveal/first-reaction intent, (b) UGC framing (UGC/creator/tiktok/"haul"/"PR drop"/"video of me unboxing"), (c) a specific product (image/URL/"this/our/my X").
---
# ugc-unboxing-flow

UGC-style unboxing pipeline — creator opens a package with the reveal as climax. Creative prompt-writing is delegated to backend enhancers. The skill itself owns control flow, gating, sequencing, polling, and stitching. All prompt-construction rules (canonical 4-slot arc PACKED → REVEAL → PRODUCT-FOCUS → SATISFACTION, box logic, weight & grip physics, packing paper, modesty, POV cadence, audio rules, forbidden phrases) live inside the backend system prompts behind `enhancer` — not here.

## Reference Resolution

Only `product-analyzer` references are loaded via `skill_view`. Character / board / clip prompt logic is NOT loaded from local files — it lives in the backend enhancer.

| Step | Resource | How to call |
| --- | --- | --- |
| Product URL extraction (URL case) | `analyzer/product-analyzer/references/url-extract.md` | `skill_view("product-analyzer", "references/url-extract.md")` |
| Product visual analysis (photo case) | `analyzer/product-analyzer/references/visual-analysis.md` | `skill_view("product-analyzer", "references/visual-analysis.md")` |
| Character generation | backend system prompt | `enhancer(flow="ugc-character", inputs={...})` |
| Storyboard generation (4-slot) | backend system prompt | `enhancer(flow="ugc-unboxing-board", inputs={...}, image_refs={...})` |
| Seedance prompt writing (4-cut) | backend system prompt | `enhancer(flow="ugc-unboxing-clip", inputs={...}, image_refs={...})` |

## Reference IDs and URLs (two-channel input — no re-upload for generated outputs)

Throughout this pipeline the same image plays two roles and you MUST capture BOTH every time you create or upload one:

- **ref id** — fed into the next `generate_image` / `generate_video` call inside `medias[].value`. For uploaded files this is a `media_input` UUID; for generate outputs this is the source `job_id` itself, used as a chain-reference. NO `upload` round-trip on generated outputs — they chain forward via job-id; the backend sniffs the source type from `value` (no chain-ref `type` field).
- **`url`** — public HTTPS URL, fed into `enhancer` via `image_refs` so the enhancer LLM can actually _see_ the image when writing the next prompt.

Where they come from:

| Source | id field (→ `medias[].value`) | url field |
| --- | --- | --- |
| `upload` (uploaded product / user-attached character / real package photo) | `uploads[i].id` | `uploads[i].url` |
| `generate_image` Soul character (Step 2) | `job_id` returned by the call | `result.url` on terminal status |
| `generate_image` board K (Step 5) | `job_id` returned by the call | `result.url` on terminal status |

After every Soul / imagegen generation, poll job_status to terminal state and record `(job_id, result.url)` for that asset — NO download, NO re-upload. Pass `job_id` to the next `generate_image` / `generate_video` call's `medias[].value` and `url` to the next `enhancer` call's `image_refs`.

`upload` DOES accept a public result URL (via safe-fetch), so a board can be re-uploaded to a `media_input` when a step needs one — the chain-ref `job_id` resolves for Seedance `role:"image"` but NOT for Seedream's `image_references` i2i, which needs a real `media_input` (see the anti-slop pass). Field names like `character_media_id` are kept as-is — semantically they now hold a chain-ref `job_id` for generated outputs and a `media_input` UUID for uploads. The agent passes that id as `medias[].value` — the backend sniffs the source type from the value, so no `type` field is needed.

## Variety rolls are backend-owned

You do NOT generate `variety_rolls` for the `ugc-character` flow. `enhancer` injects 8 fresh integers in `[0, 99]` server-side before forwarding to the model. Never pass `variety_rolls` inside `inputs` — the wrapper will overwrite anything you put there.

## Architecture

- Each **board** is a 21:9 strip with **4 vertical 9:16 slots** — four sequential narrative moments inside ONE Seedance clip. Unboxing requires 4 slots (vs 3 for talking-head) because the canonical arc has four distinct beats: sealed box → product reveal → product focus → satisfaction.
- Each board → ONE Seedance call. Inputs: board image + character + product (+ optional real package image if user provided one), all as `medias` with role `image`.
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

## Canonical Unboxing Arc — Board 1 slot roles

| Slot | Role | Frame content |
| --- | --- | --- |
| 1 | PACKED | Character with the sealed delivery box in front of them — box closed, taped, untouched. Product NOT visible. |
| 2 | REVEAL | Product just out of the box, held or placed next to character. Box may be at frame edge (just-emptied) or already gone. Peak surprise. |
| 3 | PRODUCT-FOCUS | The product alone, framed as the hero (close-up of product in hands or extended toward lens). Box GONE. |
| 4 | SATISFACTION | Character settled with the product — confident pose, warm grin, product in hand or beside them. Box GONE. |

For multi-board (K > 1) videos: Board 1 carries the canonical arc above. Boards 2..N continue the story past the reveal — exploring / using / demonstrating the product through 4 slots each, conditioned on the previous board's final slot. The sequential-board mechanic is identical to ugc-flow's, only with 4 slots per board instead of 3.

| K    | arc_role                     |
| ---- | ---------------------------- |
| K==1 | `BOARD_1_CANONICAL_UNBOXING` |
| K>1  | `BOARD_K_POST_REVEAL`        |

## Pipeline

### 1. Parse request

Extract: product (URL or photo), duration, gender, optional real package/box photo, any user-specified overrides (location, hair color, ethnicity, outfit register, clothing, mood, props, etc.). Compute N + per-clip durations from the tables above.

### TikTok selected-handoff truth mode (conditional)

This mode is active only when the incoming structured brief contains `truth_contract`; otherwise this section changes nothing. In truth mode:

- `truth_contract` overrides every generic example, phrase bank, product-analysis inference, specificity rewrite, and rule asking for a concrete number, time, comparison, result, purchase count, or measurement.
- `allowed_product_claims` is the complete allowlist. Use an allowed product claim only as its exact verbatim string. Never paraphrase, strengthen, combine, or derive another claim. An empty allowlist means claim-free consumer copy.
- Forward `truth_contract` unchanged in every board and clip enhancer `inputs`. Product descriptions passed downstream stay visual/mechanical unless they contain an exact allowlisted claim.
- When unsupported numbers are forbidden, use observable actions, framing, materials, body placement, and visible mechanics for specificity. Production metadata such as board/clip indices and durations must never become spoken or displayed claims.
- Forward `brief.duration_policy` on every final video request when present.

### TikTok handoff product continuity

When the incoming brief contains `truth_contract`, non-empty
`brief.product_references` are already supplied product images/media and
`brief.requested_product_url` is already supplied URL input. Resolve/upload
those references as needed, but never ask the user to provide the same product
again and never require it to be attached in the current turn. Ask only when
the handoff explicitly lists the product prerequisite as missing.

### 1.1 Product analysis (mandatory — always via product-analyzer)

Product MUST always be normalized through `product-analyzer` regardless of input form. This guarantees URL and photo paths produce the same structural product data — no asymmetric downstream behavior.

- **URL provided** → `skill_view("product-analyzer", "references/url-extract.md")`. Run the extraction pipeline. Result includes `product_description`, gallery images, brand, category signals.
- **Photo only** → `skill_view("product-analyzer", "references/visual-analysis.md")`. Run the visual analysis. Result includes `product_description`, category, usage mechanic.

After analysis, also determine:

- `tier`: `"luxury" | "premium" | "drugstore"` from packaging visual cues + brand identity (never look up price).
- `category`: e.g. `"skincare" | "cosmetics" | "fragrance" | "food" | "fitness" | "cars" | "tech" | ...`.

`tier` and `category` are decided here ONCE and passed into both the character and board enhancers — no re-detection downstream.

**Product staging contract (fixed once, reused VERBATIM in every downstream call):** from the analyzer output write ONE canonical product description: shape, material, color, hand-relative size ("palm-sized, fits entirely in one hand, ~15 cm tall" — never object comparisons, they drift), mechanism anatomy (which part is where, what moves, where the output exits), absent features stated visually ("cordless, smooth body, no buttons"), the label (mode-dependent, below), plus one imperfection. Label: when a product PHOTO is uploaded (the standard path), the label keeps its real text — the reference image + the enhancers' Product Angle Lock carry it; write nothing that calls it illegible. Description-only mode (no photo): describe the label as "small label, turned slightly away, too small to read". In BOTH modes, never stage other props with legible text or numbers. Photo-mode caveat: if the photo shows a big readable logo — warn the user once (wordmarks render as gibberish or a real competitor brand — production data) and keep it angled away in prompts only if they agree.

### 1.2 Input tier classification

Classify the user request based on specificity:

| `input_tier` | Trigger | Behavior |
| --- | --- | --- |
| `auto` | 1-5 words, no scenario, "make unboxing", or empty brief | Full autopilot |
| `guided` | 1-3 sentences with general idea, tone, mood, or rough flow | Preserve user's tone, build slot structure inside enhancer |
| `director` | 4+ sentences with specific scenario, dialogue intent, shot list, location sequence, or props | Map user beats 1:1 onto slots |

The classified `input_tier` is passed into both `ugc-unboxing-board` and `ugc-unboxing-clip` enhancers.

### 1.4 Accent & quirk (OPT-IN)

If the brief names an identifiable origin for the creator, or asks for "weird"/"viral" character energy, ask ONE combined optional question (accent consent + one quirk offer) — bundled into the same single `ask_question` call as the other creative gaps, never a separate extra call. Never add an accent the user didn't approve; default = neutral English, no quirk. If opted in: write the persona/quirk sentence ONCE (identity + attitude, e.g. "a young Korean it-girl — English is her second language and you hear it in every sentence") and carry it VERBATIM into EVERY enhancer call — appended to `user_request` for board/clip calls, into `user_overrides` for the character call — restated each time, or it drifts. Accent reality check (production data): text-only accent enforcement lands ~1 render in 3 — if the user can drop a 5–10s voice sample, attach it to the Seedance generation as an audio reference (`@voice: accent and vocal delivery reference only — do not copy words, only the accent, melody, and timbre. Reference.`); offer this once at intake, don't block on it.

### 1.5 Persona source — detect `character_provided`

Set `character_provided = true` if the user attached one or more person photos alongside the product brief (any framing — close-up face, full-body, any pose). Otherwise `character_provided = false`.

If `character_provided == true`:

- Upload the user-provided person photo via `upload(...)` → capture `(character_media_id, character_url)` from `uploads[0].id` + `uploads[0].url`.
- **SKIP Step 2 entirely** (no Soul 2.0 generation, no character enhancer call). The user's photo IS the character.
- Proceed directly to Step 3.

If `character_provided == false`:

- Proceed to Step 2.

This is a hard gate, not a question to the user. Do NOT call `ask_question` to confirm — if a person photo is attached, treat it as the character. Quality / framing / pose of the user's photo is the user's own responsibility.

### 2. Character generation — only when `character_provided == false`

**This step is MANDATORY when `character_provided == false`. It is NOT optional, NOT skippable, and NOT mergeable with Step 5. Without a real `character_media_id` captured here, Step 5 (board generation) cannot run — boards require an existing character identity image to lock against. Never describe the character inline in a board prompt as a substitute for running this step. If `character_provided == false` and you do not yet have `character_media_id`, you are NOT ready for Step 3 — return here.**

Call the character enhancer. Text-only — no `image_refs` for this flow. The wrapper auto-generates `variety_rolls`; do NOT include them in `inputs`.

```json
enhancer({
  "flow": "ugc-character",
  "inputs": {
    "tier": "<luxury | premium | drugstore>",
    "category": "<skincare | cosmetics | fragrance | food | fitness | cars | tech | ...>",
    "gender": "<woman | man>",
    "user_request": "<original brief verbatim — backup parsing source + tone signals>",
    "user_overrides": {
      "location": "<optional>",
      "hair_color": "<optional>",
      "hair_style": "<optional>",
      "ethnicity": "<optional>",
      "outfit_register": "<optional>",
      "age_band": "<optional>",
      "mood": "<optional>",
      "...": "..."
    },
    "previous_character_traits": null
  }
})
```

The enhancer returns `{"prompt": "<full Soul 2.0 prompt string>"}`. Submit:

```json
generate_image({
  "requests": [{
    "model": "text2image_soul_v2",
    "prompt": "<enhancer output>",
    "aspect_ratio": "3:4",
    "params": {"quality": "2k", "enhance_prompt": false}
  }]
})
```

Poll job_status to terminal state. Capture `(character_media_id, character_url)` where `character_media_id` is the `job_id` returned by `generate_image` and `character_url` is `result.url` on terminal status. NO download, NO `upload` round-trip — Soul outputs chain forward via the `job_id` reference (verified across `motion-design-flow:625-626` and `soul-id:106`).

`character_media_id` feeds the next `generate_image.medias[].value`; `character_url` feeds the next `enhancer.image_refs`. Outfit is fixed across boards unless the story explicitly transitions to a new context.

### 3. Upload product (and optional package)

`upload(files=[product.png])` → capture both `uploads[0].id` (as `product_media_id`) AND `uploads[0].url` (as `product_url`). Skip if no product. (If product came from URL, the analyzer pipeline already produced uploadable image(s) in Step 1.1.)

If the user supplied a real package/box photo: `upload(files=[package.png])` → capture `(package_media_id, package_url)`. These are used as Slot 1 (PACKED) packaging reference in the board enhancer. If no package photo is provided, the board enhancer falls back to a generic plain brown taped delivery box — no further action needed.

### 4. Draft full monologue

Word density: ≤10s ~ 12-20 words, 11-12s ~ 20-28, 13-15s ~ 28-35. Sum across clips for total. Split into N board-segments, then mentally into 4 slot-segments per board (the slot-level split is the enhancer's job — the agent only delivers the per-board segment).

Greetings + product introduction allowed ONLY in Board 1. Other boards continue mid-thought.

**Craft pass on the full monologue (before splitting into segments):**

- Unboxing's canonical arc stays (the package IS the premise — no product delay); sharpen it with story craft: the caved-in confession frame ("I saw this fourteen times on my feed. I caved."), genuine surprise scripted as a BODY event at the reveal, ONE "but then" beat, the CTA riding inside the resolution. In truth mode, quoted examples are structural only; never copy their factual or numeric wording unless it is an exact allowlisted claim.
- Anti-slop pass on every line: the first words are never `Okay wait / Okay so / OMG / Hey guys / So basically / Stop scrolling / You NEED this / Story time`; banned anywhere: "literally", "obsessed", "game-changer", "holy grail", "changed my life", "hits different", corporate words (elevate / seamless / effortless). Friction openers beat enthusiasm ("I almost returned this."). Outside truth mode, every claim carries one concrete — a number, a time, a named comparison; praise without a concrete gets cut. In truth mode, use only exact allowlisted claims and never add a "concrete" to satisfy this craft rule.
- Board-1 opener flavor (optional): H1 impact action is ALREADY this flow's default — the first word lands mid-event over the box; don't re-add it. The opener may instead carry ONE alternate catalog flavor compatible with the canonical PACKED first cut — H2 mid-sentence confession, opened on word four as if walked-in-on (the caved-in frame delivered this way); H5 hostile open, a challenge aimed straight at the viewer; H7 result-first (the line refers backwards to what made them cave); H4 freeze-beat (one short performed hold locked on the sealed box, ≤0.7s, then the line). The flavor colors the words: the first-word constraint and anti-slop openers govern every variant, and the PACKED visual arc is untouched. No H8 (structural, core-flow only).
- At most ONE peak reaction per clip in the monologue (the clip enhancer may stage up to 2 — the arc peak plus an optional closer beat, each product-motivated).
- Echoes/repeats count toward the word budget but carry no info — cut them first.

**First-word constraint (positional, applies to every audio line):** the literal FIRST WORD of every board's monologue segment must be hook content directly — NEVER `OK / Okay / Okay so / Alright / Alright so / So / Yeah so / Right so / Um / Well / Like / Wait / Wait what / Hold on` as the opener. These read as AI-recording-warmup. They ARE allowed mid-sentence anywhere later — the constraint is positional, first word only. If the drafted opener starts with one of these, rewrite to lead with the hook content. (Mirrored inside the `ugc-unboxing-clip` enhancer — the clip writer also enforces this.)

### 5. Generate boards sequentially

For each board K in 1..N, call the board enhancer. Pass the public URLs in `image_refs` so the enhancer LLM can see the references when writing the prompt; pass the matching `*_media_id`s inside `inputs` so the downstream `gpt_image_2` call can condition on them:

```json
enhancer({
  "flow": "ugc-unboxing-board",
  "inputs": {
    "K": <board index>,
    "N": <total boards>,
    "arc_role": "<BOARD_1_CANONICAL_UNBOXING | BOARD_K_POST_REVEAL>",
    "clip_duration": <4-15>,
    "tier": "<from Step 1.1>",
    "input_tier": "<from Step 1.2>",
    "user_request": "<original brief verbatim>",
    "truth_contract": "<brief.truth_contract unchanged, or omit when absent>",
    "product_description": "<from product-analyzer, or null>",
    "character_media_id": "<from Step 1.5 or Step 2>",
    "product_media_id": "<from Step 3, or null>",
    "package_media_id": "<from Step 3, or null when no real package photo>",
    "previous_board_media_id": "<board K-1 media_id, or null when K==1>"
  },
  "image_refs": {
    "product_url": "<from Step 3, or omit when no product>",
    "character_url": "<from Step 1.5 or Step 2>",
    "package_url": "<from Step 3, or omit when no real package photo>",
    "previous_board_url": "<board K-1 url, or omit when K==1>"
  }
})
```

Each `*_url` above accepts either a single URL string OR an array of 1-10 URL strings. Use arrays when you have multiple meaningful references for one role: `product_url` for product-analyzer gallery angles (front / back / side / packaging); `package_url` when the user uploaded several shots of the real package (closed / open / from above) — the enhancer can then nail Slot 1 PACKED more precisely; `character_url` when the user attached multiple person photos in Step 1.5 (tighter identity lock). The board enhancer's `@Image1..@ImageN` reference table adapts via the auto-prepended IMAGE MANIFEST. `previous_board_url` is single.

Returns `{"prompt": "<full gpt_image_2 prompt string>"}`. Submit:

```json
generate_image({
  "requests": [{
    "model": "gpt_image_2",
    "prompt": "<enhancer output>",
    "aspect_ratio": "21:9",
    "medias": [
      {"value": "<PRODUCT_MEDIA_ID>", "role": "image"},
      {"value": "<CHARACTER_MEDIA_ID>", "role": "image"}
      /* + {"value": "<PACKAGE_MEDIA_ID>", "role": "image"} if real package photo provided */
      /* + {"value": "<BOARD_K-1_JOB_ID>", "role": "image"} if K>1 */
    ]
  }]
})
```

All medias entries use the v2 flat shape `{value, role: "image"}` — the backend sniffs the source type from `value`, so no `type` field is needed:

- Product is always uploaded (a `media_input` id).
- Character from Step 1.5 / Step 2 (uploaded id for user-attached, Soul `job_id` for Soul-generated).
- Real package photo (when supplied) is always uploaded (a `media_input` id).
- Previous board chain-ref (K>1) is the board `job_id`.

Poll job_status to terminal state. Capture `(board_K_media_id, board_K_url)` where `board_K_media_id` is the `job_id` returned by `generate_image` and `board_K_url` is `result.url` on terminal status. NO download, NO `upload` round-trip — `gpt_image_2` outputs chain forward via `job_id`. Pass `board_K_media_id` into the next K's `previous_board_media_id` (in `inputs`) and `board_K_url` into the next K's `previous_board_url` (in `image_refs`). Both are also needed in Step 6 below.

### 5.5 Anti-slop pass (Seedream 5.0 Pro i2i) — MANDATORY, run for EVERY board

`gpt_image_2` holds identity but slops the render (waxy / HDR / over-smoothed skin). **You MUST run EVERY finished board through** a `seedream_v5_pro` instruction-edit (i2i) that de-slops it while keeping faces, composition and product pixel-faithful — the de-slopped output **REPLACES the board downstream** (its `job_id` / `url` feed the clip enhancer `image_refs` and the Seedance `medias`).

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

**ANTI-SLOP PROMPT** (fixed, every board):

> KEEP EXACTLY the framing, composition, slot layout, camera distances, poses, subjects and product of this horizontal storyboard sheet and every one of its side-by-side vertical slots — no reframe, no zoom, no crop, no re-layout, no change to the scene, to any person's face / hair / body, or to the product design. CHANGE ONLY micro-realism, applied identically in every slot: true-to-life pore-level skin with natural texture and fine vellus hair, real material detail, even natural daytime light with gentle highlight roll-off and faint true sensor noise, a flat authentic iPhone photo, deep focus. PRESERVE each face's exact shape / width / proportions 1:1 — do NOT squeeze / narrow / slim / stretch any face. AVOID AI-slop: waxy plastic skin, airbrushed poreless skin, beauty-filter smoothing, over-saturation, HDR glow / bloom / halos, oversharpening, teal-orange grade, shallow depth of field, bokeh, cinematic / DSLR look. Keep the product blank / unbranded, no added text, no watermark, no baked slot labels.

- Media role **`image_references`** (NOT `image`); `aspect_ratio` = the board's `21:9`.
- Capture the de-slopped `(board_K_media_id, board_K_url)` and OVERWRITE the raw-board refs so the clip step + Seedance chain the cleaned board. For K>1, the `previous_board_*` fed into board gen is the de-slopped K-1.
- **Fallback:** moderation block → retry once on `seedream_v5_lite`; total failure → use the raw `gpt_image_2` board (never block).

### 6. Write Seedance prompt per board

For each K in 1..N, call the clip enhancer. Pass `image_refs` so the enhancer can read the board image as its narrative map and verify identity/product continuity:

```json
enhancer({
  "flow": "ugc-unboxing-clip",
  "inputs": {
    "K": <board index>,
    "N": <total boards>,
    "clip_duration": <4-15>,
    "arc_role": "<BOARD_1_CANONICAL_UNBOXING | BOARD_K_POST_REVEAL>",
    "monologue_segment": "<board K's spoken text, verbatim>",
    "input_tier": "<from Step 1.2>",
    "user_request": "<original brief verbatim — used by clip enhancer for tone detection>",
    "truth_contract": "<brief.truth_contract unchanged, or omit when absent>",
    "board_media_id": "<from Step 5>",
    "character_media_id": "<...>",
    "product_media_id": "<... or null>"
  },
  "image_refs": {
    "board_url": "<board K url from Step 5>",
    "character_url": "<from Step 1.5 or Step 2>",
    "product_url": "<from Step 3, or omit when no product>"
  }
})
```

Each `*_url` accepts a single URL or an array of 1-10. Reuse the same `product_url` and `character_url` arrays you passed in Step 5 so the clip enhancer reconciles continuity against every reference the board reasoned about (especially important for the PRODUCT-FOCUS → SATISFACTION transition where the product is hero). `board_url` is single (only one board sheet per clip).

Returns `{"prompt": "<full Seedance prompt string>"}`.

### 7. Submit Seedance jobs in parallel

```json
generate_video({
  "requests": [{
    "model": "seedance_2_0",
    "prompt": "<board K prompt>",
    "duration": <per-clip>,
    "duration_policy": "<brief.duration_policy in TikTok truth mode, otherwise omit>",
    "aspect_ratio": "9:16",
    "resolution": "1080p",
    "medias": [
      {"value": "<BOARD_K_MEDIA_ID>", "role": "image"},
      {"value": "<CHARACTER_MEDIA_ID>", "role": "image"},
      {"value": "<PRODUCT_MEDIA_ID>", "role": "image"}
    ]
  }]
})
/* one call per board, all issued in parallel */
```

One `generate_video` call per board, all issued in parallel — they run concurrently. In TikTok truth mode, forward `brief.duration_policy` without changing this per-board submission cadence.

Per-entry medias (same sources as Step 5), all as `{value, role: "image"}` — backend sniffs type from `value`:

- Board chain-ref → the board `job_id` (a `gpt_image_2` output from Step 5).
- Character → uploaded id for user-attached, Soul `job_id` for Soul-generated.
- Product → uploaded id (always uploaded).

Board `job_id` chain-refs feed directly into `seedance_2_0` — no download, no re-upload.

**Frozen-frame QA (every rendered clip, BEFORE stitching / showing the user):** step through the finished clip's frames (evenly spaced stills + every product close-up + 2–3 mid-word frames) and check by eye: exactly ONE hero product (no clones); hands ≤ 2 per person (check mirrors/edges); absent features stayed absent (no cord/button/port on a product sold on their absence); prop states consistent (a cap is ON or OFF, never both); label not gibberish / mirrored / a real brand; product scale matches the holding hand; lips free of doubled edges / smears on mid-word frames; faces match their references; no baked text or subtitles. Staging failures → fix the prompt inputs and re-roll THAT clip; lip slop → cut spoken words first; baked text → one re-roll, then remove in post. Motion-pass AI review misses frozen-frame defects — this check is human-eye, non-negotiable.

### 8. Poll, download, stitch (MANDATORY)

Poll each job. Download each clip to `output/clip_<K>.mp4` — the numeric suffix MUST equal the board index (clip_1 from Board 1, clip_K from Board K). Strict order, no gaps.

Stitch:

- If N == 1: copy `output/clip_1.mp4` → `output/final.mp4`. Done.
- If N >= 2: invoke the `montage` skill. Pass the clip paths in board order (clip_1.mp4 → clip_N.mp4) and target `output/final.mp4`. Hard cuts only, no transitions. The pipeline is NOT complete until `output/final.mp4` exists on disk.

### 8.5 On-video text + delivery options (ask once, at the end)

On-video text is **OFF by default** — the no-baked-text generation ban always stands; ANY text here is strictly post-render. After `output/final.mp4` exists, ask the user ONCE (a single `ask_question`, bundling both) — UNLESS the brief already answered (then honor it, skip the ask):

1. **On-video text?** — **Subtitles** (the spoken words) · **Hook** (a short top headline) · **Both** · **No text** (default on decline).
2. **Post package?** — caption + hashtags + first comment + loop note (yes / no). See Step 9.

**Subtitles** run through the `montage` skill's **§3 Burned captions (TikTok-style `.ass`)** — the canonical word-level path: timing comes from a **word-level Whisper transcript of the FINAL stitched audio** (montage §3 Steps 1–5: `audio_to_captions.py` → `make_captions.py`), so captions lip-sync to playback and **silence carries no caption** — never planned-beat timings. The **Hook** does NOT use §3 — it renders separately via `make_hook.py` (see the Hook bullet). Per pick:

- **Subtitles** (or **Both**): follow montage §3 Steps 1–5 — extract `output/final_audio.wav`, transcribe word-level, render `output/captions.ass`, burn. Bottom safe-zone, natural sentence case, white + black outline, auto-fit — all baked into `make_captions.py`. No speech → burn NO subtitles; never guess timing. (Word-level Whisper transcribes only spoken words; bracketed non-verbal sounds never appear.)
- **Hook** (or **Both**): render the ≤6-word top headline with **`make_hook.py`** (NOT the montage §3 `.ass` hook) — follow `skill_view("montage", "references/hook.md")`. FIRST ask the user the hook STYLE (box / outline / script) per that reference, in one `ask_question` (skip if the brief named a look); then `make_hook.py "<hook>" --style <chosen> --start 0 --end 2 -o output/hook.png` and overlay the PNG top-centre over the opening beat (the script prints the ffmpeg overlay command). Colour emoji ARE supported (bundled Noto) — keep any the user wants.
- **No text**: skip the burn, deliver `output/final.mp4`.

Deliverable becomes `output/final_captioned.mp4`; keep `output/final.mp4` alongside. Captions are timed to the REAL audio (word-level Whisper), never planned beats.

### 9. Report (+ optional post package)

Only after `output/final.mp4` exists on disk: Show the final deliverable path (`output/final_captioned.mp4` if Step 8.5 burned text, else `output/final.mp4`, with `output/final.mp4` kept alongside) + total duration. Optional: N board paths. Hide: job_ids, element_id, intermediate steps.

**Post package — ONLY if the user opted in at Step 8.5.** Emit a `POST PACKAGE` block as chat text — NEVER baked into the video: **Caption** (one line, comment-bait open loop; anti-slop; truth mode = no unsupported claims) · **Hashtags** (3–5 · 2 niche + 1–2 broad) · **First comment** (pinned; answers the loop / extra proof) · **Loop note** (how the clip loops).

If `output/final.mp4` is missing — Step 8 has not finished. Do not present individual clip paths as the final deliverable.

## `ask_question` — what to ask, what to NEVER ask

`ugc-unboxing-flow` pins every workflow parameter (model per step, aspect ratio, resolution, audio, `medias` shape, board structure, 4-slot canonical arc). Duration is a user input. Real-package photo is an optional creative input. Everything else is non-negotiable. Use `ask_question` **only** to fill **creative gaps** the brief left blank — never to "confirm" defaults, offer pipeline forks, or downgrade the chain.

### NEVER ask via `ask_question`

- **Aspect ratio** — locked to `9:16` final video, `21:9` board. Never offer forks.
- **Resolution / quality** — pinned per step.
- **Model selection** — locked: `text2image_soul_v2` for character, `gpt_image_2` for boards, `seedance_2_0` for video.
- **Audio generation** — always on. Seedance renders native audio (no `generate_audio` flag).
- **Identity / Soul ID training** — not applicable.
- **N boards / split** — derived automatically from duration.
- **Stitch / transitions** — hard cuts only via `montage` skill.
- **Canonical 4-slot arc** — Board 1 always PACKED → REVEAL → PRODUCT-FOCUS → SATISFACTION. Never offer "alternative arc" forks.

### DO ask via `ask_question` (creative gaps only)

Bundle into **one** `ask_question` call when more than one is missing — never one question per gap.

| Question | Ask when | Notes |
| --- | --- | --- |
| **Duration** | Brief did not specify a target length. | Offer common UGC picks: `10s` / `15s` / `30s` / `45s` + `Other` (freeform seconds). |
| **Product** | Brief did not provide a product URL or photo. | Freeform — _"share the product URL or attach a photo of it"_. |
| **Real package photo** | Brief did not mention whether the user has a real package photo, AND no box photo is already attached to the conversation. | First call: offer `Yes — I'll attach a photo of the package` / `No — use a generic plain brown delivery box` / `Other`. If user picks **Yes** AND no package photo is yet attached, fire a **second `ask_question`** with freeform request _"Please attach a photo of the package now"_ and HALT — do NOT proceed to Step 2 until the photo actually arrives. After the photo arrives, `upload` it and capture `(package_media_id, package_url)`. If user picks **No** (or changes their mind in the follow-up), set `package_media_id = null` and proceed silently with the generic-box fallback. |

If the brief already contains these answers, **do not re-ask** — proceed silently.

## Critical rules

- Character identity locked via single `character_media_id`. No mid-pipeline regeneration except via the Failure handling protocol below.
- Product analysis happens ONCE in Step 1.1 — `tier` and `product_description` are decided there and reused.
- Boards are generated SEQUENTIALLY (each conditioned on the previous via `previous_board_media_id`). Seedance clips are submitted in ONE parallel batch.
- The agent passes structured inputs to `enhancer` — never prose. All creative rules belong inside the enhancer.
- For every image created or uploaded, capture BOTH `(media_id, url)`. `media_id` feeds the next `generate_image` / `generate_video` call's `medias[].value` (the backend sniffs the source type from the value); `url` feeds the next `enhancer.image_refs`. Dropping the url leaves the enhancer blind for the next call.
- NO `upload` round-trip on `generate_image` / `generate_video` outputs — they chain forward via job-id reference. The only `upload` calls in this pipeline are: (a) user-attached character photo in Step 1.5 if `character_provided == true`, (b) product photo in Step 3, (c) optional real package/box photo in Step 3.
- Never compute or pass `variety_rolls` yourself — the wrapper generates them for `ugc-character` and overwrites anything you supply.
- Cut markers (`Hard cut to.`) appear only in Seedance video prompts (enhancer output), never in board prompts.
- No greetings / re-introductions in clips 2..N — continuous monologue, mid-thought entry.
- **Slot 1 of Board 1 MUST always show the sealed delivery box** (product NOT visible). The product reveal lands in Slot 2.
- **Box disappearance**: Slot 1 sealed, Slot 2 just-emptied at frame edge or gone, Slots 3-4 GONE. Never re-introduce the box.
- **Weight & grip physics** is enforced inside the board and clip enhancers — heavy items require two hands + visible strain; light items relaxed one-hand grip; paired products never balanced on one palm.
- A `Yes` answer to the package-photo question is an **incomplete state** until an actual image is attached to the conversation. Never proceed to Step 2 (character generation) on a bare "Yes" — fire a follow-up `ask_question` requesting the user to attach the photo, and wait. Only set `package_media_id` after the photo is received and `upload`-ed. If the user changes their mind in the follow-up and confirms "no / use generic", set `package_media_id = null` and proceed.

## Failure handling — character re-roll

If Step 5 (board) or Step 7 (Seedance) fails twice in a row on the same call, assume NSFW rejection of the Soul character render. Re-submit the original enhancer-returned character prompt from Step 2 to `generate_image` with the same Soul 2.0 params — new seed, same described person, vibe locked. Capture fresh `(character_media_id, character_url)`, discard all `board_K_media_id` (they referenced the rejected character), re-run Step 5 onward. Cap: 2 re-rolls per session. Beyond that, stop and report — do NOT fall through to `generate_video` with empty `medias[]` (= text-to-video, wrong product).

## NOT for this workflow

- Talking-head UGC review with product (creator speaking about product, no unboxing arc) → `ugc-flow`.
- Product UGC variants → sibling flows (`ugc-product-flow`, `ugc-try-on-flow`, `ugc-tutorial-flow`).
- Cinematic / scripted long-form (>15s, non-UGC) → `workflow-generation/cinematic-flow`.
- Multiple separate UGC clips (3 × 10s ad variants) → `video-generation`, one `generate_video` call per clip in parallel.