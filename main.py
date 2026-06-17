"""
PhaseWorld Selfbot - Main Entry Point
Loads config, validates license, starts plugins.
"""
import discord
import json
import os
import sys

# ── Load config ───────────────────────────────────────────────
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config/config.json")

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_config(cfg):

    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)

config = load_config()

# ── Import plugins ────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))
from plugins.status_rotator import StatusRotator
from plugins.auto_responder import AutoResponder
from plugins.logger import MessageLogger
from plugins.afk import AFKPlugin
from plugins.webhook_notifier import WebhookNotifier
from plugins.rich_presence import RichPresence

# ── Client ────────────────────────────────────────────────────
client = discord.Client()

# Attach plugins
client._rotator = StatusRotator(client, config)
client._auto_responder = AutoResponder(client, config)
client._logger = MessageLogger(config)
client._afk = AFKPlugin(client, config)
client._webhook = WebhookNotifier(config)
client._rpc = RichPresence(client, config)

async def _plugin_handler(message):
    await client._auto_responder.handle(message)
    await client._logger.log(message)
    await client._afk.handle(message)
    # Webhook: DM notifications
    if isinstance(message.channel, discord.DMChannel):
        if message.author != client.user:
            await client._webhook.on_dm(message)
    # Webhook: mention notifications
    if client.user in message.mentions and message.author != client.user:
        await client._webhook.on_mention(message)

client._plugin_handler = _plugin_handler

# Load selfbot commands
from scripts.selfbot_commands import setup_selfbot_commands
setup_selfbot_commands(client, config)

@client.event
async def on_ready():
    print(f"[PhaseWorld] Logged in as {client.user}")
    await client._rotator.start()
    await client._rpc.apply()

if __name__ == "__main__":
    token = config.get("token")
    if not token or token == "YOUR_USER_TOKEN_HERE":
        print("[ERROR] No user token set in config/config.json")
        sys.exit(1)
    client.run(token)
