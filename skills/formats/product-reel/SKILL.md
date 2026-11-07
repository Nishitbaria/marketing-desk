---
name: product-reel
description: |
  A photoreal product commercial reel of the user's real product — requires a real product photo; the product is the hero, no person on camera. Triggers: "product reveal", "automotive reveal".
---

# product-reel

Product Commercial (Track B / MDC8) pipeline. Three-stage shape (Stage A character sheet → Stage B 9-shot 3×3 storyboard → Stage C Seedance clip). The skill itself owns control flow, gating, sequencing, polling, and Stage A character sheet generation. All Stage B / Stage C creative rules (9-shot anatomy, scale alternation, lighting tier, signature beats, reference tier vocabulary, sandwich anti-grid 4-layer, diegetic typography discipline, anti-vocabulary, validated failure modes) live inside the backend system prompts behind `enhancer` — not here.

Scope is strictly Track B — premium product commercial reel for a real product the user attached. Reference tier: Tom Ford / Cartier / Persol luxury / BMW / Apple premium dynamic / ASICS / Salomon / Nike athletic / Buck Studio / Tendril motion design / Pentagram editorial-technical. Photoreal CGI permitted (the only mode where HR-3 REALISM BAN does NOT apply — see Hard Rules below).

## Reference Resolution

| Step | Resource | How to call |
|---|---|---|
| Stage A character sheet prompt | inline below (this SKILL.md) | direct `generate_image(model=gpt_image_2, ...)` with user's product photo as `medias[]` |
| Stage B 9-shot 3×3 storyboard prompt | backend system prompt | `enhancer(flow="productMD-board", inputs={...}, image_refs={...})` |
| Stage C Seedance clip prompt | backend system prompt | `enhancer(flow="productMD-clip", inputs={...}, image_refs={...})` |

## Reference URLs vs job IDs (two-channel input — no re-upload)

Throughout this pipeline the same image plays two roles and you MUST capture BOTH every time you create one. **No `upload` step in this pipeline** for outputs of `generate_image` — `gpt_image_2` outputs are passed forward via chain-reference using the original `job_id` plus `result.url`. The user's original product photo IS uploaded once (via `upload`) at the very beginning so it can be used as `medias[]` in Stage A.

- **`job_id`** — the id returned by `generate_image` for the completed job. Fed into the next `generate_image` call inside `medias[].value` as a chain-reference (the backend infers the media type from the value).
- **`url`** — public HTTPS URL (`result.url` on the terminal job status). Fed into `enhancer` via `image_refs` so the enhancer LLM can actually *see* the image when writing the next prompt.

Where they come from:

