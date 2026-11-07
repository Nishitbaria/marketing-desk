# Ad Script

Premium 15-second TV/commercial ad script — logline, 7-panel beat structure, hero,
world, dialogue/VO, tagline, music. Use for any request to write an ad / commercial
script, standalone or as the script step of the `tv-ad` workflow.

## Call

`enhancer(flow="tv-ad-script", inputs={...}, image_refs={...})`

inputs:
- `ad_type` — `problem-solution` | `lifestyle` | `high-energy`
- `tone` — heartfelt | witty | dramatic | aspirational | playful | null (null when high-energy)
- `duration_seconds` — 15
- `user_creative_brief` — the user's request / idea (may be empty)
- `client_brand` — brand JSON | null
- `product_dna` — product JSON | null
- `is_screen_bearing` — true | false
- `character_provided` — true | false

image_refs (optional): `product_url`, `character_url`, `brand_url`.

**Standalone** (a plain request to write an ad script): pass the user's request as
`user_creative_brief`; fill `ad_type` and any other fields that are clear from the
request, otherwise leave them null — do not invent brand/product facts. Omit `image_refs`.
**In the `tv-ad` workflow:** every field is supplied from the pipeline (Stages I–II).

## Result

Returns `{"prompt": "<the script as plain structured text>"}` — use `result.prompt`
directly as `script_text` (NO `JSON.parse`; it's a labeled, human-readable script).
The `tv-ad` workflow forwards `script_text` verbatim to the character / location /
seedance enhancers; standalone, present it to the user as-is.