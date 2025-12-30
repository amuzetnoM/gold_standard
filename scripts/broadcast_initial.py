import os

import discord
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

MESSAGES = {
    "🚨-alerts": """**📌 ALERT STREAM**
*Critical Market Notifications*

*   **Topic:** ⚠️ Important market alerts and notifications. Configure your notification settings!
*   **Purpose:** Real-time urgent alerts.""",
    "📊-daily-digests": """**📌 QUANTITATIVE INTELLIGENCE STREAM**
*Automated Market Analysis & Insights*

*   **Topic:** ⚡ QUANTITATIVE INTELLIGENCE STREAM. Automated daily market analysis and institutional flow monitoring.
*   **Content:** Market direction, key levels, and institutional flow.""",
    "📈-premarket-plans": """**📌 PRE-MARKET STRATEGY**
*Session Preparation*

*   **Topic:** 🛡️ PRE-MARKET STRATEGY. Key levels, institutional bias, and critical invalidation triggers for the session ahead.
*   **Timing:** Posted before market open.""",
    "📔-trading-journal": """**📌 EXECUTOR JOURNAL**
*Performance Tracking*

*   **Topic:** 📔 EXECUTOR JOURNAL. Transparent record of trade execution, PnL tracking, and algorithmic performance review.
*   **Format:** Review of executed trades.""",
    "📈-day-charts": """**📌 CHART FEED**
*Visual Intelligence*

*   **Topic:** 📊 Daily charts and visualizations (auto-posted). Pins are used to keep latest charts visible.""",
    "🎓-learning-resources": """**📌 KNOWLEDGE BASE**
*Education & Guides*

*   **Topic:** 📚 Educational resources, tutorials, and guides for improving your trading skills.""",
    "commands-codex": """**📌 MANUAL**
*Bot Usage Guide*

*   **Topic:** 📋 Bot command codex — how to use bot services. Readable by all users.""",
    "💬-market-discussion": """**📌 THE PIT**
*Professional Discourse*

*   **Topic:** 🏛️ THE PIT. Professional market discourse and collaborative alpha generation. High signal, low noise.
*   **Rules:** Be respectful and constructive.""",
    "📚-research-journal": """**📌 LABORATORY NOTES**
*Working Drafts*

*   **Topic:** 🔬 Research journal and working notes. Published research and drafts.""",
    "🤖-bot-logs": """**📌 SENTINEL LOGS**
*System Status*

*   **Topic:** ⚙️ Bot status, health checks, and system logs. Admin visibility only.""",
    "📥-reports": """**📌 CENTRAL INBOX**
*Admin Review Queue*

*   **Topic:** 📥 Central admin inbox for generated reports (premarket, journal, research). Visible to Bot Admins only.""",
    "🔧-service": """**📌 OPS TERMINAL**
*Maintenance*

*   **Topic:** 🔧 Private service/test channel for operator posts (visible to Bot Admins).""",
}


class Broadcaster(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.guilds = True
        super().__init__(intents=intents)

    async def on_ready(self):
        print(f"Logged in as {self.user}")

        for guild in self.guilds:
            print(f"Scanning guild: {guild.name}")
            channels = {c.name: c for c in guild.text_channels}

            for channel_name, message in MESSAGES.items():
                channel = channels.get(channel_name)
                if channel:
                    print(f"--> Sending to #{channel_name}")
                    try:
                        # Fetch recent messages to check if already sent
                        history = [m async for m in channel.history(limit=5)]
                        already_posted = any(message[:20] in m.content for m in history)

                        if not already_posted:
                            msg = await channel.send(message)
                            try:
                                await msg.pin()
                                print("    (Pinned)")
                            except Exception:
                                print("    (Could not pin)")
                        else:
                            print("    (Skipped - already posted)")
                    except Exception as e:
                        print(f"    (Failed: {e})")
                else:
                    print(f"--> Channel #{channel_name} not found")

        await self.close()


if __name__ == "__main__":
    client = Broadcaster()
    client.run(TOKEN)
