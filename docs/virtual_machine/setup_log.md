# Gold Standard Setup Log - 2025-12-13 00:38:10

## 1. Introduction
This document serves as a comprehensive log detailing the setup, configuration, issues encountered, and solutions implemented for the Gold Standard system. Its purpose is to provide a complete "source of truth" for anyone seeking to understand the system's current state and operational rationale.

## 2. Initial System State and Goals
The Gold Standard system is deployed on a Virtual Machine (VM) with a specific disk configuration:
- **Root Disk**: A small (e.g., 50GB) disk primarily for the VM's operating system and core functionalities. This disk *must not* be used for persistent application data or Docker-related storage.
- **New Disk (`/mnt/newdisk`)**: A larger (e.g., 500GB) dedicated data disk intended for all application data, logs, Docker volumes, and other persistent storage.

**The primary and critical user requirement throughout this setup was to ensure that absolutely no data is written to the root filesystem.** All persistent operations, especially those involving Docker and logs, must be directed to `/mnt/newdisk`.

The overarching goal was to get the `gold_standard` system running correctly, robustly, and with all data persistently stored on `/mnt/newdisk`, triggered automatically as scheduled by `systemd`.

## 3. Core Project Overview (Pre-Modifications)
The `gold_standard` is a Python-based quantitative analysis system.

- **Application Structure**:
    - Developed in Python, utilizing a virtual environment (`.venv`).
    - Core logic in `main.py` orchestrates `Cortex` (memory), `QuantEngine` (data/TA), and `Strategist` (AI).
    - CLI entry point `run.py` handles various execution modes (daemon, single run, interactive).
- **Configuration**:
    - Relies on environment variables for API keys (`GEMINI_API_KEY`, `NOTION_TOKEN`, `IMGBB_API_KEY`) typically loaded from a `.env` file in the project root.
- **Docker Compose**:
    - `gold_standard/docker-compose.yml` defines multiple services (e.g., `gost` for the main app, `prometheus`, `grafana`, `alertmanager`, `loki`, `promtail` for monitoring/logging, `node-exporter`, `cadvisor`).
    - Initially used Docker named volumes for persistent data storage.
- **Systemd Automations**:
    - `gold-standard-daily.service` (triggering daily analysis).
    - `gold-standard-weekly-cleanup.service` (for weekly cleanup tasks).
    - `gold-standard-compose.service` (manages the Docker Compose stack on boot).
    - Corresponding `.timer` files (`gold-standard-daily.timer`, `gold-standard-weekly-cleanup.timer`) define the scheduling.
- **`codex.sh`**:
    - A shell script (`/home/ali_shakil_backup/codex.sh`) to simplify interaction with the Docker Compose stack (run, build, monitor, stop).

## 4. Issues Encountered and Solutions Implemented

### 4.1. Issue: Docker Writes to Root Filesystem (Named Volumes)
- **Rationale**: The initial `docker-compose.yml` defined Docker named volumes (e.g., `gost_data`, `prometheus_data`). By default, Docker stores these named volumes under `/var/lib/docker/volumes` on the host, which typically resides on the root filesystem. This directly violated the critical requirement.
- **Solution**:
    1. Created a dedicated directory: `/mnt/newdisk/gold_standard/docker-data`.
    2. Modified `gold_standard/docker-compose.yml` to replace all named volumes with explicit **bind mounts** to subdirectories within `/mnt/newdisk/gold_standard/docker-data`. For example, `gost_data` was changed from a named volume to a bind mount to `./docker-data/gost_data`.
- **Verification**: All Docker-managed persistent data (database, output, Prometheus data, Grafana data, etc.) is now stored on the `/mnt/newdisk` partition, completely avoiding the root filesystem.

### 4.2. Issue: Systemd Service Logs Writing to Root Filesystem
- **Rationale**: The `systemd` service files (`gold-standard-daily.service`, `gold-standard-weekly-cleanup.service`) were configured to append their `StandardOutput` and `StandardError` to log files within `/home/ali_shakil_backup/gold_standard_config/`. This directory is on the root filesystem.
- **Solution**:
    1. Created the `gold_standard_config` directory on the data disk: `/mnt/newdisk/gold_standard/gold_standard_config`.
    2. Modified `gold-standard-daily.service` and `gold-standard-weekly-cleanup.service` using `sed` to update their `StandardOutput` and `StandardError` paths to point to the new location: `/mnt/newdisk/gold_standard/gold_standard_config/run.log` and `/mnt/newdisk/gold_standard/gold_standard_config/cleanup.log` respectively.
    3. Executed `sudo systemctl daemon-reload` to apply these changes to `systemd`.
- **Verification**: Service logs are now correctly directed to `/mnt/newdisk`.

