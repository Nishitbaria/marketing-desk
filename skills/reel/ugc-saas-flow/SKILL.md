---
name: ugc-saas-flow
description: |
  A UGC-style video for any WEBSITE / web app / service / store / product page at a URL — the HERO is what's ON SCREEN: the site/page shown as REAL captured screenshots (product listing, reviews, specs, pricing) while a creator talks to camera (hook → it solves my problem → result). Screenshots pop in as overlays (never a screen recording, never AI-generated UI). Works for a PHYSICAL product too when it has a store/product URL — shown via its PAGE, held in hand only in the closer, never through the body.
  Triggers: "SaaS UGC" / "UGC SaaS" / "saas ugc ad", "UGC ad from this link / URL", "video about my site / app / store / product page", "site tour". Saying "SaaS UGC" / "UGC SaaS" or naming this flow ALWAYS selects it — even for a physical product with a store link; ANY site / store / product URL routes here.
  NOT for: a product shown ONLY in-hand with NO URL (an uploaded product photo, "review / unbox this object") → ugc-flow; building or editing a website (out of scope); AI-generating a UI.
---
# ugc-saas-flow

One pipeline for UGC-style videos about **any website / web app / online service / store reachable
at a URL** — SaaS, marketplace, e-commerce, portfolio, content site. The **hero is the SITE itself
shown on screen** (a site tour / "how I use this site"), NOT a physical product. Even for an
e-commerce store, this flow shows the SITE and the shopping experience — the physical goods in the
creator's hands belong to `ugc-flow`, not here. The site is shown as **real captured screenshots**
(headless-browser stills of the useful sections), never as AI-generated UI and never as a screen
recording the user has to make.

The video is a **talking-head creator** on camera the **whole time** (generated like `ugc-flow`,
product-free), framed 2/3 with the head centered in the frame, talking with a **US accent** at a natural, lively UGC pace
(lively but never crammed).
The site appears as **useful screenshots laid OVER the face as large insets** (~0.78·W wide, height
capped ~0.60·H) that **pop in for ~1.2–1.5s each, then clear** while the creator narrates them — the
product, reviews, specs, pricing. The first ~1-2s is a hard hook on the open face; the closer ends on
the creator doing an **action with the product**. The voice is the continuous spine under
everything, with a **hook plate (top, during the hook)** then **subtitles along the bottom** burned in
by default (via the `montage` skill's §3, exactly like `ugc-flow`).

## What this flow does NOT do (hard boundaries)

- **Never AI-generates the app UI.** Video models render UI text as gibberish. The screen is
  always real pixels captured from the live site. If the site cannot be captured (see the
  availability gate) the flow asks the user for real screenshots — and if none come, delivers a
  talking-head-only video (no insets). It NEVER invents a UI.
- **Never animates a screenshot into video (no image-to-video on the UI).** The site shows as
  **static real screenshots overlaid as cards** — no scrolling, no pans, no image-to-video. Real
  captured pixels only.
- **Never forces the user to record their screen.** The browser toolkit captures the site.

## Mandatory Reference Resolution

Load each reference with `skill_view(name, file_path)`. The **talking-head spine** reuses the
existing product-free UGC references read-only (do NOT copy or fork them); the **SaaS-specific**
logic lives in this skill's own `references/`.

| Step | Skill | File path | Role |
|---|---|---|---|
| Capture the live website | `ugc-saas-flow` | `references/website-capture.md` | Drive the headless browser, capture the useful sections |
| Draft the monologue + card order | `ugc-saas-flow` | `references/saas-monologue.md` | SaaS script model — hook, natural pace, section order + words-per-section, closer action |
| Build the overlay composite | `ugc-saas-flow` | `references/screen-broll-and-composite.md` | creator base + useful screenshots as large insets over the face; captions bottom |
| Burn subtitles (default) | `montage` | `§3 Burned captions` (`skill_view("montage", "SKILL.md")`) | bottom captions (raw word-level Whisper, `--size 50 --no-caps`) + optional top hook plate — the SAME path as `ugc-flow` |
| Map creator inputs + carry framing/voice | `ugc-saas-flow` | `references/saas-ugc-character.md` | `ugc-character` enhancer input mapping (tier / category / self-film setting) + SaaS framing (2/3, head centered in frame) / US accent / audio carried into the Seedance prompt |
| Write the Seedance clip prompt | `ugc-saas-flow` | `references/saas-clip-prompt.md` | ONE continuous talking-head shot, no board/cuts/Angle Lock; product-in-closer + no-rendered-site bans |

The clip prompt uses this skill's own `references/saas-clip-prompt.md` — ONE continuous talking-head
shot, no board, no Angle Lock. The product is product-free in the body and only appears in the closer
(real image as media); the site is never rendered inside a clip. **This flow generates NO
storyboards** — Seedance is seeded with the creator image directly (see Architecture), so there is no
`gpt_image_2` board step and `ugc-boards.md` is NOT used. Do NOT load `product-analyzer` and do NOT
load any `ugc-product-*` / `ugc-unboxing-*` / `ugc-try-on-*` / `ugc-tutorial-*` / `ugc-clip-prompt`
reference.

## Architecture

A creator base with screenshots overlaid on top:

1. **Talking-head spine (the base picture, always on camera)** — creator to camera for the whole
   video, generated via the `ugc-character` enhancer (like `ugc-flow`; product-free, identity + base
   anti-slop from the enhancer), then **de-slopped by a Seedream i2i pass on the seed** (Step 3.5) —
   **no storyboard**, the (de-slopped) creator image seeds Seedance directly — carrying the **whole
   monologue's audio**. Framed 2/3, head centered in the frame, lively US-accent delivery (enforced in the Seedance
   prompt). Continuous creator voice + face across the entire video.
