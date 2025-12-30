# Syndicate Reign — Absolute System Definition

**Version**: Reign 1.0 (Autonomous)
**Status**: ACTIVE / HANDS-OFF
**Last Verified**: 2025-12-30

---

## 1. Core Philosophy
Syndicate Reign is an **autonomous quantitative intelligence engine**. It operates without human intervention, governed by a rigid schedule and self-healing sentinels.
*   **No Manual Triggers**: The system runs on `systemd` timers.
*   **Self-Correction**: The `Sentinel` service monitors health and fixes application states.
*   **Decoupled Intelligence**: Discord is the interface; Backend is the brain.

---

## 2. Infrastructure Architecture

### Virtual Machine
*   **Host**: `syndicate` (GCP Compute)
*   **User**: `ali_shakil_backup_gmail_com`
*   **Root Path**: `/home/ali_shakil_backup_gmail_com/syndicate`
*   **Python Env**: `~/miniforge3/envs/syndicate`

### Service Mesh (Systemd)
The system is composed of **4 independent, cooperating services**. All legacy `gold-standard-*` services have been purged.

| Service Name | Script | Role | Schedule |
| :--- | :--- | :--- | :--- |
| **`syndicate-daemon`** | `run.py --daemon` | **Orchestrator**. Manages the daily loop, market data limits, and task dispatching. | Continuous (Loop) |
| **`syndicate-llm-worker`** | `scripts/llm_worker.py` | **Compute Node**. Consumes `llm_tasks` from DB. Dedicated process for heavy AI generation. | Continuous (Queue) |
| **`syndicate-sentinel`** | `scripts/syndicate_sentinel.py` | **Watchdog**. Checks CPU/RAM, restarts crashed services, unjams stuck tasks (>30m). | Loop (5m interval) |
| **`syndicate-discord`** | `src.digest_bot.discord.bot` | **Interface**. Posts digests, journals, and handles user `/intel` requests. | Continuous (Gateway) |

### Data Flow
1.  **Daemon** triggers analysis -> Writes `action` to DB.
2.  **Daemon** posts `llm_tasks` (prompts) to DB.
3.  **LLM Worker** picks up `llm_tasks` -> Generates Content -> Updates DB -> Writes Markdown to `output/`.
4.  **Notion Publisher** (inside Daemon) syncs Markdown -> Notion.
5.  **Discord Bot** reads DB/Files -> Broadcasts to Channels.

---

## 3. Operations & Controls

### Discord Command Center
These commands are available in `#syndicate-intel` or `#admin-ops`:

*   `/intel [query]` — Request immediate market analysis (Queued to LLM Worker).
*   `!health` — Demand a system status report (CPU, RAM, Services).
*   `!force_publish` — Trigger immediate Notion sync.
*   `!reset_tasks` — Emergency override to clear stuck AI tasks.

### Manual Console Recovery
If Discord is unreachable, SSH into the VM:

```bash
# Check Status
sudo systemctl status syndicate-*

# View Real-time Logs
sudo journalctl -u syndicate-daemon -f
sudo journalctl -u syndicate-llm-worker -f

# Emergency Restart
sudo systemctl restart syndicate-daemon syndicate-llm-worker syndicate-discord syndicate-sentinel
```

---

## 4. File System Standards

*   `data/syndicate.db`: Single source of truth. SQLite WAL mode.
*   `output/reports/`: All generated markdown intelligence.
*   `output/journals/`: Daily trading journals.
*   `logs/`: Application-level logs (rotating).
*   `.env`: **ONLY** location for secrets (Notion Key, Discord Token).

---

## 5. Security & Autonomy
*   **No Root**: Services run as user `ali_shakil_backup_gmail_com`.
*   **Secrets**: `.env` is `.gitignore`'d.
*   **Recovery**: `syndicate-sentinel` will auto-restart any service that exits with failure.

**THIS DOCUMENT IS THE ABSOLUTE SOURCE OF TRUTH.**
Any configuration deviating from this is considered "Legacy" or "Drift" and must be corrected.
