# One-Person Studio

Video team for solo creators on Switch, for the WeMakeDevs Flip the Switch hackathon. Reply to Nishit in Hinglish, short and direct.

## Team

`agents/studio.template.yaml` is the source of truth for every agent, the main room and its kickoff. Import it in Switch Console to apply a change. `agents/video-room.template.yaml` defines each video room. Director reads it from the repo, so it needs no import.

| Agent | Job | Skills |
| --- | --- | --- |
| `studio-director` | Leads the team, the only agent the creator talks to | `skills/director/` |
| `studio-quill` | Writes the script | `skills/quill/` |
| `studio-cut` | Renders the MP4 into `renders/<slug>/` | `skills/cut/` |
| `studio-keeper` | Checks scripts and renders, replies PASS or FIX | `skills/keeper/` |

Flow: creator asks Director in the main room, Director opens a video room from `agents/video-room.template.yaml`, then Quill writes, Keeper checks, Cut renders, Keeper checks and Director tags the creator there. Reel is planned and not built.

## Rules

- Never invent product facts, prices, stats, quotes or links. Use `[need: ...]`.
- Only the creator approves a video. Agents never upload, post or publish.
- `brand/brand-kit.md` is demo data for the fictional Driftnote. `brand/brand.md` and `brand/MOTION.md` come from it. Read them before any visual or script work.
- Template files take only fields documented in Switch's `docs/TEMPLATES.md`. Do not invent fields.
- Keep `auto_approve: false` on every agent. A template has no include, so all agents live in one file.
- Remotion is the only render engine, with remocn components. Pins are `create-video@4.0.541`, `@remotion/sfx@4.0.541`, `@remotion/transitions@4.0.541` and `shadcn@4.23.0`. New renders never use HyperFrames. Do not run `npx skills add`, the remocn skill is vendored in `skills/cut/remocn/`.
- Commit no secrets, no `.hyperframes/`, no `out/`, and no MP4 except the one Notely demo.
- Do not read `~/Library/Application Support/switchdash/control-api.json` or any `credentials.json`.
- No em dashes in any file, script or reply.

## Git

- This is a hackathon repo. Commit directly to `main` and push. No branches or PRs.
- Commit, push or merge only when Nishit says so in that moment.
- Never force-push, and never use `--admin`.
- Stage named paths, never `git add .`.

## Checks

Run after changing the template:

```bash
PY="$HOME/Library/Application Support/switchdash/local-switch-server/native/switch-core/0.31.0/venv/bin/python"
"$PY" -I -c "from switch_core.template_lint import lint_template as l; r=l(open('agents/studio.template.yaml').read()); print(r.ok, r.errors, r.warnings)"
```

Run in `renders/<slug>/` after changing a composition:

```bash
npx tsc --noEmit
```

Then look at one frame per beat. A passing check does not show how a frame looks. Report a render only after `npx remotion ffprobe` confirms it.

## Known issues

- Keep `verbose: false` in `~/.claude/settings.json`. With `true`, Switch Console shows Claude as signed out or too old.
- Delete an existing `studio-*` agent before re-importing the template. Switch refuses a name already in use.
