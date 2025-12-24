from __future__ import annotations

import logging
import os
try:
    import discord
    from discord.ext import commands
    from discord import ButtonStyle
    from discord.ui import View
except Exception:
    # Provide lightweight fallbacks for environments without discord.py to allow test collection
    discord = None

    class ButtonStyle:
        green = "green"
        grey = "grey"
        blurple = "blurple"

    class View:
        def __init__(self, *args, **kwargs):
            pass

    class _DummyUI:
        @staticmethod
        def button(label=None, style=None):
            def decorator(fn):
                return fn

            return decorator

    # A minimal 'commands' stub with required decorators and Cog base class
    class _DummyCommands:
        class Cog:
            pass

        @staticmethod
        def command(name=None):
            def decorator(fn):
                return fn

            return decorator

        @staticmethod
        def has_role(role_name):
            def decorator(fn):
                return fn

            return decorator

    commands = _DummyCommands()

    # Provide a small ui namespace compatible with usage: discord.ui.button
    class _DummyDiscord:
        ui = _DummyUI()

    discord = _DummyDiscord()

LOG = logging.getLogger("digest_bot.discord.digest_workflow")

class ApproveView(View):
    def __init__(self, task_id: int, author_id: int):
        super().__init__(timeout=None)
        self.task_id = task_id
        self.author_id = author_id

    @discord.ui.button(label="Approve", style=ButtonStyle.green)
    async def approve(self, button, interaction):
        # Only operators may approve; ensure role check
        if "operators" not in [r.name for r in interaction.user.roles]:
            await interaction.response.send_message("You are not authorized to approve.", ephemeral=True)
            return
        from db_manager import get_db
        db = get_db()

        # Enforce sanitizer checks: ensure no corrections recorded for this task
        with db._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT SUM(corrections) as total FROM llm_sanitizer_audit WHERE task_id = ?", (self.task_id,))
            row = cur.fetchone()
            corrections = int(row["total"] or 0)
        if corrections > 0:
            await interaction.response.send_message(
                f"Task {self.task_id} has {corrections} sanitizer corrections and cannot be approved. Please review or re-run.",
                ephemeral=True,
            )
            db.save_bot_audit(str(interaction.user), "approve_failed", f"task={self.task_id} corrections={corrections}")
            return

        # Mark approved and audit
        ok = db.approve_llm_task(self.task_id, str(interaction.user))
        if ok:
            await interaction.response.send_message(f"Task {self.task_id} approved and marked completed by {interaction.user}")
        else:
            await interaction.response.send_message(f"Failed to approve task {self.task_id}", ephemeral=True)

    @discord.ui.button(label="Flag", style=ButtonStyle.grey)
    async def flag(self, button, interaction):
        if "operators" not in [r.name for r in interaction.user.roles]:
            await interaction.response.send_message("You are not authorized to flag.", ephemeral=True)
            return
        from db_manager import get_db
        db = get_db()
        db.save_bot_audit(str(interaction.user), "flag", f"task={self.task_id}")
        await interaction.response.send_message(f"Task {self.task_id} flagged for review by {interaction.user}")

    @discord.ui.button(label="Re-run", style=ButtonStyle.blurple)
    async def rerun(self, button, interaction):
        if "operators" not in [r.name for r in interaction.user.roles]:
            await interaction.response.send_message("You are not authorized to rerun.", ephemeral=True)
            return
        from db_manager import get_db
        db = get_db()
        # Copy task and insert new pending task
        with db._get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT document_path, prompt FROM llm_tasks WHERE id = ?", (self.task_id,))
            row = cur.fetchone()
            if not row:
                await interaction.response.send_message("Task not found", ephemeral=True)
                return
            cur.execute("INSERT INTO llm_tasks (document_path, prompt, provider_hint, status) VALUES (?, ?, ?, 'pending')", (row['document_path'], row['prompt'], None))
        db.save_bot_audit(str(interaction.user), "rerun", f"task={self.task_id}")
        await interaction.response.send_message(f"Task {self.task_id} re-enqueued by {interaction.user}")


class DigestWorkflowCog(commands.Cog):
    """Cog that exposes operator-facing workflows around digests."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="digest_full")
    @commands.has_role("operators")
    async def cmd_digest_full(self, ctx, period: int = 24):
        """Generate a full digest and post to channel with approval UI (operators only)."""
        from ..daily_report import build_structured_report
        from ..discord import templates as discord_templates
        from db_manager import DatabaseManager
        db = DatabaseManager()
        # Build structured report and render embed
        structured = build_structured_report(db, hours=period)
        embed_dict = discord_templates.build_daily_embed(structured)

        # Convert to discord.Embed if library is available
        embed_obj = None
        try:
            if hasattr(discord, 'Embed'):
                embed_obj = discord.Embed.from_dict(embed_dict)
        except Exception:
            embed_obj = None

        # Create a synthetic task id for UI actions if not tied to an existing task
        task_id = 0
        view = ApproveView(task_id, ctx.author.id)
        if embed_obj is not None:
            await ctx.send(embed=embed_obj, view=view)
        else:
            # Fallback to plaintext
            await ctx.send(discord_templates.plain_daily_text(structured), view=view)


def setup(bot):
    return DigestWorkflowCog(bot)
