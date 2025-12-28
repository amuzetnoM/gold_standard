from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone
from discord.ext import commands, tasks

LOG = logging.getLogger("digest_bot.discord.alerting")

QUEUE_THRESHOLD = int(os.getenv("SUBSCRIPTION_QUEUE_THRESHOLD", "10"))
SANITIZER_THRESHOLD = int(os.getenv("SUBSCRIPTION_SANITIZER_THRESHOLD", "1"))
CHECK_INTERVAL = int(os.getenv("SUBSCRIPTION_CHECK_INTERVAL", "60"))


class AlertingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_queue_alert = None
        self._last_sanitizer_alert = None
        self.check_loop.start()

    @tasks.loop(seconds=CHECK_INTERVAL)
    async def check_loop(self):
        try:
            from db_manager import get_db
            db = get_db()
            # Check queue
            qlen = db.get_llm_queue_length()
            # Alert if above threshold and hasn't alerted in last 30 minutes
            if qlen > QUEUE_THRESHOLD:
                if not self._last_queue_alert or (datetime.now(timezone.utc) - self._last_queue_alert) > timedelta(minutes=30):
                    await self._notify_subscribers("queue", f"LLM queue length high: {qlen} pending tasks")
                    self._last_queue_alert = datetime.now(timezone.utc)

            # Check sanitizer corrections in last hour
            corrections = db.get_recent_sanitizer_total(hours=1)
            if corrections >= SANITIZER_THRESHOLD:
                if not self._last_sanitizer_alert or (datetime.now(timezone.utc) - self._last_sanitizer_alert) > timedelta(minutes=30):
                    await self._notify_subscribers("sanitizer", f"Sanitizer corrections (last 1h): {corrections}")
                    self._last_sanitizer_alert = datetime.now(timezone.utc)
        except Exception:
            LOG.exception("Error in alerting check loop")

    async def _notify_subscribers(self, topic: str, message: str):
        from db_manager import get_db
        db = get_db()
        subs = db.list_subscriptions(topic)
        if not subs:
            LOG.info("No subscribers for topic %s", topic)
            return
        for s in subs:
            user_id = int(s["user_id"])
            try:
                user = await self.bot._bot.fetch_user(user_id)
                await user.send(f"[Alert][{topic}] {message}")
            except Exception:
                LOG.exception("Failed to notify subscriber %s for topic %s", user_id, topic)

    @check_loop.before_loop
    async def before_check(self):
        await self.bot._bot.wait_until_ready()


def setup(bot):
    return AlertingCog(bot)