2. **Overlay cards** — real screenshots of the **useful** sections (product, reviews, specs,
   pricing) captured from the URL, shown as **small static cards overlaid on top** of the creator.

Composite (see `screen-broll-and-composite.md`): the creator clips concat into one continuous base;
each screenshot is a **large inset laid OVER the face**, anchored to the section the creator is
narrating (variant B), each a **~1.2–1.5s pop with a ~0.3–0.5s clean-face gap** between (interrupted,
not continuous). The **first ~1–2s (hook)** and the **closer (product action)** carry NO inset — the
face owns them. Insets are **~0.78·W wide, centred, with a HARD height ceiling of ~0.60·H** (tall
cards shrink to fit; sizes normalise across cards) and sit **centred slightly up** so their bottom
never enters the **bottom ~15% caption band**. The inset floats over the live video (creator visible
around the edges) — **no blur, no backing**. Captions run along the bottom. The voice plays
continuously; audio is never re-encoded (the composite encodes the video once). NO full-screen site,
NO scrolling.

## Duration → N clips → per-clip durations

Same table as `ugc-flow` — the talking-head spine is generated identically.

| Total D | N | Clip durations |
|---|---|---|
| 4-15 | 1 | D |
| 16-19 | 2 | balance to ≥4s each (D=18 → 14+4) |
| 20-30 | 2 | 15, D-15 |
| 31-45 | 3 | 15, 15, D-30 |
| 46-60 | 4 | 15, 15, 15, D-45 |
| >60 | ceil(D/15) | 15 each, last = remainder ≥4s |

## Timeline & overlay model

The arc is **hook → the site solves it → result + action**. The creator is on camera the WHOLE
video (never a full-screen site); the site shows as **useful screenshot cards overlaid on top**.
Model the composite as a timeline over the continuous creator audio:

- **Hook — first ~1–2s (`t_hook = min(2.0, t(hook_words))`), no inset.** The hardest, most expressive
  line on the open face, shown as a **top plate** (Metropolis); make-or-break. Bottom captions start
  when the plate leaves (Step 7).
- **Body — screenshot insets (~70%).** As the creator narrates the useful sections in order (product
  → features → reviews → pricing), **each captured still pops in as a large inset OVER the face for
  ~1.2–1.5s** (aim for many — ~6-10), then a clean-face beat, then the next — **interrupted, not a
  continuous strip**. The **first inset is the hero** (logo/navbar, anchored to the beat that names
  the site); narration order = inset order; more insets from more captures + beats.
- **Closer — last ~15%, no inset.** Result / metric + CTA **while the creator does an action with
  the product** (in-hand for a physical product; on the phone for SaaS/services).

### Card timing = variant B anchor (no ASR)

Each card is **anchored** at the word-time its section starts being narrated, mapped over the
continuous voice: `t(cum) = T × cum_words / total_words`. We author the script and know
words-per-section, so **no transcription is needed**. Each inset then shows for **~1.2–1.5s** with a
**~0.3–0.5s clean-face gap** before the next — interrupted, not continuous. **Each captured still
is its own card** (~6-10), so a section with several stills gives several successive cards. To show
more of the site, capture more stills + narrate more beats — the per-card time and gap stay fixed.
`screen-broll-and-composite.md` has the exact overlay recipe (N==1 and N>=2 are identical — the
clips concat into one base first).

