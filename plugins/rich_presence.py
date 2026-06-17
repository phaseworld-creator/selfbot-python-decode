"""
Plugin: Rich Presence Customizer
"""
import discord

class RichPresence:
    def __init__(self, client, config):
        self.client = client
        self.config = config

    async def apply(self):
        cfg = self.config.get("rich_presence", {})
        if not cfg.get("enabled"):
            return
        name    = cfg.get("name", "My App") or "My App"
        details = cfg.get("details", "") or None
        state   = cfg.get("state", "") or None

        activity = discord.Activity(
            type=discord.ActivityType.playing,
            name=name,
            details=details,
            state=state,
        )
        await self.client.change_presence(activity=activity)
        print(f"[RichPresence] Applied: {name}")