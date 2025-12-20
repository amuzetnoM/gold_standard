"""Utility helpers for Discord bot: metrics & notifier wrappers."""
from __future__ import annotations

import logging
from prometheus_client import Counter, Gauge

LOG = logging.getLogger("digest_bot.discord.utils")

cmd_counter = Counter("gost_discord_commands_total", "Total Discord commands executed")
error_counter = Counter("gost_discord_errors_total", "Total errors in Discord bot")
background_tasks_gauge = Gauge("gost_discord_background_tasks", "Number of background tasks running")
