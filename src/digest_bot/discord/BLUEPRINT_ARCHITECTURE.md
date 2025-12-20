# Gold Standard — Discord Bot Blueprint (Architecture)

Overview
--------
This document captures the architecture and design rationale for a first-of-its-kind, state-of-the-art Discord integration for Gold Standard. The bot is designed to be an operational control-plane and a lightweight assistant for day-to-day monitoring, incident alerts, digest publishing, and constrained LLM-powered interactions.

Goals
-----
- Operational visibility: post daily LLM reports, sanitizer alerts, and queue health to an ops channel.
- Human-in-the-loop: provide commands to fetch recent sanitizer audits, flag/unflag tasks, and re-run a generation.
- Safety-first: never post raw LLM-generated content without sanitizer checks; allow operators to accept or reject content.
- Extensibility: modular Cog-based architecture (discord.py) so features are pluggable and testable.
- Metrics & health: expose internal metrics via Prometheus client and readiness endpoints.
- Security: least privilege tokens, secure storage for webhook tokens and ephemeral secrets, rate limiting, and role-based command controls.

Core Components
---------------
- Bot core: `bot_base.py` — initialize the `discord.Bot` (slash + message commands), lifecycle management, metrics, graceful shutdown.
- Cogs:
  - `cogs.reporting` — create and send daily digest posts on demand, view last report, and schedule ad-hoc runs.
  - `cogs.sanitizer_alerts` — listen for sanitizer audit events and post compact summaries, allow triage commands.
  - `cogs.moderation` — role-restricted commands for operators: view flagged tasks, re-run, or mark as resolved.
  - `cogs.llm_integration` — run short LLM queries with enforced ICU (inspection) and sanitized results.
- Utilities:
  - `utils.metrics` — Prometheus gauges/counters integrated with `gold_standard/metrics` pipeline.
  - `utils.notifier` — wrapper to send messages to Discord webhooks and internal channels.

Operational patterns
--------------------
- Use slash commands for interactive ops and message-based low-noise notifications for alerts.
- Background task loop: sends daily report, watches sanitizer counters, and alerts if thresholds breached.
- Circuit breaker and retry policies when calling external services (Ollama, Notion, Google GenAI).
- Audit logging: every moderator action is written to the DB (or audit log) with user, timestamp, and justification.

Security & deployment
---------------------
- Bot token stored in a secrets manager (.env for staging, Vault/KMS for production).
- Use minimal scopes for bot (gateway intents minimized; only enable MESSAGE_CONTENT if required and justified).
- Systemd unit sample and containerization recommended (Dockerfile + process supervisor).

Testing & CI
------------
- Unit tests: validate Cog registration, configuration parsing, and command permission checks using mocked Discord objects.
- Integration smoke: run in a staging channel with a test bot token for sanity verification.

Roadmap
-------
1. Basic reporting & health alerts
2. Moderator command set and sanitizer triage
3. LLM-safe interactive summarization in ops channel
4. Bot-managed Notion publish flow (review + approve)
5. Advanced: automated incident postmortem generator and limited self-refactor commands (carefully gated)
