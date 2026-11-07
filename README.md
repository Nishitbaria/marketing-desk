# Creator crew (working title)

A crew of AI agents for creators, built on [Switch](https://github.com/sandbox-quantum/switch) for the WeMakeDevs "Flip the Switch" hackathon. Coming up with ideas and writing content is the hard part. AI writes well only when it is instructed completely, so every agent here works from one detailed brief of the creator's voice and audience.

## The problem

_To write._

## The crew

_Agents are added one by one. See [agents/](agents/)._

## Why Switch

_To write._

## Try it in 2 minutes

_To write: import the template, use the sample inputs, no accounts needed._

## Full setup

Switch itself does not live in this repo. Switch Console, a desktop app, runs the server for you.

1. Install Switch Console: on macOS, open the `.dmg` and drag it into Applications ([install guide](https://docs.switchagents.ai/switch-rooms/getting-started/install-switch-console.md)).
2. In Console, choose **Add a server**, then **Run a server on this computer** ([add a server](https://docs.switchagents.ai/switch-rooms/getting-started/add-a-server.md)).
3. Finish the guided setup with an agent provider you are already signed in to, such as Claude Code ([getting started](https://docs.switchagents.ai/switch-rooms/getting-started.md)).
4. Fill in [docs/creator-brief.md](docs/creator-brief.md).
5. Import the template from [switch/](switch/) and choose **Use template**.

Docker is only needed for the bundled Mattermost. Without it the room still works inside Switch Console.

## How it works

_To write._

## Safety

- Agents draft. Nothing is posted anywhere without the creator.
- Keys go in `.env`, which git ignores. Never commit them.

## What's in the repo

| Path | What it holds |
|---|---|
| `agents/` | One instruction file per agent |
| `switch/` | The Switch template that creates the crew and its room |
| `samples/` | Fictional demo inputs |
| `docs/` | Creator brief, hackathon rules, how Switch works |
| `demo/` | Screenshots, video script, run transcript |

## Limits

_To write._
