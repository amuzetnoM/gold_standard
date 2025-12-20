from __future__ import annotations

import logging
from discord.ext import commands

LOG = logging.getLogger("digest_bot.discord.moderation")

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="flagged")
    @commands.has_role("operators")
    async def cmd_flagged(self, ctx, limit: int = 20):
        """List flagged tasks (role: operators)."""
        from db_manager import DatabaseManager
        db = DatabaseManager()
        with db._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, document_path, status, completed_at FROM llm_tasks WHERE status = 'flagged' ORDER BY completed_at DESC LIMIT ?", (limit,))
            rows = cur.fetchall()
        if not rows:
            await ctx.send("No flagged tasks")
            return
        lines = [f"id={r['id']} path={r['document_path']} completed_at={r['completed_at']}" for r in rows]
        await ctx.send("\n".join(lines))

    @commands.command(name="unflag")
    @commands.has_role("operators")
    async def cmd_unflag(self, ctx, task_id: int):
        """Clear flagged status for a task (role: operators)."""
        from db_manager import get_db
        db = get_db()
        db.update_llm_task_result(task_id, status='completed')
        await ctx.send(f"Task {task_id} unflagged and marked completed")

    @commands.command(name="rerun")
    @commands.has_role("operators")
    async def cmd_rerun(self, ctx, task_id: int):
        """Re-enqueue a task for reprocessing."""
        from db_manager import get_db
        db = get_db()
        # Basic re-enqueue pattern: copy prompt and create a new pending task
        with db._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT document_path, prompt FROM llm_tasks WHERE id = ?", (task_id,))
            row = cur.fetchone()
            if not row:
                await ctx.send(f"Task {task_id} not found")
                return
            cur.execute("INSERT INTO llm_tasks (document_path, prompt, provider_hint, status) VALUES (?, ?, ?, 'pending')", (row['document_path'], row['prompt'], None))
        await ctx.send(f"Task {task_id} re-enqueued")


def setup(bot):
    return ModerationCog(bot)