### 4.3. Issue: API Keys Not Loaded (Empty Environment Variables)
- **Rationale**: When `codex.sh run` was executed, the `GEMINI_API_KEY` (and others) were reported as unset inside the Docker container. This happened because `docker compose run -e VAR="${VAR}"` only passes variables that are *already set* in the shell where `codex.sh` is running. The `.env` file was present but not sourced by `codex.sh`.
- **Solution**: Modified `/home/ali_shakil_backup/codex.sh` to explicitly `source "/mnt/newdisk/gold_standard/.env"` before executing the `docker compose run` command. This loads the environment variables from the `.env` file into the shell environment of `codex.sh`.
- **Verification**: The Gemini AI is now reported as configured (`[LLM] ✓ Primary: Gemini`).

### 4.4. Issue: `run.py` Entering Autonomous Mode (`--once` flag ignored)
- **Rationale**: The `codex.sh run` command calls `python run.py --once`, which is intended to execute a single analysis cycle and exit. However, `run.py` was observed entering "AUTONOMOUS MODE" (daemon mode) before exiting. This was due to a logic flaw in `run.py`'s `main` function (it defaulted to daemon mode if no other specific run command was matched) and an outdated Docker image.
- **Solution**:
    1. Modified `gold_standard/run.py` to add an explicit conditional check `if args.once: run_all(...) ; return` early in the `main` function, ensuring it exits after a single `run_all` call when `--once` is present.
    2. Removed the `image: ghcr.io/amuzetnom/gold_standard:latest` line from the `gost` service in `docker-compose.yml`. This forced `docker compose` to use the locally built image (reflecting `run.py` changes) instead of pulling a potentially outdated one from a registry.
    3. Rebuilt the Docker image using `codex.sh build`.
- **Verification**: The script now correctly runs a single analysis cycle and exits cleanly, without entering autonomous daemon mode.

### 4.5. Issue: `matplotlib` Cache Directory Permissions
- **Rationale**: `matplotlib` attempted to create its cache directory (e.g., `~/.cache/matplotlib`) in a location inside the container where the `goldstandard` user did not have write permissions.
- **Solution**: Added `MPLCONFIGDIR=/tmp/matplotlib` as an environment variable to the `gost` service in `docker-compose.yml`. This redirects `matplotlib`'s cache directory to `/tmp/matplotlib` within the container, which is always a writable temporary location.
- **Verification**: `matplotlib` chart generation now proceeds without permission errors.

### 4.6. Issue: Persistent `cortex_memory.lock` Permission Denied
- **Rationale**: This was the most stubborn permission issue, preventing `Cortex` from writing its memory file and lock file. Despite correcting file/directory ownership and ensuring `cortex_memory.json` was not read-only, the `filelock` library still reported permission denied when trying to create `/app/cortex_memory.lock`. This indicated a deeper interaction issue with `filelock` and Docker bind mounts when the file was directly in the application's root directory.
- **Solution**:
    1. Modified `gold_standard/main.py` to change the `Config.MEMORY_FILE` and `Config.LOCK_FILE` properties. They now point to paths within the `/app/data` directory (`/app/data/cortex_memory.json` and `/app/data/cortex_memory.lock`). This relocates the memory files to the dedicated persistent data volume (`gost_data`).
    2. Removed the explicit `cortex_memory.json` mount from the `gost` service in `docker-compose.yml`, as the file is now expected to be within the `gost_data` volume managed by the application logic.
    3. Rebuilt the Docker image using `codex.sh build`.
    4. Modified `codex.sh` to add `--user "1000:1003"` to the `docker compose run` command. This ensures the ephemeral container created by `docker compose run` explicitly executes as the host's `ali_shakil_backup` user (UID 1000, GID 1003), matching the ownership of the bind-mounted directories and files.
- **Verification**: `cortex_memory.lock` permission errors are finally resolved, and the `Cortex` memory system operates correctly.

## 5. Current Operational Status
As of **2025-12-13 00:38:10**, the `gold_standard` system is configured and operational as follows:

- **Execution**: The system successfully completes a single analysis run when triggered via `/home/ali_shakil_backup/codex.sh run`, executing `python run.py --once` inside its Docker container.
- **Data Persistence**: All persistent data (SQLite database, output reports, charts, `cortex_memory.json`, Docker volumes) and service logs are correctly directed to the `/mnt/newdisk` partition, safeguarding the root filesystem.
- **Configuration**: API keys are loaded from `gold_standard/.env` and correctly passed to the Docker container.
- **User Context**: Docker containers run with appropriate user permissions (`goldstandard` user internally, mapped to `ali_shakil_backup` on host for bind mounts), ensuring file access.
- **Systemd Automations**: The `systemd` service and timer files (`gold-standard-daily.*`, `gold-standard-weekly-cleanup.*`, `gold-standard-compose.service`) are correctly configured to manage the application's lifecycle and scheduled tasks.
