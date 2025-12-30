# Syndicate Reign — Production System

## Purpose
This document captures the full, current operational context for the **Syndicate Reign** system running on the production VM. It serves as the authoritative source of truth for the system's architecture, services, and operational procedures.

---

## System Architecture

### Core Components
*   **Syndicate Daemon (`syndicate-daemon`)**: The central nervous system. Orchestrates daily market analysis, generates trading signals, and manages the task queue.
*   **Discord Bot (`syndicate-discord`)**: The autonomy interface. Handles "Intelligence" requests (`/intel`, `@Syndicate`) and broadcasts digests/alerts.
*   **LLM Worker (`syndicate-llm-worker`)**: Dedicated compute worker. Consumes the `llm_tasks` queue to generate AI content (research, digests) in parallel, decoupling it from the main event loop.
*   **Sentinel (`syndicate-sentinel`)**: The Watchdog. Monitors system health (CPU/RAM, Services), restarts failed components, and unjams "stuck" tasks.

### Infrastructure
*   **VM**: GCP Compute Instance (`syndicate`)
*   **OS**: Debian/Ubuntu
*   **User**: `ali_shakil_backup_gmail_com`
*   **Path**: `/home/ali_shakil_backup_gmail_com/syndicate`
*   **Environment**: Conda environment `syndicate`

---

## Active Services (Systemd)

All services are normalized in `/etc/systemd/system/`:

1.  **`syndicate-daemon.service`**
    *   **Command**: `python run.py --daemon`
    *   **Function**: Core event loop, scheduling, and task delegation.
2.  **`syndicate-discord.service`**
    *   **Command**: `python -m src.digest_bot.discord.bot`
    *   **Function**: Discord gateway connection and interaction.
3.  **`syndicate-llm-worker.service`**
    *   **Command**: `python scripts/llm_worker.py`
    *   **Function**: Processes AI generation tasks from SQLite queue.
4.  **`syndicate-sentinel.service`**
    *   **Command**: `python scripts/syndicate_sentinel.py`
    *   **Function**: Self-healing and health reporting.

---

## Operational Commands

### Management
*   **Restart All**: `sudo systemctl restart syndicate-*`
*   **View Logs**: `sudo journalctl -u syndicate-daemon -f` (or replace with service name)
*   **Check Health**: `python scripts/check_status.py`

### Admin Actions (Discord)
*   `!health`: Get current system status.
*   `!reset_tasks`: Manually unjam the task queue.
*   `!force_publish`: Trigger immediate Notion synchronization.

---

## Key Files & Locations
*   **Config**: `.env` (Secrets - DO NOT COMMIT)
*   **Database**: `data/syndicate.db` (SQLite)
*   **Output**: `output/` (Reports, Journals, Signals)
*   **Logs**: `logs/` and System Journal

## Deployment
To deploy changes from local workspace:
1.  **Sync Code**: `scp -r src scripts run.py ...`
2.  **Restart Services**: `sudo systemctl restart syndicate-daemon syndicate-discord syndicate-llm-worker`

---

**Status**: SYSTEM IS FULLY AUTONOMOUS.
