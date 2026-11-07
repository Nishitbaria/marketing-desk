Director is the studio's lead and the only agent the creator talks to. It routes and reports. It never writes, renders or checks the brand.

Inputs: the creator's one-line ask, plus `brand/brand.md`, `brand/MOTION.md` and `skills/director/SKILL.md`.

Outputs: one brief, a one-line status after each handoff, a question to the creator for any `[need: ...]`, a final tag to the creator with the MP4 path, and a closing line once the creator approves. It edits no files. See [samples/director-run.md](../samples/director-run.md).

It runs from `agents/studio.template.yaml`, which is the source of truth.

```mermaid
flowchart TD
  C[Creator] -->|one-line ask| D[Director]
  D -->|brief| Q[Quill]
  Q -->|script| K1{Keeper: script}
  K1 -->|FIX, max 2 loops| Q
  K1 -->|PASS with a need| N[Director asks you]
  N -->|your answer| Q
  K1 -->|PASS| R[Cut]
  R -->|MP4| K2{Keeper: render}
  K2 -->|FIX, max 2 loops| R
  K2 -->|PASS| D2[Director]
  D2 -->|MP4 path, approve or your change| C
```

Switch wakes an agent only when a message addresses it. So Quill, Cut and Keeper add a `cc @studio-director` line to each handoff, and Director posts its status from that. Its status line has no @ mention, so it wakes nobody.

The third FIX on the same piece stops the chain. Keeper sends it to Director, and Director asks the creator.

Only the creator approves a video. `@studio-director approved render` is Keeper's routing line for a brand PASS, not approval.
