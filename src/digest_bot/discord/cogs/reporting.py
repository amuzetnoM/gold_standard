from __future__ import annotations

import logging
import os
from discord.ext import commands, tasks

LOG = logging.getLogger("digest_bot.discord.reporting")

class ReportingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_id = os.getenv("DISCORD_OPS_CHANNEL_ID")
        # Background task optional; disabled unless env set
        if os.getenv("DISCORD_ENABLE_DAILY_REPORT") == "1":
            self.daily_report.start()

    @tasks.loop(hours=24)
    async def daily_report(self):
        # Placeholder: call the same report generation used by `daily_report.py`
        try:
            from ..daily_report import build_report
            from db_manager import DatabaseManager
            db = DatabaseManager()
            msg = build_report(db)
            if self.channel_id:
                ch = await self.bot._bot.fetch_channel(int(self.channel_id))
                await ch.send(msg)
            else:
                LOG.warning("DISCORD_OPS_CHANNEL_ID not set; skipping daily report post")
        except Exception:
            LOG.exception("Failed to send daily report")

    @daily_report.before_loop
    async def before_daily_report(self):
        # Wait until the bot is ready
        await self.bot._bot.wait_until_ready()

    @commands.command(name="report")
    @commands.has_role("operators")
    async def cmd_report(self, ctx, hours: int = 24):
        """Generate a short report and post into the channel (role: operators)."""
        from ..daily_report import build_report
        from db_manager import DatabaseManager
        db = DatabaseManager()
        msg = build_report(db, hours=hours)
        await ctx.send(msg)

def setup(bot):
    return ReportingCog(bot)
