# Persona-Clone Trigger (Audience-Parity)

Canonical home for trend-picker Mode C post-detection orchestration. Owned by `skills/research/trend-picker/` — the gate detector lives in `SKILL.md` § Activation Gate, this file describes what runs after the gate fires.

Fires only after Rule 0 is confirmed NOT applicable (no user-supplied source video URL with adapt intent). Activate when ALL four conditions hold: (a) brief references an existing creator (`@username` or platform URL to a profile, not a single video), (b) intent is to create a **new** persona/influencer, (c) phrasing implies audience parity ("hit the same audience", "like @X but not a copy", "such as @X", "under the same audience as @X"), (d) output is multi-post / multi-reel / content plan (not a single one-shot).

When triggered, do NOT load the soul-id skill or start generation until the user picks depth via `AskUserQuestion`: **Deep** (video-DNA pipeline: reel-level video analysis + adaptation per reel, ~5-10 min, higher cost) or **Quick** (metadata-only research, fast and cheap).

## Deep Path

This procedure is executed directly by the model — no separate agents are involved. The model loads each skill in sequence (or in parallel where noted) via `skill_view` and runs the steps inline.

1. **Load the trend-picker skill with `mode=creator_dna`** — returns an aggregate DNA report URL plus the top-3 reel URLs. (See trend-picker SKILL.md § Mode C.)
2. **Generate ONE base portrait** of the persona via a direct t2i call (`text2image_soul_v2`, neutral pose, clean outfit, face-forward, no props). The system prompt for this call is `skills/media/image-generation/character/references/soul-v2-ugc-character.md` — this is the canonical UGC-character spec, and the persona will be referenced into Seedance reels in Branch V, so the UGC-character file applies (NOT `soul-v2-avatar.md`). `nano_banana_2` is FORBIDDEN on this path — it produces a non-editorial look that poisons LoRA training. After the job completes (poll required), persist the result for both branches: `artifact_put(key="base_kadr:job_id", value="<job_id>")` and update `artifact_put(key="mode_c:state", value={"phase": "base_done"})`.
3. **Fork into TWO ASYNC BRANCHES from the same base kadr.** Both branches start in the same message; **Branch V must NOT wait for Branch I** (Branch I work is carousel-only). Submit the Branch V uploads/elements/seedance jobs **before or in parallel with** Branch I work — never serialize.

   - **Branch V (video, starts immediately):** `upload(files=[...])` → `element(action="create", category="character", medias=[...])` → for each reel URL from step 1, run **`video-adapt` in avatar-swap mode** (`policy.visual_policy == "swap_character"`) in parallel using the shared `character_element_id` via `<<<element_id>>>` in the Seedance prompt. Video-adapt does NOT build its own element on this path — it consumes the shared one.
   - **Branch I (image, runs in parallel with Branch V):** same base kadr → `nano_banana_2` produces 4 pose/outfit variations with the base kadr wired in as the reference image via the model's correct reference field (NOT a generic `image_urls` guess — verify the field name before the call). Then ask the user how to complete the carousel via `AskUserQuestion` — both paths are equally valid; do NOT pick a default, wait for the user:

     ```
     AskUserQuestion(
         question="How should the carousel be finished?",
         options=[
             {"label": "Train Soul ID — ~30 min upfront wait, persistent identity that survives across sessions, cheaper per frame at scale", "value": "soul_id"},
             {"label": "Skip training, generate frames via NB2 with the base kadr as reference — instant start, higher cost per frame, identity not persisted between sessions", "value": "nb2_direct"},
         ],
     )
     ```

     - **Path A — `soul_id`:** load the **soul-id skill** to train a Soul ID on the 5-kadr dataset → once training completes, load the **image-generation skill** to produce carousel/stills via Soul 2.0 with `soul_id`.
     - **Path B — `nb2_direct`:** skip training entirely → load the **image-generation skill** to produce each remaining carousel frame via `nano_banana_2` with the base kadr passed in as the reference image (same shape as the 4 variations already submitted in this branch).

4. **Reels NEVER wait for Branch I.** Only the carousel depends on Branch I, regardless of which Path A/B is chosen. If you find yourself blocking on Branch I before submitting Branch V Seedance jobs, you have serialized incorrectly — re-issue Branch V immediately.
5. **The model does not hand-craft Seedance prompts on this path.** Branch V prompts come from `video-adapt` Step C (`vadapt_adapt` flow `vadapt-adapt-avatar`) byte-for-byte; image prompts come from image-generation skill conventions.

## Quick Path

Current behaviour: metadata-level research (no Mode C, no Gemini DNA extraction) → load the soul-id skill if a recurring persona is needed → direct image/video generation via the appropriate skill.

Cache the DNA report URL (if Deep was previously run) in the session artifact list so follow-up requests in the same chat reuse it instead of re-analyzing.

## Session artifact contract

The Persona-Clone pipeline propagates state across skills via the session artifact registry. Canonical keys:

| Key | Value | Set by | Read by |
|---|---|---|---|
| `mode_c:state` | `{phase: "entry" \| "dna_done" \| "base_done" \| "branches_dispatched"}` | trend-picker entry gate; updated each phase | all downstream skills |
| `mode_c:depth` | `"deep"` \| `"quick"` | trend-picker entry gate (from `AskUserQuestion`) | all downstream skills |
| `creator_dna:<reel_url>` | per-reel Gemini JSON | trend-picker Mode C step 2 | image/video Workflow D |
| `creator_dna:aggregate_url` | URL of aggregate DNA report | trend-picker Mode C step 4 | image/video Workflow D |
| `base_kadr:job_id` | `job_id` of the base portrait | step 2 above | Branch I (NB2 reference), Branch V (element source) |
| `character_element_id` | `element_uuid` after `element(action="create")` | Branch V step 1 | every Seedance job in Branch V (`<<<element_uuid>>>` in prompt) |

Downstream skills (`skills/media/image-generation/SKILL.md` § Workflow D, `skills/media/video-generation/SKILL.md` § Handoff input mode) MUST check `artifact_get(key="mode_c:state")` first — when present, HANDOFF validation failure is a hard-stop, not a fall-through.

## Reasoning telemetry

On each Mode C transition, emit one short line in your reasoning so log readers and ultrareview can spot pipeline skips:

- `[MODE_C STATE: phase=entry, depth=undecided]` — persona-clone trigger fired
- `[MODE_C STATE: phase=entry, depth=deep, reels_to_analyze=3]` — after `AskUserQuestion`
- `[MODE_C STATE: phase=dna_done, dna_url=<url>]` — Mode C aggregate uploaded
- `[MODE_C STATE: phase=base_done, base_kadr_id=<job_id>]` — step 2 (base portrait) completed
- `[MODE_C STATE: phase=branches_dispatched, video_jobs=<n>, image_jobs=<m>, character_element_id=<uuid>]` — step 3 fan-out submitted

Zero-cost telemetry. A missing phase line in the log = the corresponding step was skipped.
