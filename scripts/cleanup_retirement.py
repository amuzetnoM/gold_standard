#!/usr/bin/env python3
"""Cleanup and retirement script to run periodically.

Responsibilities:
- Find stuck llm_tasks (started but running > threshold) and either requeue or mark failed
- Move slow tasks along (reset started_at, increment attempts)
- Trigger executor drain for a short run
- Trigger Notion retry publishes
- Record bot_audit entries
"""
import logging
from datetime import datetime, timedelta
from pathlib import Path

import sys
# ensure project root is on sys.path when invoked from systemd wrapper
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from db_manager import DatabaseManager

logger = logging.getLogger("cleanup_retirement")

# thresholds
STALE_SECONDS = int(60 * 60)  # 1 hour
MAX_ATTEMPTS = 5
EXECUTOR_MAX_TASKS = 100


def find_stale_tasks(db: DatabaseManager, older_than_seconds: int = STALE_SECONDS):
    from datetime import timezone
    cutoff = (datetime.now(timezone.utc) - timedelta(seconds=older_than_seconds)).isoformat()

    with db._get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, document_path, status, attempts, started_at FROM llm_tasks WHERE started_at IS NOT NULL AND status != 'completed' AND datetime(started_at) <= datetime(?, 'utc')",
            (cutoff,)
        )
        rows = [dict(r) for r in cur.fetchall()]
    return rows


def retire_or_reset_task(db: DatabaseManager, task_row: dict):
    tid = task_row["id"]
    attempts = task_row.get("attempts") or 0
    from datetime import timezone
    now = datetime.now(timezone.utc).isoformat()

    import sqlite3, time
    retry = 3
    while retry > 0:
        try:
            with db._get_connection() as conn:
                cur = conn.cursor()
                if attempts >= MAX_ATTEMPTS:
                    logger.info("Marking task %s as failed (attempts=%s)", tid, attempts)
                    cur.execute(
                        "UPDATE llm_tasks SET status = 'failed', error = ?, completed_at = ? WHERE id = ?",
                        ("stuck - auto-failed by cleanup_retirement", now, tid),
                    )
                    # Insert a bot_audit record in the same transaction to avoid DB lock
                    cur.execute(
                        "INSERT INTO bot_audit (user, action, details) VALUES (?, ?, ?)",
                        ("system", "cleanup_fail_task", f"task={tid}"),
                    )
                else:
                    # reset so executor can pick it up again, increment attempts
                    logger.info("Resetting task %s to pending for retry (attempts=%s)", tid, attempts)
                    cur.execute(
                        "UPDATE llm_tasks SET status = 'pending', attempts = attempts + 1, started_at = NULL, last_attempt_at = ? WHERE id = ?",
                        (now, tid),
                    )
                    cur.execute(
                        "INSERT INTO bot_audit (user, action, details) VALUES (?, ?, ?)",
                        ("system", "cleanup_reset_task", f"task={tid}"),
                    )
            break
        except sqlite3.OperationalError as e:
            if 'locked' in str(e).lower():
                logger.warning("Database locked when processing task %s, retrying...", tid)
                retry -= 1
                time.sleep(0.5)
                continue
            else:
                raise
    else:
        logger.error("Failed to update task %s due to persistent DB lock", tid)


def drain_executor_once():
    # Best-effort: import executor and run drain to move tasks along
    try:
        from scripts.executor_daemon import ExecutorDaemon

        ed = ExecutorDaemon(dry_run=False)
        ed.run_once(max_tasks=EXECUTOR_MAX_TASKS)
    except Exception as e:
        logger.exception("Executor drain failed: %s", e)


def retry_publishes_once():
    try:
        from scripts.retry_failed_publishes import run_once as retry_once

        retry_once()
    except Exception as e:
        logger.exception("Retry publishes failed: %s", e)


def run_once(dry_run: bool = False, db_path: str | None = None, no_drain: bool = False, no_retry: bool = False):
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting cleanup_retirement run (dry_run=%s, db_path=%s, no_drain=%s, no_retry=%s)", dry_run, db_path, no_drain, no_retry)

    db = DatabaseManager(db_path=Path(db_path) if db_path else None)

    stale = find_stale_tasks(db)
    logger.info("Found %d stale tasks", len(stale))
    for r in stale:
        if dry_run:
            logger.info("Would act on task: %s", r)
        else:
            retire_or_reset_task(db, r)

    # Run executor drain to pick up any reset tasks
    if not dry_run and not no_drain:
        drain_executor_once()

    if not dry_run and not no_retry:
        retry_publishes_once()

    logger.info("Cleanup_retirement run complete")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Cleanup and retirement run")
    parser.add_argument("--dry-run", action="store_true", help="Do not modify database; just report")
    parser.add_argument("--db-path", help="Custom path to sqlite DB")
    parser.add_argument("--no-drain", action="store_true", help="Do not run executor drain (for testing)")
    parser.add_argument("--no-retry", action="store_true", help="Do not run retry publishes (for testing)")
    args = parser.parse_args()

    run_once(dry_run=args.dry_run, db_path=args.db_path, no_drain=args.no_drain, no_retry=args.no_retry)

