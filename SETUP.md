# Setup

Switch does not live in this repo. Switch Console, a desktop app, runs the server for you.

1. Install Switch Console: on macOS, open the `.dmg` and drag it into Applications ([install guide](https://docs.switchagents.ai/switch-rooms/getting-started/install-switch-console.md)).
2. In Console, choose **Add a server**, then **Run a server on this computer** ([add a server](https://docs.switchagents.ai/switch-rooms/getting-started/add-a-server.md)).
3. Finish the guided setup with an agent provider you are already signed in to, such as Claude Code ([getting started](https://docs.switchagents.ai/switch-rooms/getting-started.md)).
4. Check **Gateway > Machines** shows this computer online. If it does not, create one agent by hand under **Agents** on this computer; that enrolls the machine.
5. In **Templates**, import `studio.template.yaml` and choose **Use template**. It asks for nothing: provider and machine default to the first one online.
6. Open the `studio` room. The four agents clone this repo into their own folders and say hello.
7. Paste an ask from [samples/asks.md](samples/asks.md).

## Make it yours

Edit [brand/brand-kit.md](brand/brand-kit.md): your product, the facts agents may use, your voice and your "never say" list, then push. Agents re-read it on every ask.

## Notes

- No messaging app is needed. Without one, the room lives in Switch Console. Docker is only needed for the bundled Mattermost.
- Agents run with `auto_approve: false`, so Console asks you before an agent runs a tool.
- Keys for generation tools go in `.env`, which git ignores. Never commit them.
