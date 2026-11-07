---
name: ai-influencer-flow
description: |
  Generate a standalone AI influencer: one clean photoreal UGC creator/persona image (no products) via Soul 2.0, reusable as a character reference.
---
# ai-influencer

Standalone generator for a single AI influencer — one clean UGC-feel person image.

## Pipeline

1. Parse the request — extract gender, age, hair, ethnicity, location, outfit, mood
2. Character enhancer (text-only) via `enhancer(flow="ugc-character", ...)`
3. Generate via `generate_image(model="text2image_soul_v2", ...)` with `enhance_prompt: false`
4. Poll, register as character element, report

## Pinned invariants
- Model: `text2image_soul_v2`. Aspect ratio: `3:4`. Quality: `1080p`
- `enhance_prompt: false` always
- No products / objects / props in the character image