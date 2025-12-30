# Syndicate Sentinel
> The Watchdog

## Overview

**Sentinel** (`scripts/syndicate_sentinel.py`) is the self-healing subsystem of Reign implemented to address the turing problem. It runs as an independent `systemd` service, completely separate from the Daemon and Worker, ensuring that if they crash or stall, they are recovered automatically.

---

## Core Responsibilities

The Sentinel operates on a **5-minute heartbeat loop** and performs three critical checks:

### 1. Service Integrity (The "Pulse" Check)
It queries `systemd` via D-Bus (subprocess) to check the status of:
*   `syndicate-daemon.service`
*   `syndicate-llm-worker.service`
*   `syndicate-discord.service`

**Action**: If any service is `inactive`, `failed`, or `dead`, Sentinel immediately issues a `systemctl restart [service]` command and logs the incident.

### 2. Queue Health (The "Stall" Check)
It connects to `data/syndicate.db` and inspects the `llm_tasks` table.

*   **Condition**: Tasks with `status='in_progress'` for > 30 minutes.
*   **Diagnosis**: This indicates the Worker crashed *during* generation, or hung indefinitely.
*   **Action**:
    1.  Resets task to `status='pending'` (retry).
    2.  Restarts `syndicate-llm-worker` to clear any zombie processes.
    3.  Increments the `retry_count` on the task.

### 3. Resource Monitoring (The "Load" Check)
It checks system vital signs:
*   **CPU Usage**: Warns if sustained > 90%.
*   **RAM Usage**: Warns if free memory < 500MB.
*   **Disk Space**: Warns if `/` or `/mnt/data` is > 90% full.

**Action**: Currently logs warnings. (Future: Alert via Discord Webhook).

---

## Operational Commands

### Checking Sentinel Status
```bash
sudo systemctl status syndicate-sentinel
```

### Viewing Sentinel Logs
To see what interventions Sentinel has taken:
```bash
sudo journalctl -u syndicate-sentinel -n 100
```
*Look for "FIXED:", "RESTARTED:", or "RESET:" in the logs.*

### Manual Override
If Sentinel itself is misbehaving (e.g., restarting loops), you can stop it:
```bash
sudo systemctl stop syndicate-sentinel
```

---

## Architecture Notes
*   **Python-Native**: Written in pure Python to share config/logging logic with the Core.
*   **Privileged**: Runs as a user depending on `systemd` access (configured via sudoers or polkit for specific `systemctl` commands).
*   **Fail-Safe**: If Sentinel crashes, `systemd` is configured to restart *it* as well (`Restart=always`).
