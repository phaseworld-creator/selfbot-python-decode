"""
Plugin: Webhook Notifier
Sends Discord webhook notifications for events.
"""
import aiohttp
from datetime import datetime

class WebhookNotifier:
    def __init__(self, config):
        self.webhook_url = config.get("webhook_url", "")

    def is_enabled(self):
        return bool(self.webhook_url)

    async def send(self, title, description, color=0x5865F2):
        if not self.is_enabled():
            return
        payload = {
            "embeds": [{
                "title": title,
                "description": description,
                "color": color,
                "footer": {"text": "PhaseWorld Selfbot"},
                "timestamp": datetime.utcnow().isoformat()
            }]
        }
        async with aiohttp.ClientSession() as session:
            await session.post(self.webhook_url, json=payload)

    async def on_dm(self, message):
        await self.send(
            "📬 New DM",
            f"**From:** {message.author}\n**Message:** {message.content}",
            color=0x57F287
        )

    async def on_mention(self, message):
        guild = message.guild.name if message.guild else "DM"
        await self.send(
            "🔔 You were mentioned",
            f"**Server:** {guild}\n**Channel:** #{message.channel}\n**By:** {message.author}\n**Message:** {message.content}",
            color=0xFEE75C
        )