The creator's ORIGINAL audio plays continuously and is **copied, never re-encoded**; the voice never
drops. Every beat's audio comes from a generated talking-head clip, so there is exactly ONE voice
across the whole video.

## Pipeline

### 1. Parse request

Extract: **website URL** (required — the site is the hero), duration, creator gender, any creator
overrides (location, look, mood), and the **`caption_mode`** (`Both` default / `Subtitles` / `Hook` —
see the ask table; captions are ON unless the brief says "no captions"). Compute N + per-clip
durations + arc role per clip from the tables above.

**Routing gate (do this first).** This flow shows what's **ON SCREEN** (the site / store / product
page as screenshots). Decide by the SITE, **not** by whether the product is physical:
- **Stay here (ugc-saas-flow)** if the user says **"SaaS UGC" / names this flow** (a hard override),
  OR gives **any site / store / product-page URL** — even for a physical product. The product is
  shown via its PAGE (screenshots), held in hand only in the closer, never through the body.
- **Hand off to `ugc-flow`** (`/ ugc-product-flow` / `ugc-unboxing-flow` / `ugc-try-on-flow`) ONLY
  when there is **NO URL / no site to show** and the ask is a pure product-in-hand video (an uploaded
  product photo, "review / unbox this object" as the hero) — then stop.

An explicit "SaaS UGC" request ALWAYS wins over the physical-vs-not question. A store/product URL
(e.g. an iHerb product page) belongs HERE — the creator talks about the product using its page, and
the physical item appears only in the closer.

**Classify the site (for tone/look only, no hard taxonomy):** rough `type` (`saas` | `ecommerce` |
`marketplace` | `service` | `portfolio` | `content` | …), `audience` (`b2b` | `prosumer` |
`consumer`), `surface` (`web` | `mobile-app` | `dashboard`). These steer the creator's look and the
monologue tone; decided once here.

### 1.1 Persona source — detect `character_provided`

Identical to `ugc-flow`: if the user attached a person photo, that photo IS the creator — upload
it via `upload`, capture `(character_media_id, character_url)`, and SKIP Step 3. This
is a hard gate, not a question. Otherwise generate the creator in Step 3.

### 2. Capture the website + build a section map (mandatory)

Follow `skill_view("ugc-saas-flow", "references/website-capture.md")`. Primary path: call
`website_screenshot(url, mobile: true, full_page: true)` — a real MOBILE full-page capture
(vertical, readable text) with cookie/overlay dismiss built in — and download the returned
`screenshot_url` to `output/site_full.png`.

Then build a **section map**: VIEW `site_full.png` (and optionally `web_extract` the URL for the
heading order) and record the sections top→bottom, each with an approximate vertical band, e.g.:

```
[ {label:"hero", y:0.00-0.18}, {label:"features", y:0.18-0.45},
  {label:"dashboard", y:0.45-0.62}, {label:"reviews", y:0.62-0.80}, {label:"pricing", y:0.80-1.00} ]
```

**Then capture the USEFUL sections as their own stills — this is the important part.** Every card in
the video comes from these, so capture the genuinely valuable sections: the **product / hero, real
reviews, specs / features, pricing**. Content behind a tab/accordion often isn't rendered in the
single full-page shot, so make a SECOND call requesting those sections by name — the tool clicks each
and takes a dedicated viewport shot:

```
website_screenshot(url, mobile: true, sections: ["Reviews", "Pricing", "Specifications", ...])
```

**Capture MANY useful stills (target ~6-10 for a 30-45s video) — the number of cards on screen
equals the number of distinct useful stills you capture.** Be GRANULAR: don't stop at 3 broad
sections — break them into individual **feature screens** (dashboard, search, editor…), a couple of
**review** shots, **pricing** + a specific **plan**, **specs**, distinct **product views**. For each
returned `sections[i]`, download its `url` to `output/section_<label>.png` and mark that label in the
section map. The composite (Step 6) overlays each still as its own **card**. Sections the tool
couldn't open are skipped. Skip low-value bands (nav, footer, logo strips) — they never become a
card. This is the lever for "more screenshots": capture generously.

The section map drives BOTH the monologue order (Step 4) and the card order (Step 6). If
`website_screenshot` is unavailable or errors, the reference gives the fallback (browser toolkit,
then ask the user for screenshots). **Never fabricate a UI to proceed.**

### 3. Generate the creator — only when `character_provided == false`

