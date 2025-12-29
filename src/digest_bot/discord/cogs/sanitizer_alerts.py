from __future__ import annotations

import logging

from discord.ext import commands

from src.digest_bot.discord.content_router import ContentType

LOG = logging.getLogger("digest_bot.discord.sanitizer_alerts")


class SanitizerAlertsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def post_sanitizer_alert(self, summary: str):
        """Post a sanitizer alert using the content router."""
        # Route to SYSTEM_ERROR which goes to bot-logs/admin channels
        await self.bot.post_content(f"[Sanitizer] {summary}", content_type=ContentType.SYSTEM_ERROR)

    @commands.command(name="sanitizer_audits")
    @commands.has_role("operators")
    async def cmd_sanitizer_audits(self, ctx, limit: int = 10):
        """Show recent sanitizer audits (role: operators)."""
        from db_manager import DatabaseManager

        db = DatabaseManager()
        with db._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, task_id, corrections, notes, created_at FROM llm_sanitizer_audit ORDER BY created_at DESC LIMIT ?",
                (limit,),
            )
            rows = cur.fetchall()
        lines = [
            f"id={r['id']} task={r['task_id']} corrections={r['corrections']} @ {r['created_at']} notes={r['notes']}"
            for r in rows
        ]
        if not lines:
            await ctx.send("No sanitizer audits found")
        else:
            # Chunk to avoid message length thresholds
            await ctx.send("\n".join(lines[:10]))


def setup(bot):
    return SanitizerAlertsCog(bot)
