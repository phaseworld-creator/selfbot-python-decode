"""
Plugin: AFK
Replies to anyone who pings you while AFK is enabled.
"""

class AFKPlugin:
    def __init__(self, client, config):
        self.client = client
        self.config = config
        self.enabled = False
        self.message = "I'm AFK right now, I'll be back soon."

    def set(self, enabled, message=None):
        self.enabled = enabled
        if message:
            self.message = message

    async def handle(self, message):
        if not self.enabled:
            return
        if message.author == self.client.user:
            return
        if self.client.user in message.mentions:
            await message.channel.send(f"💤 **AFK** | {self.message}")
            print(f"[AFK] Replied to {message.author}")
