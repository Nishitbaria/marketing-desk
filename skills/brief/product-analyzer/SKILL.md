---
name: product-analyzer
description: |
  Product input preprocessing for media workflows. Extracts product data from e-commerce URLs (Amazon, Shopify, AliExpress, any product page) via web_extract, or analyzes product photos for category and usage/opening mechanic; output feeds downstream image/video generation. Use for "extract product from <URL>", "analyze this product photo", any product URL/photo as workflow input. NOT for trend research (trend-picker), source-video analysis (video-adapt), brand extraction (brand-analyzer), or generation.
---
# Product Analyzer

Utility skill. Two modes — pick the one that matches your input, then load the matching reference via `skill_view`.

## When to use

Called by media workflows (e.g. `workflow-generation/ugc-flow`, future product-driven workflows) at the input-parsing stage, before any generation. You typically do NOT invoke this skill directly from the user — it is a building block.

## Modes

| Input | Reference to load | What you get |
|---|---|---|
| Product URL (Amazon / Shopify / AliExpress / any e-commerce page) | `references/url-extract.md` | Structured product data (name, brand, price, variant, description, specs) + 3-5 curated product images filtered visually |
| Product photo only (no URL, no description) | `references/visual-analysis.md` | Product category + usage mechanic + opening mechanic + key visual details, ready for prompt building |

Load only the reference matching your case — do not pull both.

Inside `tiktok-organic-marketing`, `tiktok_organic(action="research")` owns the
research-stage URL extraction internally. Use this skill later only when the
selected generation route needs richer visual analysis.

```
URL → skill_view("product-analyzer", "references/url-extract.md")
Photo → skill_view("product-analyzer", "references/visual-analysis.md")
```

## NOT for this skill

- Trend / viral / creator research → `research/trend-picker`.
- Source video analysis for adaptation → `workflow-generation/video-adapt`.
- Brand asset extraction (logo, color palette from a brand homepage) → `analyzer/brand-analyzer`.
- Image / video generation → `media/image-generation`, `media/video-generation`, or a `workflow-generation/*` flow.
