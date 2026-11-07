# Connect Slack

This guide takes you from a fresh clone to the studio agents answering in a Slack channel, on macOS or Windows. Slack uses Socket Mode, so it works from a laptop with no public URL.

The full chain was run through Slack on Windows on 2026-11-07, from a one-line ask to a rendered MP4. The steps are the same on macOS, but that exact run has not been repeated there.

## Before you start

Install everything in [SETUP.md](../SETUP.md#requirements) first. The agents run on your computer and use the tools installed there.

You also need:

- A Slack workspace where you can install a custom app. Many workspaces need admin approval first.
- An admin account on the Switch server. You have one if Switch Console set up the server.

## Step 1: Create the Slack app

1. Open [api.slack.com/apps](https://api.slack.com/apps) and select **Create New App**, then **From an app manifest**.
2. Choose your workspace and select **JSON**.
3. Paste the manifest below and create the app.

If your workspace has guests, delete the whole `agent_view` block before you paste. Otherwise guests are blocked from the app and direct messages become threads, and neither can be undone. Switch does not use that block.

Leave `socket_mode_enabled` set to `true`. That setting is why no public URL is needed.

```json
{
    "display_information": {
        "name": "Agent Switch"
    },
    "features": {
        "app_home": {
            "home_tab_enabled": true,
            "messages_tab_enabled": false,
            "messages_tab_read_only_enabled": false
        },
        "bot_user": {
            "display_name": "Agent Switch",
            "always_online": false
        },
        "agent_view": {
            "agent_description": "Switch agents. Mention one by name in a channel and it answers there; its progress appears on the message while it works."
        },
        "slash_commands": [
            { "command": "/help", "description": "Show the list of available in-room commands", "should_escape": false },
            { "command": "/reset", "description": "Reset a targeted agent's session (clears context, then reconnects)", "usage_hint": "@agent-name | @role (required)", "should_escape": true },
            { "command": "/reset-all-agents", "description": "Reset EVERY agent's session in this room", "should_escape": false },
            { "command": "/compact", "description": "Compact a targeted agent's session context", "usage_hint": "@agent-name | @role (required)", "should_escape": true },
            { "command": "/compact-all-agents", "description": "Compact EVERY agent's session context in this room", "should_escape": false },
            { "command": "/interrupt", "description": "Interrupt a targeted agent's current turn", "usage_hint": "@agent-name | @role (required)", "should_escape": true },
            { "command": "/interrupt-all-agents", "description": "Interrupt EVERY agent's current turn in this room", "should_escape": false },
            { "command": "/agents-status", "description": "Show each agent's presence and capabilities in this room", "should_escape": false },
            { "command": "/roles", "description": "List this room's roles and who currently holds each", "should_escape": false },
            { "command": "/list-agents", "description": "List the agents available in this room", "should_escape": false },
            { "command": "/list-switch-agents", "description": "List all agents registered on the Switch", "should_escape": false },
            { "command": "/list-documents", "description": "List the room's internal documents", "should_escape": false },
            { "command": "/list-references", "description": "List the room's references", "should_escape": false },
            { "command": "/list-aliases", "description": "List per-room agent aliases (@alias to agent)", "should_escape": false },
            { "command": "/set-alias", "description": "Give an agent a room alias", "usage_hint": "@agent-name @alias", "should_escape": true },
            { "command": "/remove-alias", "description": "Remove a room alias", "usage_hint": "@alias (or @agent-name)", "should_escape": true },
            { "command": "/invite-agent", "description": "Add an existing agent to this room", "usage_hint": "@agent-name", "should_escape": true },
            { "command": "/run-cmd", "description": "Show the terminal command to start a session for an agent", "usage_hint": "@agent-name [@role]", "should_escape": true },
            { "command": "/agents-greet", "description": "Have agents in the room introduce themselves", "should_escape": false },
            { "command": "/room-url", "description": "Show the frontend URL for this room", "should_escape": false }
        ]
    },
    "oauth_config": {
        "scopes": {
            "bot": [
                "files:read",
                "files:write",
                "assistant:write",
                "channels:history",
                "channels:manage",
                "channels:read",
                "chat:write",
                "chat:write.customize",
                "commands",
                "groups:history",
                "groups:read",
                "groups:write",
                "im:history",
                "im:read",
                "im:write",
                "mpim:history",
                "reactions:read",
                "reactions:write",
                "users:read",
                "usergroups:read",
                "usergroups:write"
            ]
        },
        "pkce_enabled": false
    },
    "settings": {
        "event_subscriptions": {
            "bot_events": [
                "app_home_opened",
                "message.channels",
                "message.groups",
                "message.im",
                "message.mpim"
            ]
        },
        "interactivity": {
            "is_enabled": true
        },
        "org_deploy_enabled": false,
        "socket_mode_enabled": true,
        "token_rotation_enabled": false,
        "is_mcp_enabled": false
    }
}
```

Source: [Connect Slack](https://docs.switchagents.ai/switch-rooms/deploy/messaging-apps/slack.md) in the Switch docs. Check there for the latest manifest.

## Step 2: Get the three values

Collect these from Slack. The two tokens are secrets: paste them only into Switch Console, never into this repo, `.env` or chat.

| Value | Where to find it | Starts with |
| --- | --- | --- |
| Bot token | Your app, then **Install App**. Install it first, then copy **Bot User OAuth Token** | `xoxb-` |
| App-level token | Your app, then **Basic Information**, then **App-Level Tokens**. Generate one with the `connections:write` scope | `xapp-` |
| Workspace ID | Open Slack in a browser. The URL is `app.slack.com/client/T.../C...`; copy only the `T...` part | `T` |

## Step 3: Connect Slack in Switch Console

1. In the sidebar switcher, select your server and open its **Home** page.
2. Under **Messaging apps**, select **Connect**, then choose **Slack**.
3. Set **Name** to `Studio Slack`. You will type this exact name again in step 4.
4. Paste the bot token, app-level token and workspace ID.
5. Leave **Allow creating channels from Switch** on, so the template can create the channel.
6. Choose **Agent name autocomplete** now, because you cannot change it later in Console or the Gateway. It needs a paid Slack plan. Without it, you can still type agent names by hand.
7. Select **Connect**. Switch rejects a bad token straight away.
8. When asked which Slack account is yours, search for your name, handle or email, then select **This is me**.

Do not skip step 8. The template adds you to the room through this linked account, and your agents will not recognize you as their owner without it.

To confirm, check that the connection shows under **Messaging apps** on the **Home** page with no red error.

## Step 4: Run the studio template

1. Pull the latest `main`.
2. In Console, open **Your Agents** and delete any existing `studio-*` agents. Switch refuses a name already in use.
3. Open **Templates**, select **Import template**, paste `agents/studio.template.yaml`, then select **Import** and **Save**.
4. Select **Use template** and fill in the form.
5. Select **Create all**.

| Field | Enter |
| --- | --- |
| Directory | The full path to your clone, for example `C:/Users/you/studio-desk` or `/Users/you/studio-desk`. Check every letter: a typo still creates the agents, but they will not start |
| Messaging app | `Studio Slack`, exactly as you named it in step 3. Do not leave it empty unless this connection is marked as the default |

## Step 5: Confirm it works

1. Open the new Slack channel. Its name starts with `studio-studio`.
2. Check that all four agents posted a one-line intro. If they did not, run `/agents-greet`.
3. Run `/agents-status` to see that all four are in the room.
4. Send this message, tagging Director:

```text
@studio-director Driftnote Plus ke liye 30 second launch video banao
```

It passes if Director posts a brief and tags Quill, then Quill and Keeper run. The team then stops and asks you for missing facts. Answer with `@studio-director`, and Cut renders the video into `renders/<slug>/`.

Tag `@studio-director` in every message you send, and spell it exactly, because a typo looks like an agent ignoring you. Cut may ask for approval in Console during a render, so keep Console open.

## Troubleshooting

| What you see | Cause | Fix |
| --- | --- | --- |
| "names users (Admin), and it is on no messaging app" | **Messaging app** was empty and no connection is the default | Enter `Studio Slack` in the form. Nothing was created, so retry |
| "Unknown bridge" | The name does not match the connection | Copy the exact name from the **Home** page. It is case-sensitive |
| Name already in use | Old `studio-*` agents still exist | Delete them, then run the template again |
| Agents exist but nobody replies | The directory path may be wrong; the Console log says "does not exist on this machine" | Fix **Directory** on each agent's page, or recreate the agents |
| A second channel like `studio-studio-607850c5` | The old channel kept the name | Use the new channel. Delete the old one in Slack to free the name; archiving does not free it |
| "This chat account isn't linked" | Your Slack account is not linked | Open the server's **Home** page and select **Link my account** |
| Cut's render fails on FFmpeg or FFprobe | FFmpeg is not installed, or Console started before it was | Install FFmpeg, then fully quit and reopen Console |
| Bad token error on Connect | The wrong token is in a field | `xoxb-` goes in Bot Token, `xapp-` goes in App-level token |

Disconnecting Slack later deletes every Switch room on that connection, with its history. You cannot undo it.
