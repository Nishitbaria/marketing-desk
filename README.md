# One-Person Studio

A video team for solo creators, built on [Switch](https://docs.switchagents.ai) for the WeMakeDevs "Flip the Switch" hackathon. You drop one line in Slack or Discord and agents write and make the video. You are the only human and you approve the final cut.

The planned team is Quill for words, Reel for visuals, Cut for the edit and Keeper for brand checks. **Quill and Cut are in the template today.**

## Agents

| Agent | Job | Skills | Output |
| --- | --- | --- | --- |
| `studio-quill` | Writes the script | `skills/quill/` | A script in the room, ending `@studio-cut render it` |
| `studio-cut` | Renders the script | `skills/cut/` | An MP4 under `renders/<slug>/`, then a tag to the creator for approval |

### What Quill does

Quill writes every word in a video: hooks, launch scripts, explainers, UGC talking-head scripts and faceless voiceovers. Ask it:

```
@studio-quill launch video for my app "Notely", 30s, vertical, for indie devs
```

It replies in the room with the format, 3 hook options, a timestamped script, a shot list and open questions, then ends with `@studio-cut render it`.

Quill follows `brand/brand-kit.md` and lists what it does not know instead of inventing it. It never generates media, never publishes and never posts outside the room.

### What Cut does

Cut picks up Quill's script, builds the video with HyperFrames, renders it to `renders/<slug>/` and tags you for approval. It uses Quill's words unchanged, and it never uploads or publishes anything.

## How Switch is used

`agents/studio.template.yaml` is the whole setup: it declares the agents, the room, the room's kickoff and the form values. Switch runs the agent, mirrors the room to your chat app and keeps you in the loop.

## Import it

1. In Switch Console, open **Templates**, choose **Import template**, paste `agents/studio.template.yaml` and click **Import**, then **Save**. Steps for a new install are in [SETUP.md](SETUP.md).
2. Choose **Use template**, then **Create agents and room**. The form asks for nothing; provider, machine and directory sit under Advanced.
3. Quill and Cut say hello in the `studio-studio` room.

`directory` defaults to one absolute path on the author's machine. On another machine, change it under Advanced to this repo's root.

## Test it

Send each ask in [samples/asks.md](samples/asks.md). Quill passes if the reply has all six parts, stays in brand tone, lists open questions instead of making up facts, and ends with the required line.

## Make it yours

Replace `brand/brand-kit.md`. The demo brand, Driftnote, is fictional and labelled `DEMO / SYNTHETIC`. Skill credits are in [skills/quill/SOURCES.md](skills/quill/SOURCES.md).

## License

MIT, see [LICENSE](LICENSE).
