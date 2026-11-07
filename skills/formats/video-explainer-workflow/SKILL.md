---
name: video-explainer-workflow
description: |
  A narrated NON-photoreal animated explainer or story video: one narrator over stylized 10-second blocks, one style key locks the look.
---

# Video Explainer (Workflow)

## Pipeline
Phase 0: Ask (duration, language, style/preset, character, aspect)
Phase R: Research the topic
Phase 1: Style key
Phase 2: Narration (N blocks)
Phase 3: Block prompts
Phase 3b: Script gate
Phase 4: Render clips (gemini_omni)
Phase 5: Voiceover (seed_audio)
Phase 5b: Music bed
Phase P: Presenter overlay (if presenter mode)
Phase 6: Assemble
Phase 6b: Cover (optional)
Phase 6c: Final QC
Phase 7: Report (platform jobs only)

## Hard rules
- No realism. Ever. Non-photorealistic only.
- Faceless audio in clips (no dialogue, no lip-sync)
- Per-block, no timecodes
- Always assemble automatically
- Voice 100%, music quiet