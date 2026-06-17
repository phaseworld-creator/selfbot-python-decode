"""
Plugin: Message Logger
Logs messages from specified channels/DMs to a file.
"""
import os
from datetime import datetime

class MessageLogger:
    def __init__(self, config):
        self.config = config
        self.log_path = config.get("log_path", "logs/messages.log")
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def is_enabled(self):
        return self.config.get("log_to_file", False)

    async def log(self, message):
        if not self.is_enabled():
            return
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        guild = message.guild.name if message.guild else "DM"
        channel = str(message.channel)
        author = str(message.author)
        content = message.content
        line = f"[{timestamp}] [{guild} / #{channel}] {author}: {content}\n"
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(line)
