---
name: ad-copy
description: |
  Writes platform-ready paid-ad copy from a product, brand, or creative brief — multiple variants with distinct
  hook angles, each sized to the platform's real character limits (Meta, TikTok, Google, Amazon, YouTube).
  Invoke when the user says: "write ad copy", "ad headlines", "primary text for this ad", "captions for my ads",
  "Google ad text", "Amazon title and bullets", "fresh hooks for a tired ad", or types /ad-copy.
  Pairs with image/video generation (copy + creative) and consumes the brief-intake / product-analyzer outputs.
  NOT for: long-form articles/blogs, video scripts (use script-writer), or research (use trend-picker).
---
# Ad Copy

Generate paid-ad text that's ready to paste straight into the ad manager. Default to **multiple variants with different hook angles** — one angle rarely wins, and variants are exactly what A/B testing needs.

Pure text generation. **No shell, no external CLI.** Read a brand page with `web_extract` only if the user hands you a URL and the brand voice isn't already known from the brief.

## When to use

- The user asks for ad text / headlines / captions / primary text / bullets for a paid placement.
- As a step inside a URL→ads flow (after `product-analyzer` extracts the product) or a creative refresh (fresh hooks for a fatigued ad).

## When NOT to use

- Long-form copy (articles, landing pages, blogs) — out of scope.
- Spoken video scripts → `script-writer`. Research / trend lookup → `trend-picker`.

## Inputs (pull first, ask only the gaps)

Read what's already provided (a brief from Brief Intake, a `product-analyzer` result, the product photo/URL, or the message):

- **Product / brand** + the single biggest benefit
- **Platform(s)** + ad format
- **Audience**
- **Tone / brand voice**
- **Offer / CTA** (if any)

Ask via `ask_question` ONLY when **platform** or a core (product or offer) is genuinely missing — bundle into one call, never drip one question at a time.

## Hook angles (rotate across variants — pick 3–5 distinct ones)

1. **Problem → solution** — name the pain, then resolve it.
2. **Transformation** — before/after, the outcome state.
3. **Social proof** — popularity, counts, testimonials feel.
4. **Curiosity / pattern-break** — an open loop that demands the click.
5. **Urgency / scarcity** — only when a real offer or deadline exists.
6. **Objection-flip** — surface the #1 doubt and answer it.
7. **Identity** — "for people who…", belonging.

Each variant = one clearly different angle. Never ship near-duplicate variants.

## Platform formats & limits

Respect the caps — copy that overflows is truncated in-platform.

| Platform | Fields | Practical limits |
|---|---|---|
| Meta (FB/IG) | Primary text, Headline, Description | primary ~125 chars before "See more", headline ~40, description ~30 |
| TikTok | Caption / on-screen hook line | caption ≤ ~100 chars, native and punchy |
| Google Search | Headlines (≤30 chars), Descriptions (≤90 chars) | hard caps; supply several headlines + 2–4 descriptions |
| Amazon | Title, 5 bullet points | title ≤ ~200 chars; bullets benefit-led, not spec dumps |
| YouTube | Title (≤100 chars), Description | hook in the first line before the fold |

## Output

For each requested platform: **N variants (default 3)**, each labeled with its hook angle, every field filled and within limits. Keep it tabular / scannable so the user can paste fields directly.

## Notes

- Match the user's language.
- Anchor claims to the product's REAL benefits (from `product-analyzer` / the brief) — never invent specs, prices, or results.
- **Refresh case (Performance Strategist):** when replacing a fatigued ad, generate net-new angles that differ from the existing creative — not paraphrases of it.
- Do not add legal disclaimers or AI labels — out of scope for this skill.
