Gold Standard Discord Bot — Blueprint

This blueprint contains a production-minded scaffold for the Discord bot powering operational notifications and light LLM interactions.

Quick start (dev)
------------------
1. Install digest bot requirements: `pip install -r src/digest_bot/requirements.txt`
2. Copy `.env.example` to `.env` and set `DISCORD_BOT_TOKEN` and `DISCORD_OPS_CHANNEL_ID`.
3. Run: `python -m digest_bot.discord.bot_base` (development run; does not auto-post to channels unless configured).

Design principles
-----------------
- Safety-first: the bot never publishes raw LLM outputs. All results go through `llm sanitizer` paths.
- Minimal privileges: run with only necessary intents and role checks for ops commands.
- Observability: metrics for command usage, errors, and background task outcomes.

Files of interest
-----------------
- `bot_base.py`: orchestrator and lifecycle manager
- `cogs/`: modular features (reporting, moderation, sanitizer alerts, llm)
- `utils.py`: shared helpers for metrics and notifier
- `BLUEPRINT_ARCHITECTURE.md`: design doc

Notes
-----
This is a blueprint and intentionally conservative; full production rollout must include secrets management, an approval testing plan, and a careful permission audit before enabling message content intents.