from __future__ import annotations

import logging
from discord.ext import commands

LOG = logging.getLogger("digest_bot.discord.sanitizer_alerts")

class SanitizerAlertsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def post_sanitizer_alert(self, summary: str):
        # Find ops channel and post; this is a small helper for other parts of the system
        channel_id = __import__('os').getenv('DISCORD_OPS_CHANNEL_ID')
        if not channel_id:
            LOG.warning("No ops channel configured; skipping sanitizer alert")
            return
        ch = await self.bot._bot.fetch_channel(int(channel_id))
        await ch.send(f"[Sanitizer] {summary}")

    @commands.command(name="sanitizer_audits")
    @commands.has_role("operators")
    async def cmd_sanitizer_audits(self, ctx, limit: int = 10):
        """Show recent sanitizer audits (role: operators)."""
        from db_manager import DatabaseManager
        db = DatabaseManager()
        with db._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, task_id, corrections, notes, created_at FROM llm_sanitizer_audit ORDER BY created_at DESC LIMIT ?", (limit,))
            rows = cur.fetchall()
        lines = [f"id={r['id']} task={r['task_id']} corrections={r['corrections']} @ {r['created_at']} notes={r['notes']}" for r in rows]
        if not lines:
            await ctx.send("No sanitizer audits found")
        else:
            # Chunk to avoid message length thresholds
            await ctx.send("\n".join(lines[:10]))

def setup(bot):
    return SanitizerAlertsCog(bot)
