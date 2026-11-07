---
name: youtube-faceless-video
description: |
  THE flow for faceless, narrator-led EXPLAINER videos for social channels — 30s to 3+ min, default 16:9.
---
# youtube-faceless-video

## Pipeline (Phases 0→8)
Phase 0: Intake (2 question screens + voice widget)
Phase 1: Style anchor
Phase 2: Asset roster (characters, locations, props)
Phase 3: Script + block plan
Phase 4: Generate blocks (gemini_omni)
Phase 5: Voiceover (seed_audio)
Phase 6: Assemble → ONE final video
Phase 7: CAPS subtitles (if opted)
Phase 8: Offer upscale

## Golden rules
- Models are LOCKED. Never substitute.
- Every clip is ONE 10s block of 3 hard cuts (Kids: 4 cuts)
- Characters never talk on screen
- Duration is FIXED = N×10s
- One voice everywhere
- No time-stretching in post