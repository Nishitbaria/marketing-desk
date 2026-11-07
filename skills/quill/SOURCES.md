# Sources

Adapted from `agent/skills/` in [Nishitbaria/super-creator](https://github.com/Nishitbaria/super-creator), by the same author. Generation, rendering and tool steps were left out; those belong to other agents.

| File | Source skill | What came from it |
|---|---|---|
| `hooks.md` | `youtube-hook-plot` | The asset engine, line craft, narrator modes, proof rules and tell list, condensed and cut down to short hooks. Calibration examples, teaser and mid-video CTA blocks were left out. |
| `formats.md` | `video-explainer-workflow` | One narrator, audio in the voice only, about 10 second blocks. Its "no timecodes" rule was dropped because Quill's script is timestamped. |
| `formats.md` | `youtube-faceless-video` | One voice, length as a multiple of 10 seconds, characters never talk on screen. |
| `formats.md` | `ugc-flow` | Draft the full monologue first, and the length to segment table. |
| `script-writer.md` | `script-writer` | The rule never to invent brand or product facts. |

`script-writer.md` is otherwise new writing for this repo. The source `script-writer` skill only routes to a backend enhancer Quill cannot call, and its links to `references/deslop.md` and `references/retention-laws.md` in `youtube-hook-plot` point at files that do not exist upstream. The default beats, word budgets, format defaults and shot list rules are new here.
