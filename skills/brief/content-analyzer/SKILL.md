---
name: content-analyzer
description: |
  General-purpose content analysis — a growing set of modes that parse a concrete artifact the user already has into structured analysis for a downstream use case. Pick the mode matching your intent and load its reference via skill_view. Use for "analyze this for editing/marketing", any "analyze X for <use case>". NOT for trend/creator research (trend-picker), product preprocessing (product-analyzer), brand extraction (brand-analyzer), or generation.
---
# Content Analyzer

Utility skill — a broad, growing set of content-analysis modes. Each mode runs a
dedicated enhancer and returns structured analysis. Pick the mode matching your
intent, then load the matching reference via `skill_view`.

## When to use

Called by workflows (or directly) at the analysis stage, before any downstream
editing / marketing / generation step, whenever a concrete content artifact must
be turned into a structured, use-case-oriented analysis.

## Modes

| Intent | Reference to load | What you get |
|---|---|---|
| Analyze content for editing | `references/edit-video-analyze.md` | Seedance 2 video-to-video edit prompt for a single add / remove / replace / modify edit |
| Analyze a video for marketing | `references/marketing-analyze.md` | Marketing teardown of a video — hooks (visual / audio / semantic), retention beats, CTA, shareability (STEPPS) |

Load only the reference matching your case — do not pull both.

```
Editing intent   → skill_view("content-analyzer", "references/edit-video-analyze.md")
Video marketing analysis → skill_view("content-analyzer", "references/marketing-analyze.md")
```

## NOT for this skill

- Product input preprocessing → `analyzer/product-analyzer`.
- Brand asset extraction (logo, color palette from a brand homepage) → `analyzer/brand-analyzer`.
- Trend / viral / creator research → `research/trend-picker`.
- Image / video generation → `media/*` or a `workflow-generation/*` flow.
