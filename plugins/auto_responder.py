"""
Plugin: Auto Responder
Replies to messages matching keywords.
"""

class AutoResponder:
    def __init__(self, client, config):
        self.client = client
        self.config = config

    def is_enabled(self):
        return self.config.get("auto_responder", {}).get("enabled", False)

    async def handle(self, message):
        if not self.is_enabled():
            return
        if message.author == self.client.user:
            return
        cfg = self.config.get("auto_responder", {})
        responses = cfg.get("responses", {})
        content_lower = message.content.lower()
        for keyword, reply in responses.items():
            if keyword.lower() in content_lower:
                await message.channel.send(reply)
                print(f"[AutoResponder] Replied to '{keyword}' in {message.channel}")
                break
