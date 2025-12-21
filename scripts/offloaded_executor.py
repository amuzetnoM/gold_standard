#!/usr/bin/env python3
"""Offloaded executor that runs a small pool of fast GGUF models locally and processes "fast" LLM tasks.

Runs as a lightweight daemon (or --once) and is intended to take small/low-latency tasks off the main executor.

Usage:
    python scripts/offloaded_executor.py --once
    # or run as a long-running service (systemd provided)

Environment:
    OFFLOAD_POLL_S         - seconds between polls (default 30)
    OFFLOAD_MAX_TASKS      - max tasks per cycle (default 5)
    OFFLOAD_MAX_ATTEMPTS   - attempts before marking failed (default 3)
    KEEP_LOCAL_MODELS      - comma-separated model names to keep (for model selection)

"""

from __future__ import annotations

import argparse
import logging
import os
import signal
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List

# Add project src
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from db_manager import DatabaseManager
from scripts.local_llm import LocalLLM

LOG = logging.getLogger("offloaded_executor")

DEFAULT_POLL_S = int(os.environ.get("OFFLOAD_POLL_S", "30"))
DEFAULT_MAX_TASKS = int(os.environ.get("OFFLOAD_MAX_TASKS", "5"))
DEFAULT_MAX_ATTEMPTS = int(os.environ.get("OFFLOAD_MAX_ATTEMPTS", "3"))
KEEP_LOCAL_MODELS = [m.strip() for m in os.environ.get("KEEP_LOCAL_MODELS", "").split(",") if m.strip()]

running = True


def handle_sigterm(signum, frame):
    global running
    LOG.info("Received signal %s, shutting down...", signum)
    running = False


signal.signal(signal.SIGINT, handle_sigterm)
signal.signal(signal.SIGTERM, handle_sigterm)


def choose_fast_model(llm: LocalLLM):
    """Choose a fast model heuristic: prefer names in KEEP_LOCAL_MODELS, then small size, then 'mini' hints."""
    models = llm.find_models()
    if not models:
        return None

    # If KEEP_LOCAL_MODELS provided, prefer first found match
    for keep in KEEP_LOCAL_MODELS:
        for m in models:
            if keep.lower() in m.get("name", "").lower() or keep.lower() in str(m.get("path", "")).lower():
                return m["path"]

    # Prefer name hints
    for hint in ("mini", "tiny", "fast", "phi3", "mistral"):
        for m in models:
            if hint in m.get("name", "").lower():
                return m["path"]

    # Otherwise pick the smallest by file size if available
    try:
        models_sorted = sorted(models, key=lambda x: x.get("size_gb", 9999))
        return models_sorted[0]["path"]
    except Exception:
        return models[0]["path"]


def poll_once(db: DatabaseManager, llm: LocalLLM, max_tasks: int = DEFAULT_MAX_TASKS, max_attempts: int = DEFAULT_MAX_ATTEMPTS):
    """Run one cycle: pick pending fast tasks and execute locally."""
    with db._get_connection() as conn:
        cur = conn.cursor()
        # Select pending 'generate' tasks that are small or have priority 'fast'
        cur.execute(
            """
            SELECT id, prompt, attempts FROM llm_tasks
            WHERE status = 'pending' AND task_type = 'generate' AND (priority = 'fast' OR length(prompt) < 2000)
            ORDER BY created_at ASC LIMIT ?
            """,
            (max_tasks,),
        )
        rows = cur.fetchall()

    if not rows:
        LOG.debug("No eligible tasks found")
        return 0

    for row in rows:
        task_id = int(row[0])
        prompt = row[1]
        attempts = int(row[2] or 0)

        LOG.info("Processing task %s (attempts=%s)", task_id, attempts)

        # Mark started
        now = datetime.utcnow().isoformat()
        with db._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE llm_tasks SET status = 'started', started_at = ?, last_attempt_at = ?, attempts = attempts + 1 WHERE id = ?",
                (now, now, task_id),
            )

        try:
            result = llm.generate(prompt, max_tokens=1024)
            LOG.info("Task %s completed (len=%d)", task_id, len(result))

            with db._get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE llm_tasks SET status = 'done', response = ?, completed_at = ? WHERE id = ?",
                    (result, datetime.utcnow().isoformat(), task_id),
                )
        except Exception as e:
            LOG.exception("Task %s failed: %s", task_id, e)
            # Retry if attempts < max_attempts
            if attempts + 1 < max_attempts:
                with db._get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE llm_tasks SET status = 'pending', error = ? WHERE id = ?",
                        (str(e), task_id),
                    )
            else:
                with db._get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE llm_tasks SET status = 'failed', error = ?, completed_at = ? WHERE id = ?",
                        (str(e), datetime.utcnow().isoformat(), task_id),
                    )
    return len(rows)


def run_loop(db_path: Path, poll_s: int = DEFAULT_POLL_S):
    LOG.info("Starting offloaded executor (poll_s=%s)", poll_s)
    db = DatabaseManager(db_path)
    llm = LocalLLM()

    # Choose a fast GGUF model and load
    model = choose_fast_model(llm)
    if not model:
        LOG.warning("No local GGUF models found; offloaded executor won't run until a model is available")
    else:
        if llm.load_model(model):
            LOG.info("Loaded offload model: %s", llm.model_name)
        else:
            LOG.warning("Failed to load chosen offload model: %s", model)

    while running:
        try:
            worked = poll_once(db, llm)
            if worked == 0:
                time.sleep(poll_s)
        except Exception:
            LOG.exception("Error in offloaded executor main loop")
            time.sleep(max(poll_s, 5))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run one cycle and exit")
    parser.add_argument("--db-path", type=str, help="Path to sqlite DB (overrides default)")
    parser.add_argument("--poll-s", type=int, default=DEFAULT_POLL_S)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    db_path = Path(args.db_path) if args.db_path else None
    if args.once:
        db = DatabaseManager(db_path)
        llm = LocalLLM()
        model = choose_fast_model(llm)
        if model and llm.load_model(model):
            LOG.info("Loaded offload model: %s", llm.model_name)
        poll_once(db, llm)
        return

    run_loop(db_path, args.poll_s)


if __name__ == "__main__":
    main()