| Source | id field | url field |
|---|---|---|
| `generate_image` completed job (Stage A character sheet, Stage B storyboard) | `job_id` returned by the call (carry forward as chain-reference) | `result.url` / `url` on terminal job status |
| `upload` (Stage 0 user's product photo only) | `uploads[i].id` → `product_photo_media_id` | `uploads[i].url` → `product_photo_url` |

After Stage A and Stage B generations, poll job_status to terminal state, then record `(job_id, result.url)` for that asset. Pass `job_id` to the next `generate_image` call's `medias[]` (as the flat `value`) and `url` to the next `enhancer` call's `image_refs`.

## Architecture

- **Stage 0 upload** — user's product photo (chat attachment) → `upload` once → capture `(product_photo_media_id, product_photo_url)`. This is the ONLY `upload` call in the pipeline.
- **Stage A** — fixed-English character sheet prompt (lives here in the skill, NOT in an enhancer). One `generate_image` call to `gpt_image_2` with the product photo as `medias[]` foundation produces a 5-view (or 6-view 2×3 for two-colorway) character sheet — the production bible for cross-shot consistency. Tier-specific background + lighting baked into the prompt.
- **Stage A.2** — `ask_question` lets the user confirm the character sheet or regenerate.
- **Stage B** — picked character sheet becomes the foundation. ONE `enhancer(flow="productMD-board", ...)` call writes the 9-shot 3×3 storyboard prompt → ONE `generate_image` call to `gpt_image_2` with the character sheet as `medias` reference produces the 9-shot 3×3 storyboard sheet.
- **Stage C** — ONE `enhancer(flow="productMD-clip", ...)` call writes the Seedance prompt → ONE `generate_video` batch with one request object by default. Extra variants are repeated request objects only when explicitly requested.

## Aspect ratio defaults

| Step | Default aspect | Behavior |
|---|---|---|
| Stage A character sheet | `3:2` | always 3:2 (sheet shape per Track B doctrine), never asked |
| Stage B 9-shot 3×3 storyboard sheet | `3:2` | always 3:2 (sheet shape per Track B doctrine), never asked |
| Stage C Seedance | `16:9` default for Track B; `9:16` supported but rare for product commercial | ask only if brief did not specify |

The 9-shot 3×3 sheet aspect stays `3:2` regardless of video target — Track B sheets are always 3:2 because each thumbnail inside is 16:9 horizontal (matching the deliverable). The Seedance `aspect_ratio` follows the user's Step 0a answer.

If brief is unambiguous about aspect ratio (`"vertical reel"` / `"for tiktok"` / `"9 by 16"` / `"square post"`) — pick silently. If ambiguous — `ask_question` once via Step 0a below, then carry the answer through to Stage C only (sheet aspects stay 3:2).

## Pipeline

### 1. Parse request

Extract: duration (default 15s), aspect ratio (default 16:9 for Track B unless brief specifies), brand name (if user mentions one — otherwise generic product showcase), product photo attachment status (HARD GATE — see Step 0b), reference tier hint from brief vocabulary (Tom Ford / BMW / ASICS / Buck / Pentagram — see Step 0c), tagline (if user provided one verbatim — never invent).

Decide `tier_signal` from brief:
- Luxury vocabulary (`"timeless"` / `"heritage"` / `"crafted"` / `"editorial"` / `"luxury"` / `"premium"` + watch / fragrance / jewelry / case / leather) → Tom Ford / Cartier / Persol tier.
- Premium dynamic vocabulary (`"engineering"` / `"performance"` / `"mechanical"` / `"precision"` + car / watch / camera / device) → BMW / Apple / Bugatti tier.
- Athletic vocabulary (`"speed"` / `"trail"` / `"run"` / `"athletic"` / `"sport"` + sneaker / running / fitness) → ASICS / Salomon / Nike tier.
- Motion design vocabulary (`"hyperkinetic"` / `"kinetic"` / `"chaos"` / `"max energy"` + tech / gaming / drink) → Buck / Tendril tier.
- Editorial-technical (`"dev tool"` / `"developer"` / `"technical"` / `"editorial-grade"` + tech product) → Pentagram / Buck editorial-technical tier.

If brief has no clear tier vocabulary → ask via Step 0c.

Decide `variant_count` (number of repeated Stage C request objects):
- DEFAULT `variant_count = 1` for product-reel.
- If brief contains explicit variance hedge phrase — set `variant_count = N`:
  - `"best-of-N"` / `"premium variants × N"` / `"× N takes"` / `"N alternate cuts"` / `"do N variations"` / `"N versions"` / `"make N versions"` / `"give me N"`
  - Clamp range: `1 ≤ N ≤ 6`. If N > 6 in brief — clamp to 6 and note in chat ("requested {original}, capped to 6 — each Seedance variant is ~$0.20-0.40").
  - If N ≥ 4 — write a one-line reflection in chat before submitting Seedance: `"Submitting N parallel Seedance request objects in one approved call."`
- If brief doesn't mention variance hedge → keep default `variant_count = 1` (Track B single-take default).

### 2. Step 0z — Person detection (HARD ROUTE BEFORE ANY ASK)

Track B is product cinematography — the hero is the product, not a human. If the brief implies a human is on camera with the product (model wears / actor uses / talent demonstrates / portrait of person holding X), this is `tv-ad-flow` territory. Detect and route BEFORE asking aspect ratio or anything else (don't waste user interactions if we're handing off).

After Step 1 parse, scan `user_request` for person tokens. Match is case-insensitive and requires whole-word token boundary.

**Person tokens:**

```
person, man, woman, male, female, model, actor, actress, human, talent, hero, character, wears, wearing, wear, holds, holding, hold, hand, hands, body, portrait, face
```

**False-positive guards** — DO NOT count a match if the token appears in any of these contexts (check ±2 words around the token):

- `personal use` / `personally` / `personality` — `person` here carries non-human sense.
- `talent acquisition` / `talent pool` / `talent management` — `talent` here carries hiring sense.
- `face of the brand` / `face value` / `face plate` / `front face` / `dial face` / watch case `face` — `face` here is a brand-identity phrase or a product-surface noun.
- `character sheet` / `character design` (when referring to the Stage A production bible) — `character` here is the production-doc term.
- `hand-crafted` / `hand-stitched` / `handmade` / `by hand` — `hand` here is a craftsmanship adjective, not a human limb in frame.
- `body of work` / `body copy` / `car body` / `bottle body` — `body` here is a product-anatomy noun, not a human body.
- `hero shot` / `hero product` / `hero view` — `hero` here is the cinematography term, not a person.
- `model code` / `model number` / `latest model` — `model` here is the product variant noun.

If at least one person token matches AND no false-positive guard applies → fire `ask_question`:

```
ask_question({
  questions: [{
    question: "The brief mentions a person on camera with the product. product-reel is pure product cinematography (no humans in frame). For human-centric ads, tv-ad-flow runs the full character + dialogue/VO + dramaturgy pipeline. Which path?",
    header: "Person in ad — route?",
    multiSelect: false,
    options: [
      {label: "Switch to tv-ad-flow", description: "Full character + script + location + dramaturgy pipeline. Hand off the brief verbatim."},
      {label: "Stay in productMD — product only, no human in frame", description: "Strip the person from the brief locally and continue Track B as pure product cinematography."},
      {label: "Cancel — let me re-do the brief", description: "Abort. User restarts with a clearer brief."}
    ]
  }]
})
```

Branch on user pick:

- **Switch to tv-ad-flow** → STOP product-reel immediately. Hand off the original brief verbatim to `tv-ad-flow`. Do NOT continue to Step 0a / 0b / 0c / Stage A.
- **Stay in productMD** → strip the person references from the brief locally and write a one-line chat note: `"Removed person references from brief — proceeding as pure product cinematography."` Then proceed to Step 0a.
- **Cancel** → abort the run; user will restart with a clearer brief.

If no person token matches OR every match falls under a false-positive guard — proceed silently to Step 0a (no ask).

### 3. Step 0a — Aspect ratio (only if brief did not specify)

Skip if brief unambiguously implies aspect. Otherwise:

```
ask_question({
  questions: [{
    question: "What aspect ratio for this reel?",
    header: "Aspect ratio",
    multiSelect: false,
    options: [
      {label: "16:9 horizontal", description: "Default for product commercial — desktop / YouTube / OLV / cinema"},
      {label: "9:16 vertical", description: "Mobile — Reels / TikTok / Shorts (rare for Track B but supported)"},
      {label: "1:1 square", description: "Feed posts — Instagram / LinkedIn"}
    ]
  }]
})
```

Carry the answer through Stage C only. Sheet aspects (Stage A character sheet + Stage B storyboard) stay `3:2` regardless.

### TikTok selected-handoff product continuity

When the incoming brief contains `truth_contract`, non-empty
`brief.product_references` are already supplied product images/media and
`brief.requested_product_url` is already supplied URL input. Resolve/upload
those references as needed and count them in the Step 0b product-photo gate;
never require the same product to be attached in the current turn and never ask
for it again unless the handoff explicitly lists the product prerequisite as
missing. When `required_product_count` is one, treat additional references as
angles of that same product unless the handoff says otherwise.

For this TikTok handoff only:

Ordinary productMD requests without `truth_contract` keep the existing pipeline
unchanged.

- Use `brief.duration_seconds` instead of the 15s default in Stage B, Stage C,
  storyboard timing, and final video generation.
- Pass `brief.truth_contract` unchanged as `inputs.truth_contract` to
  `productMD-board` and `productMD-clip`.
- Pass `brief.duration_policy` to the final
  `generate_video` request.
- Stage A is visual-only. Do not add consumer-facing product copy, numbers,
  results, prices, comparisons, or unverified labels to the character sheet.
- Allowed product copy is limited to exact
  `truth_contract.allowed_product_claims`; an empty list means no product claims.

### 4. Step 0b — Product photo gate (HARD GATE) + multi-product detection

**Track B requires the user's actual product photo. NEVER fabricate the product.** Scan chat attachments plus TikTok handoff `product_references` and count the resolved product inputs as `attachment_count`.

**Branch A — exactly 1 image attached (default / single product):**

- Upload via `upload(files=[...])` → capture `(product_photo_media_id, product_photo_url)`.
- Set `multi_product_mode = "single"`, `product_count = 1`, `product_media_ids = [<product_photo_media_id>]`, `product_photo_urls = [<product_photo_url>]`.
- Proceed to Step 0b.2 (logo gate). Step 0b.1 is SKIPPED in this branch.

**Branch B — 2+ images attached (potential multi-product or single + extras):**

Fire `ask_question` to categorize the attachments:

```
ask_question({
  questions: [{
    question: "I see N images attached. How should I treat them?",
    header: "Attachment categorization",
    multiSelect: false,
    options: [
      {label: "All different products — multi-product reel", description: "Each image is a separate product. You'll pick how they appear in the reel (sequential / variety / group still-life) in the next step."},
      {label: "All angles of the SAME product", description: "Treat as ONE product with multiple reference angles. First attachment is the hero; the others are supplementary refs for the Stage A character sheet."},
      {label: "1 is the product, rest are logo / style refs", description: "Identify which image is the product now; remaining images go to logo gate (Step 0b.2) or are dropped as style refs."},
      {label: "Let me categorize per-image", description: "Freeform follow-up per attachment."}
    ]
  }]
})
```

Branch on user pick:

- **All different products** → batched `upload(files=[file1, file2, ..., fileN])` (one call, N files in array). Capture `product_media_ids = [<id1>, <id2>, ..., <idN>]` and `product_photo_urls = [<url1>, ..., <urlN>]`. Set `product_count = N`. Proceed to **Step 0b.1 — Multi-product mode pick**.
- **All angles of SAME product** → batched `upload`. First attachment becomes the hero (`product_photo_media_id = id1`, `product_photo_url = url1`). Remaining N-1 images become Stage A `image_refs.extra_angle_urls` (auxiliary references for the Stage A character sheet prompt — the prompt body references them as `@Image2 / @Image3 / ...` if used). Set `multi_product_mode = "single"`, `product_count = 1`, `product_media_ids = [<id1>]`. Proceed to Step 0b.2.
- **1 product + rest are logo / style refs** → batched `upload`. Ask user a short freeform follow-up "Which attachment index (1..N) is the product?". That id becomes `product_photo_media_id`. Held-aside ids feed into Step 0b.2 (logo gate) or are dropped. Set `multi_product_mode = "single"`, `product_count = 1`. Proceed to Step 0b.2.
- **Categorize per-image** → freeform follow-up enumerating each image: ask user "image K: product / logo / style ref / drop?" per attachment. Build categorized arrays from answers. If multiple products → `multi_product_mode != "single"` → proceed to Step 0b.1; else single product → Step 0b.2.

**Branch C — 0 images attached and no handoff product references:**

STOP. Do NOT proceed. Do NOT auto-generate a product via foundation generator (that would be a different product from the user's actual brand asset — strict guard).

```
ask_question({
  questions: [{
    question: "Product Reel requires the actual product hero photo. Please attach it, or pick another mode.",
    header: "Product photo missing",
    multiSelect: false,
    options: [
      {label: "I'll attach the product photo now", description: "Wait for upload, then re-run from Step 0b."},
      {label: "Switch to kinetic-reel (foundation-generated product surrogate)", description: "Use kinetic-reel's Stage A moodboard generator. Renders a product-LIKE subject, not the user's actual product."},
      {label: "Cancel — pick a different mode", description: "User picks from typography-reel / infographic-reel / motion-design-reel externally."}
    ]
  }]
})
```

NEVER auto-route around this gate. NEVER write a Stage A prompt without the user's actual product photo(s) as `medias[]`.

### 5. Step 0b.1 — Multi-product mode pick (only when `product_count ≥ 2` from Step 0b Branch B)

Fires ONLY when Step 0b Branch B routed "All different products" (or per-image categorization yielded ≥2 products). Skip entirely otherwise.

```
ask_question({
  questions: [{
    question: "You have N products. How should they appear in the reel?",
    header: "Multi-product mode",
    multiSelect: false,
    options: [
      {label: "Sequential — N separate videos (one per product)", description: "Run product-reel N times sequentially, one reel per product. Each product gets its own 9-shot storyboard + Seedance film."},
      {label: "Variety — 1 video, each product gets ≥1 dedicated shot", description: "Single 9-shot storyboard where each product has at least one focus shot. Products rotate / alternate across the 9 shots; the reel reads as a brand-line showcase."},
      {label: "Group still-life — 1 video, all products co-staged in EACH shot", description: "Single 9-shot storyboard where ALL products appear together in every shot. Composition / angles / lighting vary; products stay together as a group throughout."}
    ]
  }]
})
```

Branch on user pick:

- **Sequential** → set `multi_product_mode = "sequential"`. STOP the linear flow at this step. Outer loop: for each product in `product_media_ids[]`, RESTART the entire pipeline from Step 0a — each iteration treated as a single-product run with `product_media_ids = [<that_one>]`, `product_count = 1`, `multi_product_mode = "single"`. After N iterations, present N independent videos to user. Logo gate (Step 0b.2), Reference tier (Step 0c), and Stage A through Stage C apply PER iteration.
- **Variety** → set `multi_product_mode = "variety"`. Keep `product_media_ids[]` array intact. Proceed to Step 0b.2 (logo applies to the single combined reel) → Step 0c → Stage A (variety branch produces N character sheets in parallel).
- **Group still-life** → set `multi_product_mode = "group"`. Keep `product_media_ids[]` array intact. Proceed to Step 0b.2 → Step 0c → Stage A (group branch produces 1 group character sheet from all N product photos).

### 6. Step 0b.2 — Logo gate (OPTIONAL)

After the product photo is confirmed in Step 0b, check whether the user also provided a brand logo asset. Logo is OPTIONAL — product-reel works without one — but if the user supplied a logo, capture it here as a separate asset (not as a typeset wordmark text overlay).

Detection logic — priority order:

**1. Multiple attachments in chat.** If chat has more than one image attached and the first was assigned as the product photo in Step 0b, the remaining attachment(s) are candidate logo asset(s). Fire `ask_question`:

```
ask_question({
  questions: [{
    question: "I see multiple attachments. The first is the product photo. Is the second attachment your brand logo?",
    header: "Logo attached?",
    multiSelect: false,
    options: [
      {label: "Yes — that's the logo", description: "Upload as logo asset, ask for placement next."},
      {label: "No — it's another product angle / lifestyle ref", description: "Treat as a supplementary product reference (passed to Stage A enhancer image_refs only, not used as a separate logo)."},
      {label: "No — skip", description: "Ignore the extra attachment. No logo in this reel."}
    ]
  }]
})
```

**2. Brief mentions logo without an extra attachment.** If brief contains tokens `logo`, `our logo`, `brand mark`, `wordmark`, `logotype`, `brand asset` AND only the single product photo was attached, ask:

```
ask_question({
  questions: [{
    question: "Brief mentions a logo. Do you want to attach your brand logo asset, or skip and let the closer be atmospheric?",
    header: "Logo source",
    multiSelect: false,
    options: [
      {label: "Attach the logo now", description: "Wait for upload, then continue."},
      {label: "Skip — no logo asset, closer stays atmospheric", description: "Continue without logo. Final shot is atmospheric per default behavior."}
    ]
  }]
})
```

**3. Brief is silent on logo AND only one attachment (product photo).** Skip Step 0b.2 entirely. No logo in pipeline.

If logo source is **attached** → `upload(files=[...])` for the logo file → capture `(logo_media_id, logo_url)`. Set `logo_source = "attached"`.

If logo source is **skip** → set `logo_source = "none"`, `logo_media_id = null`, `logo_url = null`. Proceed to Step 0c.

After the logo asset is locked, ask placement:

```
ask_question({
  questions: [{
    question: "Where should the logo appear in the 9-shot storyboard?",
    header: "Logo placement",
    multiSelect: false,
    options: [
      {label: "Closer (shot 09)", description: "Default — logo lands on the final beat as the brand resolve. Atmospheric build through shots 01-08, brand sign-off on 09."},
      {label: "Opener (shot 01)", description: "Logo appears on the first beat as the brand entry, then dissolves into pure product cinematography."},
      {label: "Both opener and closer (01 + 09)", description: "Brand bookends — logo entry on shot 01, atmospheric middle shots 02-08, logo closer on shot 09."}
    ]
  }]
})
```

Capture `logo_placement = "opener" | "closer" | "both"`. Default = `"closer"` when ambiguous.

When `logo_source == "none"` → `logo_placement = null` and `logo_media_id` / `logo_url` are `null`.

Carry through to Stage B enhancer inputs (`logo_source` / `logo_placement` / `logo_media_id` / `logo_url`) and Stage B `medias[]` array (second entry carrying the logo `value` when `logo_source == "attached"`). Stage C is unchanged — the storyboard already encodes the logo visually; Seedance `medias[]` stays single-ref (storyboard only).

**HR-2 / graphic overlay interaction:** on shots where the logo asset is placed (per `logo_placement`), the asset REPLACES the typeset wordmark text overlay. Other graphic overlay shots not covered by the logo asset keep the existing rules (ALL WHITE typeset wordmark on shots 01 / 09 where applicable, tagline on shot 08 if `brand_tagline != null`, ZERO color throughout).

### 7. Step 0c — Reference tier (only if `tier_signal` is unresolved)

If Step 1 derived a clear `tier_signal` from brief vocabulary — skip Step 0c, pick silently and document the choice.

If ambiguous — ask:

```
ask_question({
  questions: [{
    question: "Which production register for the reel?",
    header: "Reference tier",
    multiSelect: false,
    options: [
      {label: "Tom Ford / Cartier / Persol — luxury chiaroscuro", description: "Pure pitch-black void, slow contemplative motion-control, monochrome palette, editorial tempo 1.8-2.5s/shot"},
      {label: "BMW / Apple / Bugatti — premium dynamic mechanical", description: "Bot&Dolly motion-control precision, ARRI Alexa cinema, controlled speed ramps, 1.4-1.8s/shot, monochrome + optional neon accent"},
      {label: "ASICS / Salomon / Nike — athletic / lifestyle", description: "Light gray studio cyclorama, motion-control + boom, scenic props, monochrome + neon accent on key feature, 1.3-1.7s/shot"},
      {label: "Buck Studio / Tendril — motion design hyperkinetic", description: "Hyperkinetic camera, stutter cuts with time-freeze, datamosh transitions, brand-color saturated, 0.8-1.5s/shot"},
      {label: "Pentagram / Buck editorial-technical", description: "Studio bright, technical labels, HUD overlays + wireframe, white hairline brackets, 1.5-2.0s/shot, editorial gray scale + technical accent"}
    ]
  }]
})
```

Carry the picked `reference_tier` through Stage A (background + lighting baked in), Stage B (enhancer input), Stage C (enhancer input → master camera + pacing + palette).

### 8. Stage A — Character sheet via gpt_image_2

Stage A branches by `multi_product_mode`:

- **`single`** (default; or sequential-loop iteration) → 1 character sheet from 1 product photo. The path below.
- **`sequential`** → already exited at Step 0b.1 via outer loop; each iteration RESTARTS the pipeline as single. This Stage A branch is the per-iteration single path.
- **`variety`** → N parallel character sheets (one per product). See **Variety branch** below.
- **`group`** → 1 group character sheet with all N products co-staged. See **Group branch** below.

Fixed-English prompt regardless of user's brief language. Tier-specific background + lighting baked in via two `<TIER_*>` placeholders.

#### Single / sequential-iteration branch (default, 1 product)

```python
generate_image({
  "requests": [{
    "model": "gpt_image_2",
    "prompt": "Generate a product character sheet — production bible for cross-shot consistency. Subject: the product shown in @Image1, preserved with engineering-grade identity (silhouette / proportions / material / key features all locked from @Image1). Format: single 16:9 sheet, light gray paper background #DDDDDD, 5 product views arranged in a single horizontal row — hero front view as the dominant central element, plus 4 secondary angle insets (3/4 left, side profile, 3/4 right, top-down or extreme macro of the most distinctive material feature). Studio cyclorama lighting throughout the sheet — clear, evenly-lit, even shadow under each view — NOT dramatic chiaroscuro (the sheet must show the product clearly across all angles; dramatic lighting is for the storyboard, not the bible). Hairline 1pt borders between views, gutters 28px, outer margin 40px. Above each view: monospace bold label (`HERO` / `3/4 L` / `SIDE` / `3/4 R` / `MACRO`). Top bar: brand placeholder + 'CHARACTER SHEET v1' + product category in monospace. Bottom section: color palette swatches extracted from the product (3 hex codes), material callouts (chrome / leather / glass / metal / fabric / ceramic), dimensions placeholder, model code placeholder. PHOTOGRAPHIC FRAME PURITY: no document-metadata chips inside individual view panels — labels and palette live in chrome margins outside the photographic frames. <TIER_BACKGROUND>. <TIER_LIGHTING>. Photoreal CGI register, ARRI Alexa / Cinema 4D Octane / ProRes 4K production value.",
    "aspect_ratio": "3:2",
    "resolution": "2k",
    "params": {"quality": "high"},
    "medias": [
      {"value": "<product_photo_media_id>", "role": "image"}
    ]
  }]
})
```

If Step 0b Branch B routed "All angles of SAME product" → append additional `medias[]` entries (one `value` per extra angle: `id2 / id3 / ...`) so the character sheet generator sees ALL angles when composing the bible.

#### Variety branch (N products, 1 reel) — N parallel character sheet calls

```python
# one generate_image call per product, submitted in parallel for K in 0..N-1
generate_image({
  "requests": [{
    "model": "gpt_image_2",
    "prompt": "<SAME character sheet prompt as single branch, with `the product` referring to `@Image1` — one per call>",
    "aspect_ratio": "3:2",
    "resolution": "2k",
    "params": {"quality": "high"},
    "medias": [{"value": "<product_media_ids[K]>", "role": "image"}]
  }]
})
```

Submit N `generate_image` calls in parallel — one per product, each a single-product character sheet build. Poll each terminal state. Capture `character_sheet_job_ids = [<id1>, <id2>, ..., <idN>]` and `character_sheet_urls = [<url1>, <url2>, ..., <urlN>]` — both arrays of length N.

CRITICAL: `character_sheet_urls[]` MUST be passed to Stage B enhancer `image_refs` as the FULL array (the enhancer LLM needs to SEE every product to compose the variety storyboard). Stage B `medias[]` MUST include ALL N character_sheet_job_ids as chain-refs (one entry per product) so the storyboard `gpt_image_2` call has visibility into every product asset.

#### Group branch (N products co-staged, 1 reel) — single grouped character sheet

```python
generate_image({
  "requests": [{
    "model": "gpt_image_2",
    "prompt": "Generate a GROUP product character sheet — production bible for cross-shot consistency of a multi-product still-life. Subjects: ALL N products shown in @Image1 / @Image2 / ... / @ImageN, preserved with engineering-grade identity (silhouette / proportions / material / key features all locked per product). Format: single 16:9 sheet, light gray paper background #DDDDDD. Layout: hero composition shows all N products together as a unified group still-life (standing / lying / arranged adjacently per product category — bottles in a row / sneakers side-by-side / watches on a tray / electronics arranged in a line). Below the hero group, 4 secondary insets show alternate group angles (3/4 group view, side group view, overhead group view, extreme macro of a detail where two product surfaces meet or sit adjacent). Studio cyclorama lighting throughout the sheet — clear, evenly-lit, even shadow under each view. Hairline 1pt borders between views, gutters 28px, outer margin 40px. Above each view: monospace bold label (`HERO GROUP` / `3/4 GROUP` / `SIDE GROUP` / `OVERHEAD GROUP` / `DETAIL MACRO`). Top bar: brand placeholder + 'GROUP CHARACTER SHEET v1' + product line in monospace. Bottom section: combined palette swatches (3 hex codes from the unified composition), per-product material callouts (N callouts, one per product), dimensions placeholder, line code placeholder. PHOTOGRAPHIC FRAME PURITY: no document-metadata chips inside individual view panels. Products maintain consistent spatial relationship across the 5 views — same relative positioning, scaling, and proximity. <TIER_BACKGROUND>. <TIER_LIGHTING>. Photoreal CGI register, ARRI Alexa / Cinema 4D Octane / ProRes 4K production value.",
    "aspect_ratio": "3:2",
    "resolution": "2k",
    "params": {"quality": "high"},
    "medias": [
      {"value": "<product_media_ids[0]>", "role": "image"},
      {"value": "<product_media_ids[1]>", "role": "image"}
      // ... continue for ALL N products as separate medias entries
    ]
  }]
})
```

Single `generate_image` call. All N product photos in `medias[]` array (the generator must SEE all products to compose the group sheet). Poll terminal → capture `(character_sheet_job_id, character_sheet_url)` — single sheet, single id/url. Set `character_sheet_job_ids = [<id>]` (length 1), `character_sheet_urls = [<url>]` (length 1) so downstream Stage B handles the group like single but with `multi_product_mode = "group"` passed to enhancer.

Where `<TIER_BACKGROUND>` and `<TIER_LIGHTING>` are replaced as follows:

- **Tom Ford / Cartier / Persol** tier:
  - `<TIER_BACKGROUND>`: `Sheet background stays light gray studio #DDDDDD for the bible doc — but every view's photographic frame uses pure pitch-black #000000 void with NO atmospheric haze, NO visible light beams as graphic, NO dust motes, NO surfaces beneath product`
  - `<TIER_LIGHTING>`: `Single hard top-light beam through silk softbox diffusion onto product. Sharp specular sculpting on curved edges. Deep crushed shadows preserved. Multi-source pro lighting on the product silhouette`
- **BMW / Apple / Bugatti** tier:
  - `<TIER_BACKGROUND>`: `Sheet background stays light gray studio #DDDDDD. Each view's photographic frame uses cool gray atmospheric gradient #1A1A1A → #2C2C2C with soft hero glow visible, optional subtle volumetric beam`
  - `<TIER_LIGHTING>`: `ARRI Alexa cinema-grade clean precision lighting. Multi-source. Halation on specular highlights. Fine 35mm grain layer`
- **ASICS / Salomon / Nike** tier:
  - `<TIER_BACKGROUND>`: `Sheet background stays light gray studio #DDDDDD. Each view's photographic frame uses off-white #DDDDDD soft gradient cyclorama. Product appears slightly levitating with soft contact shadow beneath. Optional scenic props (rocks / textures) in macro view only`
  - `<TIER_LIGHTING>`: `Clean directional key from upper-left at 30°. Soft fill. Athletic lifestyle register. Clean precision lighting, no dramatic chiaroscuro`
- **Buck Studio / Tendril** tier:
  - `<TIER_BACKGROUND>`: `Sheet background stays light gray studio #DDDDDD. Each view's photographic frame uses brand-color saturated background (extract dominant color from @Image1 product palette) with depth atmospheric haze`
  - `<TIER_LIGHTING>`: `Mixed lighting depending on view — hero front gets dramatic, secondary views get clean studio. Saturated color grade`
- **Pentagram / Buck editorial-technical** tier:
  - `<TIER_BACKGROUND>`: `Sheet background stays light gray studio #DDDDDD. Each view's photographic frame uses studio bright off-white background with optional white hairline brackets around hero view marking technical dimensions`
  - `<TIER_LIGHTING>`: `Studio bright editorial lighting. Optional HUD overlays / wireframe schematics / tracked technical labels visible on hero view only — NO HUD on secondary insets (HR-2 MIN-TEXT compliance — only the hero view shows technical chrome)`

Poll job_status to terminal state. From the completed job record(s) capture `character_sheet_job_ids[]` and `character_sheet_urls[]` arrays (length 1 for single / group / sequential-iteration; length N for variety). Render the character sheet image(s) in chat for the user so they can confirm.

### 9. Stage A.2 — Confirm character sheet (per `multi_product_mode`)

**Single / sequential-iteration / group mode** — single sheet to confirm:

```
ask_question({
  questions: [{
    question: "Here's the character sheet — production bible for the 9-shot storyboard that follows. The product('s/s') silhouette, material, key features will be locked from this sheet across all 9 shots. Confirm or regenerate.",
    header: "Confirm character sheet",
    multiSelect: false,
    options: [
      {label: "Confirm — proceed to 9-shot storyboard", description: "Character sheet looks right. Continue to Stage B."},
      {label: "Regenerate — different lighting tier", description: "Switch reference tier (re-ask Step 0c) and re-render character sheet."},
      {label: "Regenerate — same tier, different framing", description: "Keep tier, ask what to change (e.g. more macro detail / different hero angle / different palette swatch extraction), loop Stage A."},
      {label: "Cancel — pick a different mode", description: "Abort product-reel. User can switch to kinetic-reel / typography-reel / motion-design-reel externally."}
    ]
  }]
})
```

**Variety mode** — N sheets rendered side-by-side, single confirm question:

```
ask_question({
  questions: [{
    question: "Here are the N character sheets — one production bible per product. All N will feed into a single 9-shot variety storyboard where each product gets at least one focus shot. Confirm all or regenerate a specific one.",
    header: "Confirm character sheets (N)",
    multiSelect: false,
    options: [
      {label: "Confirm all — proceed to 9-shot variety storyboard", description: "All N character sheets look right. Continue to Stage B variety branch."},
      {label: "Regenerate sheet K — same tier, different framing", description: "Pick which sheet (1..N) to regenerate via short freeform follow-up; other N-1 sheets are kept."},
      {label: "Regenerate ALL — different lighting tier", description: "Switch reference tier (re-ask Step 0c) and re-render all N sheets as N parallel calls."},
      {label: "Cancel — pick a different mode", description: "Abort. User restarts with single product or different flow."}
    ]
  }]
})
```

Branch on user pick (any mode):
- **Confirm** → proceed to Step 10 (Stage B).
- **Regenerate different tier** → loop back to Step 0c, then re-run Stage A (all sheets in variety mode; the single in others).
- **Regenerate sheet K** (variety only) → freeform follow-up "what to change in sheet K", then a single `generate_image` call for THAT product only, replacing entry K in `character_sheet_job_ids[]` / `character_sheet_urls[]` arrays. Other sheets untouched. Re-render and re-confirm.
- **Regenerate same tier, different framing** (single / group / sequential) → short freeform follow-up asking what to change, then re-run Stage A with adjustment baked into the prompt.
- **Cancel** → abort, do not call Stage B.

### 10. Stage B — 9-shot 3×3 storyboard via enhancer

Call the storyboard enhancer. Pass ALL character sheet `url`s in `image_refs` so the enhancer LLM can SEE every bible (one per product in variety mode, one for single / group / sequential-iteration); pass ALL `character_sheet_job_ids[]` inside `inputs` so the downstream `gpt_image_2` call can chain-reference them.

```json
enhancer({
  "flow": "productMD-board",
  "inputs": {
    "reference_tier": "tom-ford | bmw | asics | buck | pentagram",
    "aspect_ratio": "16:9 | 9:16 | 1:1",
    "duration_seconds": "<duration from Step 1>",
    "brand_name": "<verbatim from brief, or null>",
    "brand_tagline": "<verbatim from brief, or null>",
    "user_request": "<original brief verbatim — backup parsing source + tone signals>",
    "multi_product_mode": "single | sequential | variety | group",
    "product_count": <int — length of character_sheet_job_ids array; 1 for single/group/sequential-iteration, N for variety>,
    "truth_contract": "<TikTok handoff truth_contract, or null>",
    "character_sheet_job_ids": ["<from Step 8 — array; length 1 for single/group, length N for variety>"],
    "logo_source": "attached | none",
    "logo_placement": "opener | closer | both | null",
    "logo_media_id": "<from Step 6, or null>"
  },
  "image_refs": {
    "character_sheet_urls": ["<from Step 8 — array of N urls for variety; single-element array otherwise>"],
    "logo_url": "<from Step 6, or null>"
  }
})
```

CRITICAL — `character_sheet_urls[]` MUST be the full array. In variety mode the enhancer LLM needs to SEE every product to compose the 9-shot variety storyboard with each product getting ≥1 dedicated focus shot. Dropping any url leaves the enhancer blind to one product and it will be missing from the storyboard.

Returns `{"prompt": "<full gpt_image_2 prompt string>"}`. Submit the storyboard `generate_image` call.

**`medias[]` array shape per `multi_product_mode`:**

**Single / sequential-iteration / group mode** (1 character sheet → 1 chain-ref):

```json
"medias": [
  {"value": "<CHARACTER_SHEET_JOB_ID>", "role": "image"}
]
```

**Variety mode** (N character sheets → N chain-refs, one per product):

```json
"medias": [
  {"value": "<CHARACTER_SHEET_JOB_IDS[0]>", "role": "image"},
  {"value": "<CHARACTER_SHEET_JOB_IDS[1]>", "role": "image"}
  // ... continue for ALL N character sheet job ids
]
```

CRITICAL — `medias[]` MUST include ALL N character_sheet_job_ids in variety mode. The downstream `gpt_image_2` call uses these chain-refs to visually anchor each product on its assigned focus shot(s). Dropping any entry means that product's geometry is unanchored and will drift / morph in the rendered storyboard.

**Conditional logo entry — APPEND when `logo_source == "attached"`** (from Step 0b.2). Append AFTER all character sheet entries:

```json
"medias": [
  // ... character sheet chain-ref(s) above (1 entry for single/group/sequential-iteration; N entries for variety) ...
  {"value": "<LOGO_MEDIA_ID>", "role": "image"}
]
```

The logo entry carries the uploaded logo id as its `value` (uploaded asset, not a prior generation). The enhancer LLM sees the logo as `@ImageK+1` where K is the count of character sheets (so `@Image2` for single/group, `@ImageN+1` for variety). When `logo_source == "none"`, the logo entry is OMITTED.

```json
generate_image({
  "requests": [{
    "model": "gpt_image_2",
    "prompt": "<enhancer output>",
    "aspect_ratio": "3:2",
    "resolution": "2k",
    "params": {"quality": "high"},
    "medias": [ /* shape per multi_product_mode + optional logo entry per the rules above */ ]
  }]
})
```

CRITICAL — `gpt_image_2` medias format: use the flat `{value, role}` shape for character sheets. The `value`s are the Stage A `character_sheet_job_ids` directly and the backend infers the media type from each value — NO `upload` step. The logo entry carries the uploaded logo id as its `value` (uploaded via `upload`).

**Pre-flight checklist BEFORE every Stage B `generate_image` call (HARD INVARIANTS):**

```
[ ] medias array is non-empty
[ ] medias[0].value is a character sheet job_id (the first entry is always a character sheet chain-ref)
[ ] If multi_product_mode == "single" | "group" | "sequential-iteration": medias has exactly 1 character sheet entry (+ optional logo entry = 1 or 2 total)
[ ] If multi_product_mode == "variety": medias has EXACTLY product_count character sheet entries (+ optional logo entry = product_count or product_count+1 total)
[ ] character_sheet_job_ids[] length matches multi_product_mode (1 for single/group/sequential-iteration; product_count for variety)
[ ] character_sheet_urls[] passed to enhancer image_refs has SAME LENGTH as character_sheet_job_ids[] (no dropped entries — enhancer must see every product in variety mode)
[ ] If logo_source == "attached": the LAST medias entry has value == logo_media_id
[ ] If logo_source == "none": medias contains only character sheet entries (no logo entry)
[ ] If logo_source == "attached": enhancer inputs include logo_placement matching the Step 0b.2 user pick ("opener" | "closer" | "both")
[ ] multi_product_mode + product_count passed to enhancer matches the Step 0b.1 user pick
[ ] Enhancer prompt body contains explicit "BUILD FROM @Image1 character sheet as the product bible — preserve silhouette / proportions / material / key features across all 9 shots" (or, in variety mode, "BUILD FROM @Image1..@ImageN character sheets — each product preserved on its dedicated focus shot(s)")
[ ] Enhancer prompt body lists 9-shot 3×3 grid (NOT 6-panel 3×2 — that's Track A territory)
[ ] Enhancer prompt body specifies scale alternation rule: WIDE → MACRO → MEDIUM → SPECIAL → MEDIUM → MACRO → OVERHEAD → WIDE → MEDIUM endcard (or equivalent — never two consecutive shots same scale)
[ ] Enhancer prompt body uses sandwich anti-grid 4-layer pattern (opening clause + per-shot prefix + final shot lock + FINAL REMINDER) — NOT SP1-short one-liner (that's Track A)
[ ] reference_tier passed to enhancer matches Step 0c user pick
[ ] aspect_ratio passed and consistent with Step 3 answer
[ ] Variety mode: enhancer prompt body explicitly allocates each product to ≥1 focus shot across the 9 shots (no product missing)
[ ] Group mode: enhancer prompt body explicitly states all N products co-staged in EVERY shot (group composition holds throughout)
```

If ANY check fails → DO NOT call the tool. Fix the request and re-verify.

Poll job_status to terminal state. From the completed job record `(storyboard_job_id, storyboard_url)`. Pass both into Stage C.

### 11. Stage C — Seedance via enhancer

Call the clip enhancer. Pass `storyboard_url` AND ALL `character_sheet_urls[]` in `image_refs` so the enhancer LLM can cross-check identity continuity per product (storyboard tells WHAT happens per shot; character sheet(s) anchor WHO each product is). The **Seedance `medias[]` only carries the storyboard** (Track B doctrine forbids dual-ref to Seedance — it confuses the model; storyboard already visually encodes all products).

```json
enhancer({
  "flow": "productMD-clip",
  "inputs": {
    "reference_tier": "<same as Stage B>",
    "aspect_ratio": "16:9 | 9:16 | 1:1",
    "duration_seconds": "<same duration as Stage B>",
    "brand_name": "<verbatim from brief, or null>",
    "brand_tagline": "<verbatim from brief, or null>",
    "user_request": "<original brief verbatim>",
    "multi_product_mode": "single | sequential | variety | group",
    "product_count": <int — matches Stage B value>,
    "truth_contract": "<TikTok handoff truth_contract, or null>",
    "storyboard_job_id": "<from Step 10>",
    "character_sheet_job_ids": ["<from Step 8 — array; length 1 for single/group, length N for variety>"],
    "logo_source": "attached | none",
    "logo_placement": "opener | closer | both | null"
  },
  "image_refs": {
    "storyboard_url": "<from Step 10>",
    "character_sheet_urls": ["<from Step 8 — array of N urls for variety; single-element array otherwise>"]
  }
})
```

CRITICAL — `character_sheet_urls[]` in `image_refs` MUST contain ALL N urls in variety mode so the clip enhancer LLM can cross-check that every product's identity is preserved on its assigned focus shot(s) when writing the Seedance prompt. In group mode the single grouped sheet url is enough (it visually encodes all products). In single mode the single sheet url.

Returns `{"prompt": "<full Seedance prompt string, ≤4000 characters (target 3200-3800)>"}`.

### 12. Submit Seedance batch (one request by default)

```json
generate_video({
  "requests": [{
    "model": "seedance_2_5",
    "prompt": "<enhancer output>",
    "duration": "<same duration as Stage B/C>",
    "duration_policy": "<TikTok handoff duration_policy, otherwise omit>",
    "aspect_ratio": "<from Step 3>",
    "resolution": "1080p",
    "params": {"mode": "omni_reference", "generate_audio": true},
    "medias": [
      {"value": "<STORYBOARD_JOB_ID>", "role": "image"}
    ]
  }]
})
```

Repeat the request object inside `requests[]` exactly `variant_count` times
(default 1, maximum 6). Never pass an unsupported `count` field.

**Critical: `medias[]` carries ONLY the storyboard (single ref).** Track B validated failure mode — dual-ref (character sheet + storyboard simultaneously) confuses Seedance. Character sheet identity is already encoded visually in the storyboard. NO second `medias[]` entry for character_sheet here.

**Auto-retry on Seedance error.** If `seedance_2_5` returns an error response (non-success status, API failure, content moderation rejection, transient pipeline error) — agent MUST automatically retry ONCE with the same params before reporting failure to user. Retry only fires on ERROR response, not on a successful job creation that polls to a `failed` status.

### 13. Best-of-N selection (only when multiple requests were opted in)

When user requested variance hedge and Step 12 produced N variants, evaluate variants on these criteria, pick the winner:

- **Product geometry consistency** across all 9 shots — silhouette, proportions, key features preserved. Character sheet's primary job is to anchor this.
- **Signature beat execution quality** — does the special transition shot (panel 04) actually pull off the rock-wipe / dutch tilt / exploded view, or did Seedance flatten it to a plain cut?
- **Camera moves per shot reading distinctly** — each shot's named camera move (Bot&Dolly snap / motion-control dolly / lateral parallax / overhead boom) registers as visually different. No two shots feel mechanically identical.
- **Typography clean** — diegetic text readable, overlay text on shots 01/08/09 sharp, no gibberish on macro detail shots.
- **Background discipline** — pure void stays pure, light gray studio stays evenly lit, gradient stays controlled.

With the default single request, there is no selection step.

### 14. Poll, download, present

Poll every requested variant to completion. Download each to `output/clip_<variant>.mp4`; for one request use `output/clip_1.mp4`. For multiple requests, render all variants side-by-side.

### 15. Report

Show: variant path(s) + total duration + reference tier picked + character sheet thumbnail. Optional: highlights of which signature beat was used on shot 04. Hide: job_ids, intermediate steps.

## Hard rules — MDC8 / Track B-relevant only

These are the global invariants the orchestrator owns. Stage B and Stage C creative rules live inside the enhancers — DO NOT duplicate them here.

1. **Reference resolution (HR-0) — three input shapes.** Any reference URL or attachment in the brief (style ref, mood ref, brand ref — NOT the product photo itself, which has its own HARD GATE at Step 0b) resolves via one of three shapes: (a) file attachment → `upload(files=[<local_path>])` directly; (b) direct image URL (`.jpg / .png / .webp`, Pinterest CDN, `images.higgs.ai` proxy) → `curl -sL -o /tmp/<slug>.jpg "<URL>"` → `upload`; (c) page URL (Instagram / Behance / website / any HTML page) → no screenshot tool ships in this agent, so `ask_question` for an attached screenshot of the page, or a direct image URL instead. NEVER bake a raw URL into a text-only fallback — URLs always rejected by API.

2. **Product photo is the ONLY user-attached image required (HR-1).** Track B never auto-generates a product surrogate. NEVER fabricate the product. STOP & ASK if photo missing (Step 0b enforces this). The product photo is uploaded ONCE in Step 0b via `upload` — captured as `(product_photo_media_id, product_photo_url)` and used in Stage A `medias[]`. After Stage A, downstream stages chain via the flat `medias[].value` job_ids, NO more `upload` calls.

3. **HR-2 MIN-TEXT.** Any text rendered INSIDE the panel frame ≥ headline cap-height (`"cities"` baseline reference, ~10-12% panel height). Diegetic typography on product surface is the primary text source for Track B. Graphic overlay typography is STRICTLY limited to shots 01 (brand entry) / 08 (tagline) / 09 (endcard logo lock). All graphic overlay text = ALL WHITE only, ZERO color. Tracked monospace sub-labels below headlines = STRIPPED.

4. **HR-3 REALISM ALLOWED — Track B EXCEPTION.** Photoreal humans / documentary register / ARRI Alexa cinematography / 35mm film grain / 180° shutter motion blur / iPhone editorial / real-skin texture — ALL PERMITTED in product-reel. This is the ONLY mode with photoreal allowed (Track A modes — highMD/typographyMD/infographicMD/classicMD — ban photoreal per HR-3). Track B is product cinematography of the real object; photoreal register is the discipline.

5. **HR-9 palette discipline.** 2-3 color palette locked across all 9 shots. Three palette patterns: Monochrome (luxury default — black + cool gray + white, zero color), Monochrome + neon accent (sport / tech — black + white + ONE neon on key feature only), Editorial gray scale (lifestyle / fashion — off-white + cool gray + black + white). Multiple color introductions mid-spec / color drift between shots / generic "colorful" without specific palette = BANNED.

6. **HR-10 tail freeze.** Final composition holds pixel-identical for the final 1.3/15 of selected duration. NO fade-to-black, darkening, new motion, or transitions.

7. **HR-12 image attachment routing.** If chat has image attachments AND brief mentions them — NEVER submit a text-only prompt with empty `medias`. For product-reel: the product photo is always the foundation in Stage A; downstream stages chain via job_id. NO silent vision-describe fallback.

8. **HR-13 operational asks fire via tool.** Every operational question to the user (aspect ratio / product photo gate / reference tier ask / character sheet confirm / variance hedge opt-in) goes through `ask_question`. NEVER ask in plain prose. The frontend renders option cards.

## Track B specific invariants (over and above the generic HRs)

- **9-shot 3×3 storyboard format** — NOT 6-panel 3×2 (that's Track A territory). 9 thumbnails arranged in a 3×3 grid is the validated optimum per Track B doctrine.
- **Sandwich anti-grid 4-layer pattern** — opening clause + per-shot prefix + final shot lock + FINAL REMINDER. NOT SP1-short one-liner (that's Track A). The 9-shot format carries Continuity Law clauses across many beats with coherent product geometry — the redundancy is required, not counterproductive.
- **Seedance prompt ≤4000 characters (target 3200-3800)** — Track B is denser than Track A because 9 shots require Subject Lock + Palette Lock + Continuity Law clauses plus per-beat lighting/material specs, but it must fit the engine cap.
- **Diegetic typography primary; graphic overlay strictly 3 shots (01/08/09).** Shots 02-07 = pure product cinematography, ZERO graphic text. Macro detail / hero / overhead / signature beat shots have NO overlay text. Only diegetic-on-product if applicable.
- **SFX-only audio mandatory.** NO music, NO voiceover in Seedance prompt. Music goes to CapCut post on unified timeline (in-Seedance music can mismatch across multiple request variants).
- **Photoreal CGI mandate** — ARRI Alexa / Cinema 4D Octane / ProRes 4K production value baked into every Seedance prompt. NOT stylized, NOT illustrated, NOT painterly.
- **One request object by default; repeated request objects are opt-in.**
- **Dual-ref forbidden in Seedance call** — single `medias[]` entry (storyboard only). Character sheet identity already encoded visually in storyboard.

## `ask_question` — what to ask, what to NEVER ask

product-reel pins every workflow parameter (model per step, sheet aspect = 3:2 always, one Seedance request by default, audio = SFX-only mandatory, `medias` shape, storyboard 9-shot 3×3 format, photoreal allowed, sandwich anti-grid).

### NEVER ask via `ask_question`

- **Sheet aspect** — pinned `3:2` for character sheet AND 9-shot storyboard sheet. Never offer forks.
- **Resolution / quality** — pinned: `2k` for storyboards, `1080p` for Seedance.
- **Model selection** — pinned: `gpt_image_2` for character sheet + storyboard, `seedance_2_5` for clip.
- **Audio generation** — pinned: native audio (`params.generate_audio: true`), SFX-only mandatory (NO music, NO VO).
- **variant batch** — one request by default; repeat request objects only on explicit opt-in.
- **Storyboard format** — pinned 9-shot 3×3 grid. NEVER offer 6-panel 3×2 (that's Track A).
- **Sandwich anti-grid layer count** — pinned 4-layer. NEVER offer SP1-short (that's Track A).
- **Photoreal mode** — pinned allowed (Track B is the photoreal exception). NEVER offer stylized fork.
- **Stage A vs Stage B vs Stage C** — pinned sequence; never offer "skip storyboard go straight to Seedance" forks.

### DO ask via `ask_question` (creative / operational gaps)

Bundle into ONE call when more than one is missing — never one question per gap.

| Question | Ask when |
|---|---|
| **Aspect ratio** | Brief did not specify (`16:9 horizontal` / `9:16 vertical` / `1:1 square`). |
| **Product photo gate (Step 0b)** | No product photo attached. STOP & ASK. |
| **Reference tier (Step 0c)** | Brief vocabulary does not unambiguously imply Tom Ford / BMW / ASICS / Buck / Pentagram tier. |
| **Character sheet confirm (Stage A.2)** | After every Stage A render. ALWAYS fires. |
| **Variance hedge opt-in** | Brief mentions "best-of-N" / "premium variants" / "× N takes" — confirm repeated request objects. |
| **Variant selection (Step 14)** | Only when multiple request objects were opted in and returned. |

If the brief already contains an answer — do not re-ask. Proceed silently and document the choice.

## Critical rules

- Product identity locked via the user's product photo (Step 0b upload). Character sheet (Stage A output) is the production bible for downstream consistency. No mid-pipeline product-swap.
- Stage A character sheet prompt is FIXED-ENGLISH regardless of user's brief language. The only variables are `<TIER_BACKGROUND>` and `<TIER_LIGHTING>` placeholders (resolved from Step 0c reference tier).
- Stage A → Stage B → Stage C is STRICTLY SEQUENTIAL. Stage C uses one batch call; variants are repeated request objects.
- The agent passes structured inputs to `enhancer` — never prose. All Stage B / Stage C creative rules belong inside the enhancer system prompts.
- For every image generated, capture BOTH `(job_id, result.url)` from the completed `generate_image` job. `job_id` feeds the next `generate_image.medias[]` as chain-reference (carried in the flat `value`); `result.url` feeds the next `enhancer.image_refs`. Dropping the url leaves the enhancer blind for the next call.
- Stage B / Stage C `medias` format uses the flat v2 shape: `{"value":"<job_id>","role":"image"}` — the backend infers the media type from the value.
- Stage C Seedance `medias[]` carries ONLY the storyboard (single ref). Dual-ref (character sheet + storyboard simultaneously) is a validated failure mode — confuses Seedance.
- Photoreal humans are ALLOWED in productMD (Track B exception — HR-3 does NOT apply). Photoreal model holding / wearing / using the product, photoreal environment around product, ARRI Alexa register — ALL permitted. This is the ONLY mode with photoreal.
- Diegetic typography primary. Graphic overlay typography STRICTLY limited to shots 01 / 08 / 09 — ALL WHITE only, ZERO color.
- 4 of 9 shots = SPECIAL beat slot (shot 04) carries one signature beat: exploded view / bullet-time / rock-wipe / dutch tilt / 360° spin / mandala / impact drop.

## NOT for this workflow

- **Classic motion design (MDCM)** — generic 2026 motion design ad for product/service WITHOUT specific aesthetic direction → `motion-design-reel`. motion-design-reel auto-generates 4-up moodboard, productMD requires the actual product photo.
- **High Motion / kinetic brand reels** with explicit `kinetic` / `peak-action` / `hyperkinetic` / `smash` / `sport` triggers (but NOT product hero focus — abstract subject) → `kinetic-reel`. product-reel's hero is the product geometry, not abstract kinetic energy.
- **Typography reels** where TYPE is the visual subject (letterforms morphing / kinetic typography hero) → `typography-reel`.
- **Infographic reels** with data / charts / stats viz → `infographic-reel`.
- **UGC talking-head with product** → out of scope for motion design skills. Use a UGC-specific skill.
- **Ad with hero person on camera** (model wears / actor uses / talent demonstrates / portrait of someone holding the product) → `tv-ad-flow`. tv-ad-flow has the full character + dialogue / VO + dramaturgy pipeline for human-centric commercials. product-reel is pure product cinematography; if the human is in frame, route out via Step 0z.
- **Cinematic action / scripted long-form (>15s, non-loopable)** → `short-film`.
- **Multi-chapter brand reels >15s** — product-reel ships single-clip Track B. Multi-chapter assembly is out of scope for v1; user must request manually via repeated Stage B+C calls per chapter.
- **Product mockup without actual photo** — product-reel REQUIRES the user's real product photo. If they want a generic product-like subject (e.g. "make a sneaker reel" without a specific sneaker) → route to `kinetic-reel` with foundation generator.
