from __future__ import annotations

import logging
import os

from discord.ext import commands, tasks

from src.digest_bot.discord.content_router import ContentType

LOG = logging.getLogger("digest_bot.discord.reporting")


class ReportingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Prefer a dedicated digest channel if present
        self.channel_id = os.getenv("DISCORD_DIGEST_CHANNEL_ID") or os.getenv("DISCORD_OPS_CHANNEL_ID")
        # Background task optional; disabled unless env set
        if os.getenv("DISCORD_ENABLE_DAILY_REPORT") == "1":
            self.daily_report.start()

    @tasks.loop(hours=24)
    async def daily_report(self):
        """Generate and post the daily report using the content router."""
        try:
            from db_manager import DatabaseManager

            from ..daily_report import build_report

            db = DatabaseManager()
            msg = build_report(db)

            # Use the bot's post_content method which handles routing
            await self.bot.post_content(msg, content_type=ContentType.DIGEST)
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
        from db_manager import DatabaseManager

        from ..daily_report import build_report

        db = DatabaseManager()
        msg = build_report(db, hours=hours)
        await ctx.send(msg)


def setup(bot):
    return ReportingCog(bot)
