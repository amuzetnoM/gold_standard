from __future__ import annotations

import logging
from discord.ext import commands

LOG = logging.getLogger("digest_bot.discord.subscriptions")

ALLOWED_TOPICS = {"sanitizer", "queue", "digests"}

class SubscriptionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="subscribe")
    async def cmd_subscribe(self, ctx, topic: str):
        """Subscribe to a topic: sanitizer|queue|digests"""
        topic = topic.lower()
        if topic not in ALLOWED_TOPICS:
            await ctx.send(f"Unknown topic. Allowed: {', '.join(sorted(ALLOWED_TOPICS))}")
            return
        from db_manager import get_db
        db = get_db()
        uid = str(ctx.author.id)
        sid = db.add_subscription(uid, topic)
        await ctx.send(f"Subscribed {ctx.author.mention} to `{topic}` (id={sid})")

    @commands.command(name="unsubscribe")
    async def cmd_unsubscribe(self, ctx, topic: str):
        topic = topic.lower()
        if topic not in ALLOWED_TOPICS:
            await ctx.send(f"Unknown topic. Allowed: {', '.join(sorted(ALLOWED_TOPICS))}")
            return
        from db_manager import get_db
        db = get_db()
        uid = str(ctx.author.id)
        ok = db.remove_subscription(uid, topic)
        await ctx.send(f"Unsubscribed {ctx.author.mention} from `{topic}`" if ok else f"You were not subscribed to `{topic}`")

    @commands.command(name="subscriptions")
    async def cmd_list(self, ctx):
        from db_manager import get_db
        db = get_db()
        uid = str(ctx.author.id)
        topics = db.get_user_subscriptions(uid)
        if not topics:
            await ctx.send("You have no subscriptions. Use `/subscribe <topic>` to get alerts.")
        else:
            await ctx.send(f"Your subscriptions: {', '.join(topics)}")

    @commands.command(name="list_subscribers")
    @commands.has_role("Digest Moderator")
    async def cmd_list_subscribers(self, ctx, topic: str = None):
        from db_manager import get_db
        db = get_db()
        subs = db.list_subscriptions(topic=topic)
        if not subs:
            await ctx.send("No subscribers for that topic")
            return
        lines = [f"user_id={s['user_id']} topic={s['topic']} since={s['created_at']}" for s in subs[:40]]
        await ctx.send("\n".join(lines))


def setup(bot):
    return SubscriptionsCog(bot)
