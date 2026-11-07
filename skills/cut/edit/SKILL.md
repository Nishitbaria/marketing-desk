---
name: edit
description: |
  Always read this SKILL.md before editing an existing video clip — adding, removing,
  replacing or modifying elements, motion transfer, and other prompt-driven edits of a
  supplied video.
---
# Edit

Transformations of an existing video: the user supplies the source media, and the result is a new video derived from it.

## Modes

| Solution | Request looks like |
|---|---|
| `references/main-edit.md` — the default mode; global single-edit workflow | one concrete change — add/remove/replace/modify |
| `motion_control` tool (Kling 3.0) — motion control | character image + reference video, character takes on reference's motion |