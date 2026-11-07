---
title: "Stopped at the price: building a five-agent video team on Switch"
published: false
description: "Five AI agents in one chat room write, voice and render a launch video, and stop when a fact is missing. How it works, and how to build it yourself."
tags: ai, agents, showdev, tutorial
cover_image: https://raw.githubusercontent.com/Nishitbaria/studio-desk/main/docs/blog/cover.png
---

*One line in a chat room, five AI agents, and a real MP4 at the end. This is how we built a video team for solo creators on Switch, and how you can run it from zero. Built for the Flip the Switch Hackathon by WeMakeDevs and DevTools Academy.*

**The short version**

- You ask once. Director, Quill, Voice, Cut and Keeper hand the work to each other by mention, and a real MP4 comes out.
- When a fact is missing, the chain stops and tags you. When a render is wrong, Keeper sends it back. Nothing publishes.
- The whole team is one YAML file. Switch Console comes with Mattermost, so you can run it without a Slack workspace.

Demo video: [watch it on Loom](https://www.loom.com/share/2bd581aa44634f069d2b98b29801698e) · Live page: [one-person-studio.vercel.app](https://one-person-studio.vercel.app) · Repo: [github.com/Nishitbaria/studio-desk](https://github.com/Nishitbaria/studio-desk)

{% github Nishitbaria/studio-desk %}

{% embed https://www.loom.com/share/2bd581aa44634f069d2b98b29801698e %}

---

## The message that made the project

I typed one line into a chat room and went back to something else.

A little later, this came back:

```text
script passed brand check. Before we render, it still needs your input:
- Price of Driftnote Plus: should it appear on screen,
  and if so what is it?
- Launch date: should the CTA say "out now" or a specific date?
reply @studio-director with the answer
```

Nobody had told the team the price, and it was not in the brand files. So the agents did the most useful thing an AI agent can do when it hits a gap in what it knows.

They stopped.

No invented number on screen. No render burning ten minutes on a script that was wrong. Just a tag in the chat, and a question only I could answer.

That message is the whole project.

---

## The problem is not making the video

A solo creator launching a product needs a hook, a script, visuals, an edit and a final check. AI can do each of those now. The hard part is everything between them.

You usually end up with one of two bad options.

**One agent does everything.** It finishes, and it looks done. It also has every reason to fill a gap with something plausible, because a launch video needs a price and the agent would rather finish than ask. You find the made-up number later, if you find it at all.

**You run everything yourself.** That is safe, but you are now the writer's editor, the editor's project manager and the brand reviewer, copying text between windows. The agents saved you the typing and none of the coordination.

So we set one rule on the first day, and every design decision after it came from this:

> Facts come from the creator or the brand files, never from the model. Agents do the work, and a person makes the calls.

We called it **One-Person Studio**.

![Your chat app connects through Switch to five agents running on your machine, which read the repo](https://raw.githubusercontent.com/Nishitbaria/studio-desk/main/docs/blog/architecture.png)

---

## Five Switch words, explained

If you are new to Switch, these are all you need for this post.

| Word | What it means |
| --- | --- |
| **Room** | A shared space for people and agents. It shows up as a channel in your chat app |
| **Agent** | A team member with a name, an icon and a job |
| **Session** | The running copy of an agent that actually reads and replies |
| **Mention** | Writing `@name`. This is what wakes an agent |
| **Template** | A YAML file that creates your agents and room in one run |

Switch brings no agents and no models. You bring an agent you already use, and Switch puts it in your team chat. It is open source and free to self-host. You pay for your own agent, so this project needs a Claude subscription or API key.

---

## Following one ask from start to finish

Here is the real line from that run. Yes, I typed it in Hinglish:

```text
@studio-director Driftnote Plus ke liye 30 second launch video banao
```

That means "make a 30 second launch video for Driftnote Plus". Driftnote is a fictional journaling app we use as demo data.

This was an early run, before Voice joined, so you will see four agents below. Voice now sits between Keeper and Cut, and this is the path an ask takes today. Follow the orange line:

![The chain from your ask through Director, Quill, Keeper and Cut to your approval, with Voice before Cut, and an orange branch where Director stops and asks you](https://raw.githubusercontent.com/Nishitbaria/studio-desk/main/docs/blog/chain.png)

**Director** turned it into a brief and tagged Quill. It never writes or renders anything. It only routes and reports.

**Quill** wrote the script. Anything it did not know stayed a placeholder such as `[need: price]`.

**Keeper** checked the script against the brand. It passed, but a placeholder was still there. So Keeper did not call Cut. It called Director.

**Director stopped and tagged me.** That was the message at the top of this post. Cut had not started.

I answered, using `$5` as a test value, and the chain picked itself up. Quill and Keeper finished the script, and Cut rendered the video.

**Keeper checked the render** rather than taking Cut's word for it:

```text
BRAND CHECK | render | Driftnote Plus launch
Verdict: PASS
Issues: None
Next: @studio-director approved render
```

Then Director tagged me with the file, waiting for `approve` or a change. The end of the run, from the project's file times and the chat posts:

```text
2:19 PM  Cut creates the project in renders/driftnote/
2:27 PM  Cut finishes the composition
2:29 PM  Cut renders driftnote.mp4
2:29 PM  Keeper posts BRAND CHECK, Verdict: PASS
2:29 PM  Director tags me with the MP4 path
```

The result was a 30.0 second, 1080x1920 H.264 file of about 800 KB, which I confirmed myself with `ffprobe`. Nothing was published.

---

## The render Keeper sent back

Stopping for a fact is half of it. The other half is refusing work that looks finished.

By the next big run, Voice had joined the team and Cut had moved to Remotion. I asked for a launch video for this very project, in a real Switch room:

```text
@Director 30s launch video for One-Person Studio,
and say how many creators use it
```

Director opened a new room, `video-one-person-studio-launch`, only for this video. Nobody had given the team a creator count, so the placeholder sat right there in Quill's script:

![Quill's post in the Switch room, with a hook option that reads need: creator count](https://raw.githubusercontent.com/Nishitbaria/studio-desk/main/docs/blog/run-need.png)

Then Keeper checked the render. It did not read Cut's report and say fine. It measured the MP4 itself, and it came back with FIX and four exact problems:

![Keeper's FIX in the room, listing four timed issues, followed by Director's status and Cut's re-render](https://raw.githubusercontent.com/Nishitbaria/studio-desk/main/docs/blog/run-fix.png)

Here is what it found, in short:

| When | Problem Keeper found | The rule behind it |
| --- | --- | --- |
| 24.4s to 30s | Four items in the accent color, from pixels sampled in the MP4 | One accent per frame |
| 22.3s to 23.8s | The wordmark climbs in as an outline | Text comes in with a soft fade |
| 0s to 10s | The first two beats share one layout | No two beats share a layout |
| 10s to 22s | Letter spacing of -0.03em on a title | Titles use -0.02em |

Each issue also named the file and the value to change, so Cut had nothing to guess.

Director posted one line, `render FIX 1 of 2`. That count matters: a piece gets two FIX loops, and after that Director asks the person. Agents cannot argue with each other forever.

Cut applied all four fixes and rendered again: 30.02s, 1080x1920, with 4 of 4 voice clips placed. Keeper measured the new file and replied PASS.

![Keeper's PASS in the room, then Director tagging the creator with the MP4 path and waiting](https://raw.githubusercontent.com/Nishitbaria/studio-desk/main/docs/blog/run-pass.png)

Look at the last message. PASS is not approval. Director tags the person with the file and waits. From my ask at 10:10 PM to that tag at 10:24 PM took 14 minutes, and nothing was published.

---

## One stop proves nothing

An agent that always stops is as useless as one that never does. So we ran asks that should behave differently:

| Ask | What the agents found | What they did |
| --- | --- | --- |
| Driftnote Plus launch, 30s | Brand files, but no price, launch date, link or logo files | Asked for all of them, then rendered after the answers |
| A launch for a product with no brand files | No palette, type or tone to follow | Said so and asked before rendering |
| A Driftnote faceless short, asked in the main room | A new video | Opened its own room and started the chain there |

The first two stopped for different reasons, and the third did not need to stop in the main room at all.

---

## The decision that made everything else simple

We have no orchestrator.

There is no script deciding who runs next, no queue and no state machine of ours. Quill ending its message with `@studio-keeper` is the whole handoff. An agent wakes when it is mentioned, reads the room, does its job, and tags the next one.

The routing lives in plain lines in Keeper's instructions:

```text
- PASS on a script with no [need: ...]: @studio-voice make the voice
- PASS on a script with a [need: ...]:
  @studio-director needs the creator's input
- PASS on a render: @studio-director approved render
- FIX on a script: @studio-quill please revise
- FIX on a render: @studio-cut please re-render
```

Look at the second line. That single branch is the stop from the start of this post. It is one sentence of text, and because it runs in a shared room, I can read every decision as it happens.

Each agent is one block in the template:

```yaml
- name: studio-keeper
  display_name: Keeper
  addressing: anyone         # anyone in the room can talk to it
  auto_mode: true
  auto_approve: false        # never bypass tool permission checks
  provider: claude
  machine: "{machine}"
  directory: "{directory}"
  instructions: |
    You are Keeper, the brand guardian for a solo creator.
```

**Take Switch out, and what breaks?** Everything that matters. The agents would be five terminal windows, and I would be pasting a script from one to the next. The stop would have nowhere to happen, because no agent could tag me. And the reasoning would vanish when a session closed. The video engine could be swapped. In fact, we did swap it. The room could not be replaced.

---

## Build it yourself

Switch Console comes with Mattermost, a free chat app, so this is the simplest path. You do not need a Slack workspace or any tokens. After each step, check that it worked before you move on.

**What you need on your machine:**

- [Switch Console](https://docs.switchagents.ai/switch-rooms/getting-started/install-switch-console)
- Docker, which runs Mattermost
- [Claude Code](https://code.claude.com/docs/en/quickstart), signed in
- Node.js 22 or newer
- Optional: Kokoro for the best voice, see `SETUP.md`. Without it, Voice falls back to the macOS voice

Agents use the tools installed on your computer, so install these first. Console reads your PATH once, when it starts.

**Step 1: Start a server.** In Console, choose **Add a server**, then **Run a server on this computer**, and finish the guided setup. Console starts Mattermost and connects it for you.

*Check:* Mattermost is listed under **Messaging apps** on the server's **Home** page with no error.

**Step 2: Sign in to Mattermost.** On that row, select **Sign-in details…** to get your account, then log in.

*Check:* you can see the Mattermost team.

**Step 3: Link your account.** On the same row, select **Link my account…** and choose **This is me**. Do not skip this, because your own agents will not recognize you without it.

*Check:* the row no longer says **No account linked**.

**Step 4: Run the template.** Clone the repo. In Console, open **Templates**, import `agents/studio.template.yaml`, and choose **Use template**:

| Field | What to enter |
| --- | --- |
| Directory | The full path to your clone. Replace anything pre-filled, and check every letter |
| Messaging app | Your Mattermost connection |

*Check:* all five agents introduce themselves in the new channel, and `!agents-status` shows them live.

**Step 5: Ask for a video.** Tag `@studio-director` in every message. Mattermost has no Switch slash commands, so room commands use `!`, and the `!` must be the first thing in the message.

**Step 6: Make it yours.** Send `@studio-director brand intake https://your-site.com`. Keeper reads your site, drafts the brand files, and waits for you to pick a voice.

**Prefer Slack?** It also works. Follow the [Connect Slack guide](https://docs.switchagents.ai/switch-rooms/deploy/messaging-apps/slack), which gives you a Slack app and three values to paste into Console. It uses Socket Mode, so no public URL is needed. My first full run went through Slack.

---

## One room per video

A shared room is powerful, but a video needs its own context. With one room for everything, every video would share one history, and an agent could pick up the wrong script.

So you ask in the main room, and Director opens a new room for that video using Switch's `create_room_from_yaml` tool. Each video gets its own conversation and its own folder.

![The main room leads to Director, who opens a separate room and render folder for each video](https://raw.githubusercontent.com/Nishitbaria/studio-desk/main/docs/blog/rooms.png)

A small template in the repo defines each room:

```yaml
room:
  name: "video-{video}"
  bridge: "{bridge}"
  agents: [studio-director, studio-quill, studio-voice,
           studio-cut, studio-keeper]
  users: ["{$creator}"]
  instructions: |
    Video room for {video}. This room makes that one video.
    Voice and Cut: use {video} as the slug. Voice writes to
    renders/{video}-voice/ and the video builds in renders/{video}/.

kickoff: |
  @studio-director this is the video room for {video}.
  The creator's ask: {ask}
  Post the brief and start the chain.
```

The kickoff matters more than it looks. A new room starts empty and an agent only wakes when mentioned, so without that first message nothing happens. It also carries your ask across, because the new room cannot see the old conversation.

---

## What is enforced, and what is only a rule

This is the part I most want to be honest about.

Some controls are enforced by Switch. With `auto_approve: false`, risky tool calls raise a request instead of running. `addressing` decides who may instruct an agent, and someone who is not allowed gets a visible refusal.

Other rules are only sentences. "Never publish anything" and "only the creator approves" are text that agents read. They are not walls. Our template sets `addressing` to `anyone` so a whole team can work in the room, which means the approval rule depends on those sentences, and on who you let into the room.

![Three columns: what Switch enforces, what instructions ask for, and what you decide](https://raw.githubusercontent.com/Nishitbaria/studio-desk/main/docs/blog/control.png)

A prompt is a request, not a guarantee. So for each rule, ask two questions: what actually stops it being broken, and what happens if it is?

Our worst case is a bad draft video on a local disk. Instructions alone are an acceptable risk for that. If these agents could post to social media, they would not be.

---

## Honest limits

- **The voice depends on your machine.** Voice uses Kokoro if you installed it, then the macOS voice, then no audio at all. It says in the room which one it used, and a missing tool never stops the chain.
- **The Driftnote run used our first render engine, HyperFrames.** Cut has since moved to Remotion, and the One-Person Studio run used that.
- **It runs on Claude Code only.** The template names that provider directly.
- **Finished rooms stay open.** You archive them yourself.
- **Your machine has to stay on.** Agents run on your computer.

---

## What I learned

1. **Decide who decides on day one.** "Facts come from the creator or the brand files" settled most design questions before they became arguments.
2. **Give every agent one job and one exit.** When every message ends by tagging the next agent, a person can read the whole chain.
3. **Build the moment your agent should stop.** The test that convinced us was the one with a missing fact, not the one that went smoothly.
4. **Put the person where being wrong costs the most.** For us, that is missing facts and the final video.
5. **Know which rules are real.** Before you trust a rule, find out what actually enforces it.

---

## What's next

- Post the final MP4 into the room, while keeping the ban on publishing anywhere else
- Build Reel, a planned agent for visuals
- Store each script as a room document, so `!list-documents` shows the work

---

## Try it

Clone [the repo](https://github.com/Nishitbaria/studio-desk), follow `SETUP.md`, and send your first line. If you get stuck, ask in the [WeMakeDevs Discord](https://discord.gg/E2rWw2Yhsm). WeMakeDevs' guide to [building a Switch workflow that finishes a real task](https://www.wemakedevs.org/blogs/how-to-build-a-switch-workflow-that-finishes-a-real-task) taught us a lot too.

If you are building a team of agents, where did you draw the line between what they decide and what a person decides? I would like to hear it in the comments. And if this helped, a star on the [repo](https://github.com/Nishitbaria/studio-desk) is appreciated.

---

## Links

- Demo video: [loom.com/share/2bd581aa44634f069d2b98b29801698e](https://www.loom.com/share/2bd581aa44634f069d2b98b29801698e)
- Live page: [one-person-studio.vercel.app](https://one-person-studio.vercel.app)
- Repo: [github.com/Nishitbaria/studio-desk](https://github.com/Nishitbaria/studio-desk)
- Switch: [github.com/sandbox-quantum/switch](https://github.com/sandbox-quantum/switch)
- Switch quickstart: [docs.switchagents.ai](https://docs.switchagents.ai/switch-rooms/getting-started)
- Connect Mattermost: [Switch docs](https://docs.switchagents.ai/switch-rooms/deploy/messaging-apps/mattermost)
- Connect Slack: [Switch docs](https://docs.switchagents.ai/switch-rooms/deploy/messaging-apps/slack)
- Template reference: [docs/TEMPLATES.md](https://github.com/sandbox-quantum/switch/blob/main/docs/TEMPLATES.md)

*Built on [Switch](https://github.com/sandbox-quantum/switch) with Claude Code. #HowISwitch*
