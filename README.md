# One-Person Studio

A video team for solo creators, built on [Switch](https://docs.switchagents.ai) for the WeMakeDevs "Flip the Switch" hackathon. You drop one line in Slack or Discord and agents write and make the video. You are the only human and you approve the final cut.

The planned team is Quill for words, Reel for visuals, Cut for the edit and Keeper for brand checks. **Only Quill is built so far.**

## What Quill does

Quill writes every word in a video: hooks, launch scripts, explainers, UGC talking-head scripts and faceless voiceovers. Ask it:

```
@studio-quill launch video for my app "Notely", 30s, vertical, for indie devs
```

It replies in the room with the format, 3 hook options, a timestamped script, a shot list and open questions, then ends with `ready for @studio-keeper brand check`. Keeper does not exist yet, so that line goes nowhere today.

Quill follows `brand/brand-kit.md` and lists what it does not know instead of inventing it. It never generates media, never publishes and never posts outside the room.

## How Switch is used

`agents/studio.template.yaml` is the whole setup: it declares the agent, the room, the room's kickoff and the form values. Switch runs the agent, mirrors the room to your chat app and keeps you in the loop.

## Import it

1. In Switch Console, open **Templates**, choose **Import template**, paste `agents/studio.template.yaml` and click **Import**, then **Save**. Steps for a new install are in [SETUP.md](SETUP.md).
2. Choose **Use template**, then **Create agent and room**. The form asks for nothing; provider, machine and directory sit under Advanced.
3. Quill says hello in the `studio-studio` room.

`directory` defaults to one absolute path on the author's machine. On another machine, change it under Advanced to this repo's root.

## Test it

Send each ask in [samples/asks.md](samples/asks.md). Quill passes if the reply has all six parts, stays in brand tone, lists open questions instead of making up facts, and ends with the required line.

## Make it yours

Replace `brand/brand-kit.md`. The demo brand, Driftnote, is fictional and labelled `DEMO / SYNTHETIC`. Skill credits are in [skills/quill/SOURCES.md](skills/quill/SOURCES.md).

## License

MIT, see [LICENSE](LICENSE).
