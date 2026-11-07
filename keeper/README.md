Keeper checks every Quill script and Cut render against the brand and replies PASS or FIX.
Inputs: a script or MP4 path posted in the room, plus `brand/brand.md`, `brand/MOTION.md` and `skills/keeper/SKILL.md`.
Outputs: one BRAND CHECK reply with up to 5 exact fixes and a Next line. It edits no files. See `samples/`.
It runs from `agents/studio.template.yaml`, which is the source of truth.
Quill and Cut wake it by ending their posts with an `@studio-keeper` line.
