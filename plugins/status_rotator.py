"""
Plugin: Status Rotator
Cycles through custom statuses at a set interval.
"""
import asyncio
import discord

class StatusRotator:
    def __init__(self, client, config):
        self.client = client
        self.config = config
        self.running = False
        self.task = None

    async def start(self):
        cfg = self.config.get("status_rotator", {})
        if not cfg.get("enabled"):
            return
        self.running = True
        self.task = asyncio.create_task(self._loop())
        print("[StatusRotator] Started.")

    async def stop(self):
        self.running = False
        if self.task:
            self.task.cancel()
        print("[StatusRotator] Stopped.")

    async def _loop(self):
        cfg = self.config.get("status_rotator", {})
        statuses = cfg.get("statuses", [])
        interval = cfg.get("interval", 10)
        i = 0
        while self.running:
            if not statuses:
                await asyncio.sleep(interval)
                continue
            s = statuses[i % len(statuses)]
            activity_type = {
                "playing": discord.ActivityType.playing,
                "listening": discord.ActivityType.listening,
                "watching": discord.ActivityType.watching,
                "competing": discord.ActivityType.competing,
            }.get(s.get("type", "playing"), discord.ActivityType.playing)
            activity = discord.Activity(type=activity_type, name=s["text"])
            await self.client.change_presence(activity=activity)
            print(f"[StatusRotator] Status → {s['text']}")
            i += 1
            await asyncio.sleep(interval)
