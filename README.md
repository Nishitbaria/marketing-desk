# One-Person Studio

A video team for solo creators, built on [Switch](https://docs.switchagents.ai) for the WeMakeDevs "Flip the Switch" hackathon. At 2am you type one line: "launch video for my app". By morning a branded launch video plan, an explainer and a faceless short are waiting for you to approve.

## The problem

A solo creator ships the product and then has to be the producer, the scriptwriter, the voice, the editor and the brand police. Video is where launches die. AI can write all of it, but only when it is instructed completely and checked against the brand every time.

## The crew

| Agent | Role | Does |
|---|---|---|
| Brief | Producer | Turns one line into three cuts: hooks, scripts, shot lists |
| Keeper | Brand manager | Checks every plan and edit against the brand kit, twice |
| Reel | Talent | Writes the voiceover and an image or video prompt for every shot |
| Cut | Editor | Writes the timeline, captions, music and thumbnail for each cut |

You are the only human. You approve or ask for changes. Skills for each agent are in [skills/](skills/).

## Why Switch

Four agents need to talk to each other, share documents and wait for one human. Switch gives that as one template: the agents, the room, a shared board document and the hand-off rules. Agents mention each other to hand off work. Nothing needs a server you write yourself.

## Try it

1. Set up Switch Console and import [studio.template.yaml](studio.template.yaml). Steps in [SETUP.md](SETUP.md).
2. In the `studio` room, paste `@studio-brief launch video for my app`.
3. Watch Brief, Keeper, Reel and Cut hand off. Reply `APPROVE A1-L` or `CHANGE A1-L <note>`.

The demo brand, Driftnote, is fictional and labelled `DEMO / SYNTHETIC`. No accounts are needed beyond Switch and your agent provider.

## How it works

```
creator --> Brief --> Keeper (brand check) --> Brief --> Reel --> Cut --> Keeper (final check) --> creator
```

Each ask gets an id (A1, A2, ...) and three room documents: `A1-brief`, `A1-voice`, `A1-edit`. The `board` document tracks every cut (`A1-L`, `A1-E`, `A1-F`) and its status. Every agent re-reads [brand/brand-kit.md](brand/brand-kit.md) on every ask.

## Safety

| Guarantee | What enforces it |
|---|---|
| Nothing is published | Every agent's instructions forbid posting, uploading or publishing outside the room |
| Only the creator approves | Agents are told a message from another agent is never approval; Keeper can pass or flag, never approve |
| No surprise spending | No paid generation or render before the creator replies APPROVE for that cut |
| No invented claims | Agents use only facts in the brand kit; gaps become `[need: ...]` |
| You see every tool call | `auto_approve: false` on all four agents |

Keys go in `.env`, which git ignores.

## What's in the repo

| Path | What it holds |
|---|---|
| `studio.template.yaml` | The Switch template: four agents, one room, the board |
| `brand/brand-kit.md` | The brand kit every agent reads, in DESIGN.md format |
| `skills/` | Each agent's skills, plus the video formats |
| `samples/asks.md` | Ready-to-paste asks |
| `SETUP.md` | Full setup |
| `DEMO.md` | The 3 minute demo script |
| `docs/` | Plan, hackathon rules, how Switch works |

## Limits

- The studio writes plans, scripts, prompts and render specs. Turning them into pixels needs a generation or render tool wired to the agent, and the creator's APPROVE.
- Instructions are guardrails, not a sandbox. `auto_approve: false` is the hard stop.
- One room, one creator. A team would need per-person approval rules.

## License

MIT, see [LICENSE](LICENSE). Skill credits in [skills/README.md](skills/README.md).