Generated via the `ugc-character` enhancer, **EXACTLY as `ugc-flow` Step 2** — a product-free CLEAN
person (the site is composited later as overlays, never baked into the character image; identity +
anti-slop are owned by the enhancer server-side, so `soul-v2-ugc-character.md` is NOT loaded here).
First read `skill_view("ugc-saas-flow", "references/saas-ugc-character.md")` for the SaaS **input
mapping** + the framing / setting / accent / audio notes to carry into the Step-5 Seedance prompt.

Call the character enhancer — **text-only, no `image_refs`**; the wrapper auto-injects `variety_rolls`
(never pass them):

```json
enhancer({
  "flow": "ugc-character",
  "inputs": {
    "tier": "<premium (default) | drugstore (mass-market store) — derived from `audience`>",
    "category": "<site `type` mapped: saas / service / portfolio / content → `tech`; ecommerce / marketplace → the physical product's real category>",
    "gender": "<woman | man>",
    "user_request": "<original brief verbatim — tone signals + backup parsing>",
    "user_overrides": {
      "location": "<the locked self-film scene — phone propped up, real home (couch / desk / bed), natural light; see saas-ugc-character.md §2>",
      "...": "<any look overrides the user specified>"
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

Poll to terminal; capture `(character_media_id, character_url)` = `(job_id, result.url)`. No download,
no re-upload — Soul outputs chain forward by job-id. The enhancer's Soul image is a **3:4 identity
seed** (a tight head-and-shoulders selfie is fine); the **9:16 framing (creator ~2/3, head centered in the frame), US accent, lively varied pace, and phone-mic audio are enforced in the Step-5 Seedance
prompt** (`saas-clip-prompt.md` + `saas-ugc-character.md` §1/§3/§4/§5) so the moving clip matches —
carry them there.

### 3.5 Anti-slop pass (Seedream 5 Pro i2i) — MANDATORY, only when `character_provided == false`

Soul 2.0 holds identity but can render sloppy skin (waxy / HDR / over-smoothed). De-slop the **creator
seed** with a `seedream_v5_pro` instruction-edit before it seeds Seedance — the same idea as `ugc-flow`
Step 5.5, but applied to the single 3:4 portrait (there is no board here). Skip this entirely when
`character_provided == true` — a user's own photo is used as-is, never edited.

Two tool calls, in this order:

**a. Upload the creator image to a `media_input`** (Seedream's `image_references` role rejects the
Soul `job_id` chain-ref — needs a real upload id):
```json
upload({"files": ["<character_url>"]})
```
Capture `uploads[0].id` as `creator_upload_id`.

**b. Run the de-slop i2i** (aspect `3:4`, role `image_references`):
```json
generate_image({
  "requests": [{
    "model": "seedream_v5_pro",
    "prompt": "<ANTI-SLOP PROMPT below, verbatim>",
    "aspect_ratio": "3:4",
    "resolution": "2k",
    "medias": [{"value": "<creator_upload_id>", "role": "image_references"}]
  }]
})
```

**ANTI-SLOP PROMPT** (single-portrait, fixed):

> KEEP EXACTLY the framing, composition, pose, subject and identity of this vertical portrait — no
> reframe, no zoom, no crop, no change to the person's face / hair / body / clothing. CHANGE ONLY
> micro-realism: true-to-life pore-level skin with natural texture and fine vellus hair, real material
> detail, even natural daytime light with gentle highlight roll-off and faint true sensor noise, a flat
> authentic iPhone selfie, deep focus. PRESERVE the face's exact shape / width / proportions 1:1 — do
> NOT squeeze / narrow / slim / stretch the face. AVOID AI-slop: waxy plastic skin, airbrushed poreless
> skin, beauty-filter smoothing, over-saturation, HDR glow / bloom / halos, oversharpening, teal-orange
> grade, shallow depth of field, bokeh, cinematic / DSLR look. No added text, no watermark.

Poll to terminal; capture `(character_media_id, character_url)` from THIS output and **OVERWRITE** the
raw-Soul refs — the de-slopped image is the locked identity seed for **every** Seedance clip (identity
lock is still ABSOLUTE; lock it here, after the pass, and never regenerate). **Fallback:** on a
moderation block, retry once on `seedream_v5_lite` (same call shape); if it still fails, fall back to
the raw Soul creator — NEVER block the pipeline on the anti-slop step.

### 4. Draft the monologue + card order

Follow `skill_view("ugc-saas-flow", "references/saas-monologue.md")`. **Write in English even if the
brief is in another language** (Seedance mangles non-English speech). Write on the **hook → the site
solves it → result + action** arc: **hook** (ALWAYS a bold product/result claim — "this site changed
my life", "I made $5000 with this site" — ~first 1–2s) → **body that names the useful sections in
order** (product → features → reviews → pricing, from the Step-2 map) → **closer with a product
action** (in-hand for a physical product; on the phone for SaaS/services). Write at a **natural,
lively pace (~2.4–2.7 words/sec — energetic but never crammed or rushed)** and **vary the speed
within the take** (a touch quicker on connective lines, slow to land the number / price / CTA; a
constant even speed reads robotic). Delivery is **natural, lively spoken — like a creator talking to a
friend, NOT a narrator / voiceover** (spoken-texture rules in the ref). Tag **words-per-section** — the
composite anchors each card at its narrated word-time (variant B). Density (natural pace): ≤10s ~22-26
words, 11-12s ~28-33, 13-15s ~35-40 (**hard ceiling ~40 words / 15s — more and Seedance crams and talks
too fast; aim for the middle of the range**); sum across clips. Keep the **hook line** (the first spoken line) handy
— Step 7 reuses it verbatim for the top hook plate.

### 5. Generate the talking-head spine (product-free, no storyboard)

**No storyboards.** Seedance is seeded with the **creator image directly** — there is no
`gpt_image_2` board generation. This saves ~3-4 min and two image generations per run. Each clip is
one continuous talking-head shot (the creator speaking that beat's segment to camera), not a
multi-slot board strip.

For each clip K:

- Clip prompt: `skill_view("ugc-saas-flow", "references/saas-clip-prompt.md")` — the SaaS
  talking-head reference (**ONE continuous shot, no board, no intra-clip cut, no Angle Lock**). Feed
  ONLY the creator reference + the beat's monologue segment. It bakes in framing 2/3 (head centered in frame), US
  accent (no British), **natural lively ~2.4–2.7 words/sec with varied rhythm (never crammed)**, **phone-mic audio + ambient
  matching the scene, no music**, the anti-slop + phrase-splitting rules, and the two HARD bans
  (**product only in the closer**; **never render a site / UI**). Issue the N clip-prompt LLM calls
  in one batch.
- **Product rule + the closer action.** Body clips are **product-free** — the VISUAL never mentions
  the product, no object in hands. The **closer** ends on an action with the product: **physical
  product** → creator may **pick it up / hold it up** (allowed here only); **SaaS / service** →
  creator **acts on the phone** but the **screen is turned away / blank** (no rendered UI). A phone /
  device in hand is fine; a physical product in hand is banned **except** in the physical closer.
- **Physical-product closer → seed the REAL product image** (so Seedance renders the actual product,
  not an invented one). The image must come from **the given product page itself** (`web_extract` /
  firecrawl on that URL, or a user-provided screenshot) — **never web-search / hunt for a product
  photo elsewhere.** Then either **pass the URL directly as the closer's second `media`**
  (`medias[].value = <image URL>` — the tool downloads + uploads it) **OR** `upload(files=
  [<url>])` once and reuse the returned id. **No crop, no background removal.** If the page has no
  usable product image, drop to a generic "go check it out" gesture (no object) — do NOT go looking
  for one. SaaS/service closers take no product media.
- **Identity lock is ABSOLUTE — never regenerate the creator.** `character_media_id` is fixed for
  ALL clips, **including the closer**. If the closer job returns `status: nsfw`, **retry the closer
  only**, WITHOUT the product media and with a neutral gesture ("go check it out", no object near the
  face), **same `character_media_id`**. Never regenerate the character under any circumstance — one
  creator across every clip.
- Video: `generate_video` model `seedance_2_0`, `aspect_ratio` `9:16`, `resolution`
  `1080p`, `medias` = `[character]` only for every clip **except** the physical-product closer (which
  adds the product image as above). Issue the N video jobs in parallel, exactly as `ugc-flow`.

**Pre-submit checklist (MANDATORY — reject & rewrite before generating).** Verify EACH clip prompt;
**grep it** and rewrite on any hit:
- **Single continuous shot:** grep for `Hard cut`, `Cut 1`, `Cut 2`, `slot`, `board` → any hit ⇒
  rewrite to one continuous shot (cuts happen in the composite, not inside a clip).
- **Product only in the closer:** grep a **body** clip's VISUAL for the product name → hit ⇒ remove
  (Bug D — mentioning the product with no input image makes Seedance invent a fake one).
- **Never a rendered site:** grep ANY clip for `website` / `UI` / `screen` / `browser` in the visual
  → hit ⇒ remove / convert to the Bug-E ban (the site is real overlays in the composite only).
- **Closer action present:** last clip renders the product action; physical closer passes the real
  product image as the second media (URL or uploaded id).
- **Framing / delivery / audio:** 2/3 (head centered in frame), US accent (no British), natural ~2.4–2.7 wps varied (never crammed),
  phone-mic + scene ambient, no music — present in every clip.
- Fail any check → rewrite before submitting to Seedance.

Identity holds across clips via the **same `character_media_id`** passed to every clip. Capture
every `(media_id, url)` by job-id chain-ref (no download / re-upload). Generate a talking-head clip
for **every** beat — including the **body** beats — because their audio is the voice played under
the overlay cards, and the creator stays on camera throughout.

**Frozen-frame QA** (per `ugc-flow`) on every on-camera clip before compositing: one creator, ≤2
hands, face matches reference, no baked text, lips clean on mid-word frames.

### 6. Build the overlay composite (MANDATORY)

Follow `skill_view("ugc-saas-flow", "references/screen-broll-and-composite.md")`:

**Degrade case (no site cards — capture failed and the user sent no screenshots):** skip the overlay
entirely. Concat the talking-head clips into `output/final.mp4` (stream-copy, audio untouched) and go
straight to Step 7 — the video is talking-head-only, no insets. Otherwise build the full overlay:

1. Download the talking-head clips to `output/clip_<K>.mp4` (numeric suffix = clip index) and concat
   them into one continuous base `output/creator_full.mp4` (same Seedance params → stream-copy, audio
   untouched). Probe its duration `T` and fps.
2. Prep the **card content images** built **by TYPE** — no white pad, no backing (they float over the
   live creator; see the reference). First find each element's band with `image_analyze` (logo/navbar,
   product, name+price, reviews, warranty → height fractions, per-site). Then: **hero card** = stitch
   the meaningful top bands (logo + product + price, DROP empty gaps); **text/product cards** = use
   the section still directly. Every card must carry a **site marker** (logo / navbar / price+CTA /
   reviews UI). Aim for ~6-10 cards; skip filler.
3. Anchor each card by word position over the continuous voice (variant B):
   `t(cum) = T × cum_words / total_words`. The **first ~1–2s (hook)** and the **closer (product
   action)** get NO inset; each body inset shows for **~1.2–1.5s** with a **~0.3–0.5s clean-face gap**
   before the next (interrupted, not continuous).
4. Composite to `output/final.mp4`: overlay each card as a **large inset OVER the face** — fit it
   inside a box **~0.78·W wide × ≤0.60·H tall** (contain: enforces the height ceiling + normalises
   sizes), **centred horizontally, slightly up** (`(W-w)/2 : (H-h)/2-0.04·H`), time-gated with
   `enable='between(t,s_k,e_k)'`, over the live video (no blur/backing). Its bottom must stay clear of
   the **bottom ~15% caption band**. **Audio is copied** (never re-encoded); the video is encoded
   exactly once (the overlay pass needs it). N==1 and N>=2 are identical (the clips are already
   concatenated). The pipeline is NOT complete until `output/final.mp4` exists.

### 7. Burn subtitles (MANDATORY, default ON)

Captions run through the **`montage` skill's §3 Burned captions** — the SAME canonical path as
`ugc-flow` (Step 8.5), on **raw word-level Whisper** (no script alignment). Captions are **ON by
default**; the `caption_mode` from Step 1 (`Both` default / `Subtitles` / `Hook`) picks the layers.
Only an explicit "no captions" request skips the burn (then deliver `output/final.mp4`). Timing comes
from a word-level Whisper transcript of the FINAL stitched audio (montage §3 Steps 1–5:
`audio_to_captions.py` → `make_captions.py`) — never planned-beat timings; silence carries no caption.

- **Subtitles** (or **Both**): follow montage §3 Steps 1–5 — extract `output/final_audio.wav`,
  transcribe word-level, render `output/captions.ass` with **`--size 50 --no-caps`** (bottom
  safe-zone, Metropolis, sentence case, white + black outline, auto-fit — all baked into
  `make_captions.py`), burn. If transcription finds no speech → burn NO subtitles (deliver
  `output/final.mp4`); never guess timing.
- **Hook** (or **Both**): montage §3's optional **top HOOK layer** — the authored hook line (Step 4)
  as a ≤6-word top headline (`output/hook.ass`, Metropolis default, CAPS, top ~0.10·H), burned as the
  second layer. Text only — no emoji (libass renders none).
- Burn only the chosen layers in ONE pass (audio copied; video encoded once); resolve `$FD` to
  montage's `scripts/fonts` via `find "$HOME/.hermes/skills" ...` (`$HOME`, not `~`):
  - **Both** — `-vf "ass=output/captions.ass:fontsdir=$FD,ass=output/hook.ass:fontsdir=$FD"`
  - **Subtitles** — `-vf "ass=output/captions.ass:fontsdir=$FD"`
  - **Hook** — `-vf "ass=output/hook.ass:fontsdir=$FD"`

  e.g. `ffmpeg -i output/final.mp4 -vf "<chosen>" -c:a copy output/final_captioned.mp4`.

The bottom band is the caption safe-zone the composite reserves (Step 6 keeps the inset out of it).
The pipeline is NOT complete until **`output/final_captioned.mp4`** exists — that is the deliverable.

### 8. Deliver + report + optional TikTok publish

Only after `output/final_captioned.mp4` exists (fallback `output/final.mp4` if captions were skipped):

1. **Deliver the video (REQUIRED — the composite is a local sandbox file, not hosted).** Upload it:
   `upload(files=["output/final_captioned.mp4"])` (or `output/final.mp4`) and capture the
   hosted `url` — THAT hosted video is what the user receives / plays. A bare sandbox path does NOT
   reach the user; you must upload.
2. **Report:** show the delivered video (the hosted `url` from step 1) + total duration; if captions
   were skipped (no speech found or an explicit "no captions"), say so. Hide job_ids and intermediate
   steps.

Then offer publishing with **ONE** `ask_question` (header "Publish to TikTok?"): **"Yes,
publish"** / **"No, just the file"**. On **"Yes"**:

1. **Ensure TikTok is connected** — `custom_mcp(action: "list_servers")`. If TikTok is not connected:
   `custom_mcp(action: "connect", provider_slug: "tiktok")` → return the `authorize_url` as a
   **clickable link** and wait for the user to finish the OAuth before continuing.
2. **Build the form** — `tiktok_publish_form(...)` (caption/title, privacy, the video). It is
   approval-gated: the user submits the form in the dashboard; on submit it returns `publish_tiktok_args`.
3. **Publish** — only AFTER an explicit form submit: call `publish_tiktok` (via
   `custom_mcp(action: "call", server: "tiktok", ...)`) with the form's `publish_tiktok_args`.
4. **Never publish without an explicit form submit.** On "No, just the file", stop — deliver the file only.

## `ask_question` — what to ask, what to NEVER ask

Like the sibling UGC flows, every workflow parameter is pinned (models, aspect ratios, resolution,
audio, composite style). Use `ask_question` ONLY for creative gaps.

### NEVER ask
- **Aspect ratio / resolution / model** — locked (`text2image_soul_v2` creator, `seedance_2_0`
  clip; no board model; final `9:16` `1080p`).
- **Audio** — always on; the creator's Seedance voice is the spine.
- **Whether to caption at all** — captions are ON by default; never ask whether to add them, only
  honour an explicit "no captions" request. (The layer STYLE — `Subtitles` / `Hook` / `Both` — IS
  offered as a creative choice; see DO ask.)
- **Composite style** — creator on camera throughout, useful screenshots as large insets over the
  face, captions along the bottom. Never offer a full-screen site, scrolling, or transition forks.
- **N clips / split** — derived from duration.
- **How to show the app** — real captured screenshots overlaid as cards, always. Never offer
  "generate the UI" or "animate a screenshot" — those are out of scope by design.

### DO ask (creative gaps only — bundle into ONE call)
| Question | Ask when | Notes |
|---|---|---|
| **Website URL** | Brief gave no URL. | Freeform — "share the link to your site / app / store". Required; the site is the hero. |
| **Duration** | Brief gave no length. | Offer `10s` / `15s` / `30s` / `45s` + `Other`. |
| **Caption style** | Always offer (unless the brief already picks a mode, or says "no captions"). Bundle into the up-front call. | 3 options — **Both** (hook plate + bottom captions — **default** on no-answer) / **Subtitles** (bottom captions only) / **Hook** (top hook plate only). Never a "no text" option — captions are on; only an explicit "no captions" brief skips them. |
| **Couldn't capture the site** | ANY first-try capture failure — `website_screenshot` errors / unavailable / bot-block (`image_analyze` on `site_full.png`: CAPTCHA / "verify you're human" / Cloudflare / access-denied / blank) / behind a login / unreachable / <3 real cards. **Ask immediately.** | 2 options + freeform: **"I'll send screenshots"** (user pastes key screens — product/reviews/price/specs; used as the capture); **"Make it without the site"** (talking-head only, no screenshot insets). If the user picks "send" but no screenshots arrive, or ignores the question → **degrade to talking-head-only** and say so in the report. See `website-capture.md`. |
| **Publish to TikTok?** | After `output/final_captioned.mp4` exists (Step 8). | 2 options: **"Yes, publish"** / **"No, just the file"**. See Step 8 for the connect + publish flow. |

If the brief already answers these, proceed silently.

## Critical rules

- **The screen is always real captured pixels.** No AI-generated UI, no image-to-video, no scroll.
- **Creator on camera the whole video.** Every beat's audio is a generated talking-head clip; the
  screenshots only overlay on top as cards. First ~1–2s (`t_hook = min(2.0, t(hook_words))`) = hook
  on the face; closer = product action.
- **Useful screenshots only, as large insets OVER the face.** Product, reviews, specs, pricing;
  ~0.78·W wide, height ceiling ~0.60·H, centred slightly up (bottom clear of the caption band);
  ~1.2–1.5s each (variant B), interrupted by clean-face gaps; skip filler. Never full-screen, never
  scroll; no blur/backing.
- **English speech always** (unless the user explicitly asks otherwise); American accent, no British.
- **Captions ON by default, via the `montage` skill's §3 — the SAME path as `ugc-flow`** (raw
  word-level Whisper, no script alignment). The `caption_mode` (`Both` default / `Subtitles` / `Hook`)
  selects the layers: **bottom captions** (Metropolis, sentence case, `--size 50 --no-caps`) and/or a
  **top hook plate** (Metropolis, CAPS, the authored hook line). Timing is a word-level Whisper
  transcript of the FINAL audio — never planned beats; silence carries no caption. Only an explicit
  "no captions" request skips it. Deliverable `output/final_captioned.mp4`, else `output/final.mp4`.
- **Product-free body.** Character-only clip path; no `product-analyzer`, no Angle Lock. The product
  appears only in the closer action (in-hand if physical, on the phone otherwise); a device is fine.
- Creator identity locked via a single `character_media_id`; no mid-pipeline regeneration. When
  `character_provided == false` the Soul seed is de-slopped once via a Seedream i2i pass (Step 3.5) and
  the **de-slopped** output becomes that locked `character_media_id`; it then seeds every Seedance clip
  — no storyboards, no `gpt_image_2` board step. (User-provided photos are never de-slopped.)
- Seedance clips submitted in one parallel batch.
- **Capture fails on the FIRST try → immediately ask the user (`ask_question`), never improvise.**
  If `website_screenshot` errors / is unavailable / bot-block / login / unreachable / returns <3 real
  cards, ask right away — two paths: **"I'll send screenshots"** or **"Make it without the site"**. Do
  NOT silently retry, run the browser toolkit yourself, web-search, or pull off-page images, and NEVER
  fabricate / AI-generate a UI. Screen content = the real capture OR the user's uploaded screenshots —
  nothing else.
- **No screenshots → degrade, don't dead-end.** If the user chooses "make it without the site", or
  the ask goes unanswered / no screenshots arrive, generate the **talking-head-only** video (the full
  creator + monologue spine, with NO screenshot insets in the composite) and **state in the report that
  the site could not be shown**. A talking-head-only ad is the accepted fallback — never fail outright,
  never invent a UI to fill the gap.

## NOT for this workflow
- Physical-product UGC (talking-head with an object, unboxing, try-on, tutorial, product-only) →
  `ugc-flow` / `ugc-unboxing-flow` / `ugc-try-on-flow` / `ugc-tutorial-flow` / `ugc-product-flow`.
- Building or editing the website itself → out of scope; this flow only films a site that already exists.
- Cinematic / scripted long-form (non-UGC) → `cinematic-flow`.
- A request to AI-generate the app's interface or animate a static screenshot → out of scope;
  this flow only shows real captured site footage.

## References
Load each via `skill_view(name, file_path)`:
- skill `ugc-saas-flow`, file `references/website-capture.md` — headless-browser capture + fallback.
- skill `ugc-saas-flow`, file `references/saas-monologue.md` — SaaS script model, hook + card order.
- skill `ugc-saas-flow`, file `references/screen-broll-and-composite.md` — overlay-card composite.
- skill `montage`, `§3 Burned captions` — default captions (raw word-level Whisper, `--size 50
  --no-caps`) + optional top hook plate; the SAME path as `ugc-flow`.
- skill `ugc-saas-flow`, file `references/saas-ugc-character.md` — `ugc-character` enhancer input
  mapping + SaaS framing / setting / US accent / audio carried into the Seedance prompt.
- skill `ugc-saas-flow`, file `references/saas-clip-prompt.md` — ONE continuous talking-head clip;
  no board/cuts/Angle Lock; product-in-closer + no-rendered-site bans.