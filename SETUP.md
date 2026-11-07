# Setup

Switch does not live in this repo. Switch Console, a desktop app, runs the server for you.

## Requirements

The agents run on your computer and use the tools installed there, so nothing below comes with the repo. Install these before you open Switch Console, or fully quit and reopen it afterwards. Console reads your PATH once, when it starts.

| Tool | Used by | Install | Check |
| --- | --- | --- | --- |
| [Switch Console](https://docs.switchagents.ai/switch-rooms/getting-started/install-switch-console.md) | Runs the server and the agents | macOS `.dmg`; Windows and Linux are early access | Server shows Running |
| [Claude Code](https://code.claude.com/docs/en/quickstart), signed in | All four agents | See its docs | `claude auth status` |
| [Node.js](https://nodejs.org) 22 or newer | Cut, to run HyperFrames | See its site | `node -v` |
| FFmpeg and FFprobe | Cut renders with FFmpeg; Cut and Keeper measure with FFprobe | macOS: `brew install ffmpeg`. Windows: `winget install --id Gyan.FFmpeg -e` | `ffmpeg -version`, `ffprobe -version` |

HyperFrames needs no install. Cut runs the pinned `hyperframes@0.9.19` through `npx`, so the first render needs internet. To check a machine before a run:

```bash
npx --yes hyperframes@0.9.19 doctor
```

FFmpeg, FFprobe and Chrome must pass. whisper-cpp, TTS, BGM and Docker can fail, because the studio does not use them. Docker is only needed for the bundled Mattermost.

## Steps

1. Install Switch Console: on macOS, open the `.dmg` and drag it into Applications; on Windows, run the `.exe` ([install guide](https://docs.switchagents.ai/switch-rooms/getting-started/install-switch-console.md)).
2. In Console, choose **Add a server**, then **Run a server on this computer** ([add a server](https://docs.switchagents.ai/switch-rooms/getting-started/add-a-server.md)).
3. Finish the guided setup with Claude Code signed in ([getting started](https://docs.switchagents.ai/switch-rooms/getting-started.md)).
4. Check **Gateway > Machines** shows this computer online. If it does not, create one agent by hand under **Agents** on this computer; that enrolls the machine.
5. Link your chat account under **Identities**. Then in **Templates**, import `agents/studio.template.yaml` and choose **Use template**. Set `directory` to this repo's absolute path. Set `bridge` to your chat app's display name, or leave it empty for the server's default app.
6. Open the `studio-studio` room. Each agent says hello in one line.
7. Paste an ask from [samples/asks.md](samples/asks.md).

## Make it yours

Send `@studio-director brand intake https://your-site.com`, check the draft and pick a voice. Keeper saves the brand files. Keeper reads the site with the [Firecrawl CLI](https://docs.firecrawl.dev/sdks/cli) when you have it: run `npm i -g firecrawl-cli`, then `firecrawl login`. A scrape uses your Firecrawl credits. Without it, Keeper uses `skills/keeper/extract-site.py`, which reads less and cannot check contrast. With no website, edit [brand/brand-kit.md](brand/brand-kit.md): your product, the facts agents may use, your voice and your banned words. Then update `brand/brand.md` and `brand/MOTION.md`, which the agents re-read on every ask.

## Notes

- A chat app is how a creator uses the studio day to day. If `{$creator}` is in a bridged room, link your chat account in Console first. To connect Slack, follow [docs/slack-setup.md](docs/slack-setup.md).
- Delete the existing `studio-*` agents before importing a new version.
- Every agent runs with `auto_approve: false`, so risky tool calls ask you first.
- Keys for generation tools go in `.env`, which git ignores. Never commit them.
