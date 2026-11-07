---
name: video-repurpose
description: |
  Repurposing an EXISTING video asset into other platform formats — reframing, cutting, captioning, translating/dubbing.
---
# Video Repurpose

One source video in → a pack of platform-adapted derivatives out.

## Order of operations
1. Ingest + probe specs
2. Analyze + clip-worthy moments
3. Ask about captions (mandatory)
4. Resolve targets per platform
5. Cut moments from long video
6. Reframe per target aspect ratio
7. Enhance (upscale if needed)
8. Caption / localize
9. Assembly (if multiple cuts)
10. QC gate
11. Deliver

## Reframe strategy
- Default: blur-pad letterbox (deterministic, no AI cost)
- AI reframe (reframe) only when blur-pad looks bad