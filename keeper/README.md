Keeper checks every Quill script and Cut render against the brand and replies PASS or FIX.
Inputs: a script or MP4 path posted in the room, plus `brand/brand.md`, `brand/MOTION.md` and `skills/keeper/SKILL.md`.
Outputs: one BRAND CHECK reply with up to 5 exact fixes and a Next line. It edits no files. See `samples/`.
To merge: add `KEEPER-AGENT.yaml` to the template's `agents:` list, add `studio-keeper` to the room, and mention it in the kickoff.
Cut must also end its render post with `@studio-keeper brand check`, or Keeper never wakes for renders.
