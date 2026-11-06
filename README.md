# Flip the Switch hackathon

Our project for the WeMakeDevs "Flip the Switch" hackathon, built on [Switch](https://github.com/sandbox-quantum/switch).

## Local setup

Switch itself does not live in this repo. Switch Console, a desktop app, runs the server for you.

1. Install and start [Docker](https://docs.docker.com/get-started/get-docker/). Without it, the local server has no bundled Mattermost ([troubleshooting](https://docs.switchagents.ai/switch-rooms/resources/troubleshooting.md)).
2. Install Switch Console: on macOS, open the `.dmg` and drag it into Applications ([install guide](https://docs.switchagents.ai/switch-rooms/getting-started/install-switch-console.md)).
3. In Console, choose **Add a server**, then **Run a server on this computer** ([add a server](https://docs.switchagents.ai/switch-rooms/getting-started/add-a-server.md)).
4. Finish the guided setup with an agent provider you are already signed in to, such as Claude Code ([getting started](https://docs.switchagents.ai/switch-rooms/getting-started.md)).

## Secrets

Keep keys in `.env`, which is ignored by git. Never commit them.
