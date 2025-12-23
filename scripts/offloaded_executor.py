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
from datetime import datetime, timezone
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


def choose_fast_model(llm: LocalLLM, db: DatabaseManager | None = None, keep_list: list[str] | None = None):
    """Choose a fast model heuristic:
    - Prefer names in KEEP_LOCAL_MODELS or provided keep_list
    - Prefer recently used models (if DB provided)
    - Prefer name hints (mini/tiny/fast) and small size
    """
    models = llm.find_models()
    if not models:
        return None

    keep_list = [k.lower() for k in (keep_list or KEEP_LOCAL_MODELS or []) if k]

    # If DB provided, prefer recently used models present in DB
    if db:
        try:
            with db._get_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT model_path, last_used FROM model_usage ORDER BY last_used DESC")
                used = [r["model_path"] for r in cur.fetchall()]
                for path in used:
                    for m in models:
                        if str(m.get("path")) == str(path):
                            return m["path"]
        except Exception:
            # DB issues shouldn't break selection
            pass

    # Prefer keep_list
    for keep in keep_list:
        for m in models:
            if keep in m.get("name", "").lower() or keep in str(m.get("path", "")).lower():
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
        from datetime import timezone
        now = datetime.now(timezone.utc).isoformat()
        with db._get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE llm_tasks SET status = 'started', started_at = ?, last_attempt_at = ?, attempts = attempts + 1 WHERE id = ?",
                (now, now, task_id),
            )

        try:
            result = llm.generate(prompt, max_tokens=1024)
            LOG.info("Task %s completed (len=%d)", task_id, len(result))

            # Record model usage in DB if possible
            try:
                db.record_model_usage(llm._config.model_path or getattr(llm, '_model_name', ''), name=getattr(llm, 'model_name', None), size_gb=None)
            except Exception:
                pass

            from datetime import timezone
            with db._get_connection() as conn:
                cur = conn.cursor()
                cur.execute(
                    "UPDATE llm_tasks SET status = 'done', response = ?, completed_at = ? WHERE id = ?",
                    (result, datetime.now(timezone.utc).isoformat(), task_id),
                )
        except Exception as e:
            LOG.exception("Task %s failed on model %s: %s", task_id, getattr(llm, 'model_name', None), e)

            # If the failure looks like a model fault, attempt one model reload/swap before giving up
            tried_reload = False
            try:
                llm.unload()
                alt_model = choose_fast_model(llm, db=db)
                if alt_model and str(alt_model) != str(getattr(llm, '_model_name', '')):
                    LOG.info("Attempting to reload alternative model: %s", alt_model)
                    if llm.load_model(alt_model):
                        LOG.info("Reloaded model %s, retrying task %s", alt_model, task_id)
                        tried_reload = True
                        result = llm.generate(prompt, max_tokens=1024)
                        with db._get_connection() as conn:
                            cur = conn.cursor()
                            cur.execute(
                                "UPDATE llm_tasks SET status = 'done', response = ?, completed_at = ? WHERE id = ?",
                                (result, datetime.now(timezone.utc).isoformat(), task_id),
                            )
            except Exception:
                LOG.exception("Retry after model reload failed for task %s", task_id)

            if tried_reload:
                continue

            # Retry at task level if attempts < max_attempts
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
                    from datetime import timezone
                    cur.execute(
                        "UPDATE llm_tasks SET status = 'failed', error = ?, completed_at = ? WHERE id = ?",
                        (str(e), datetime.now(timezone.utc).isoformat(), task_id),
                    )
    return len(rows)


def run_loop(db_path: Path, poll_s: int = DEFAULT_POLL_S):
    LOG.info("Starting offloaded executor (poll_s=%s)", poll_s)
    db = DatabaseManager(db_path)
    llm = LocalLLM()

    # Choose and attempt to load a fast GGUF model with retry/backoff
    attempts = 0
    model = None
    while attempts < 3 and running:
        model = choose_fast_model(llm, db=db)
        if not model:
            LOG.warning("No local GGUF models found; offloaded executor won't run until a model is available")
            time.sleep(60)
            attempts += 1
            continue

        try:
            if llm.load_model(model):
                LOG.info("Loaded offload model: %s", llm.model_name)
                # Record usage
                try:
                    db.record_model_usage(model, name=llm.model_name)
                except Exception:
                    LOG.debug("Failed to record model usage (DB)")
                break
            else:
                LOG.warning("Failed to load chosen offload model: %s", model)
        except Exception:
            LOG.exception("Exception while loading model %s", model)
        attempts += 1
        time.sleep(5 * attempts)

    # Main loop: process tasks and periodically check for pruning requests
    prune_check_counter = 0
    AUTO_PRUNE_DAYS = int(os.environ.get("AUTO_PRUNE_DAYS", "0"))
    AUTO_PRUNE_CONFIRM = os.environ.get("AUTO_PRUNE_CONFIRM", "0") in ("1", "true", "yes")
    AUTO_PRUNE_MIN_KEEP = int(os.environ.get("AUTO_PRUNE_MIN_KEEP", "1"))

    while running:
        try:
            worked = poll_once(db, llm)
            prune_check_counter += 1

            # If no work, sleep a bit
            if worked == 0:
                time.sleep(poll_s)

            # Periodically (every 10 cycles) check auto-prune settings
            if AUTO_PRUNE_DAYS > 0 and prune_check_counter >= 10:
                prune_check_counter = 0
                try:
                    to_remove = db.get_unused_models(days_threshold=AUTO_PRUNE_DAYS, keep_list=KEEP_LOCAL_MODELS, min_keep=AUTO_PRUNE_MIN_KEEP)
                    if to_remove:
                        LOG.info("Auto-prune candidates: %s", [r.get('name') for r in to_remove])
                        if AUTO_PRUNE_CONFIRM:
                            # Attempt to delete files safely (move to .model_trash then unlink)
                            trash_dir = Path(PROJECT_ROOT) / ".model_trash"
                            trash_dir.mkdir(parents=True, exist_ok=True)
                            for r in to_remove:
                                p = Path(r.get("model_path"))
                                if not p.exists():
                                    LOG.info("Model not found (skipping): %s", p)
                                    continue
                                try:
                                    dst = trash_dir / p.name
                                    p.rename(dst)
                                    LOG.info("Pruned model moved to trash: %s", dst)
                                except Exception:
                                    LOG.exception("Failed to move model to trash: %s", p)
                        else:
                            LOG.info("Auto-prune dry-run (AUTO_PRUNE_CONFIRM not set); no files removed")
                except Exception:
                    LOG.exception("Auto-prune check failed")

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
