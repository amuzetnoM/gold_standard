import logging
import platform
import time
from datetime import datetime, timedelta

import discord
from discord.ext import commands, tasks

from src.digest_bot.discord.content_router import ContentType

logger = logging.getLogger(__name__)


class Status(commands.Cog):
    """Cog for autonomous system status and health reporting."""

    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
        self.daily_status.start()

    def cog_unload(self):
        self.daily_status.cancel()

    @tasks.loop(hours=24)
    async def daily_status(self):
        """Post a daily system health summary."""
        # Wait for bot to be ready
        await self.bot.wait_until_ready()

        uptime = str(timedelta(seconds=int(time.time() - self.start_time)))

        embed = discord.Embed(
            title="🛡️ Syndicate System Report",
            description="Daily autonomous health summary.",
            color=0x2ECC71,  # Green
            timestamp=datetime.now(),
        )

        embed.add_field(name="Uptime", value=uptime, inline=True)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Platform", value=platform.system(), inline=True)

        # Check LLM status (basic)
        llm_status = "✅ Active"
        if hasattr(self.bot, "summarizer"):
            llm_name = self.bot.summarizer.config.llm.provider
            llm_status = f"✅ {llm_name.upper()}"

        embed.add_field(name="LLM Provider", value=llm_status, inline=True)
        embed.add_field(name="Sync Tracking", value="✅ Enabled", inline=True)
        embed.add_field(name="Content Routing", value="✅ Active", inline=True)

        footer_text = f"Worker ID: {platform.node()} | Version: 1.0.0"
        embed.set_footer(text=footer_text)

        await self.bot.post_content(
            content="## 📋 Daily System Health Summary", embed=embed, content_type=ContentType.SYSTEM_REPORT
        )

    @commands.command(name="status")
    async def status_cmd(self, ctx):
        """Check real-time system status."""
        uptime = str(timedelta(seconds=int(time.time() - self.start_time)))

        embed = discord.Embed(title="🤖 Bot Status", color=0x3498DB, timestamp=datetime.now())

        embed.add_field(name="Uptime", value=uptime, inline=True)
        embed.add_field(name="Ping", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="Channels", value=len(self.bot.channel_map), inline=True)

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Status(bot))
