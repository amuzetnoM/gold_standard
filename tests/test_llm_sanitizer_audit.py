import os
import sqlite3
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from db_manager import get_db
from scripts.llm_worker import process_task
from main import Config


class BadPriceProvider:
    class Resp:
        def __init__(self, text):
            self.text = text

    def generate_content(self, prompt: str):
        # Returns a report that incorrectly cites gold price as $2345
        return BadPriceProvider.Resp("Current Gold Price: $2345\nMarket commentary..")


def test_sanitizer_audit_and_flagging(monkeypatch, tmp_path):
    # Use isolated DB per test to avoid flakiness
    test_db = tmp_path / "gs_sanitizer.db"
    monkeypatch.setenv("GOLD_STANDARD_TEST_DB", str(test_db))

    # Prepare report with canonical value $4300
    rpt = tmp_path / "sanitizer_test.md"
    rpt.write_text("# Sanitizer Test\n")

    db = get_db()
    task_id = db.add_llm_task(str(rpt), prompt="""CANONICAL VALUES\n* GOLD: $4300\n""", task_type="generate")

    # Force low flag threshold to trigger flagging
    monkeypatch.setenv("LLM_SANITIZER_FLAG_THRESHOLD", "1")

    # Patch worker provider
    import scripts.llm_worker as worker_mod

    monkeypatch.setattr(worker_mod, "create_llm_provider", lambda cfg, log: BadPriceProvider())

    # Claim and process
    tasks = db.claim_llm_tasks(limit=1)
    assert tasks
    cfg = Config()
    process_task(tasks[0], cfg)

    # Check sanitizer audit recorded
    conn = sqlite3.connect(str(db.db_path))
    cur = conn.cursor()
    cur.execute("SELECT corrections, notes FROM llm_sanitizer_audit WHERE task_id = ? ORDER BY id DESC LIMIT 1", (tasks[0]["id"],))
    row = cur.fetchone()
    conn.close()

    assert row is not None and row[0] >= 1

    # Task should be flagged since we set threshold to 1
    conn = sqlite3.connect(str(db.db_path))
    cur = conn.cursor()
    cur.execute("SELECT status FROM llm_tasks WHERE id = ?", (tasks[0]["id"],))
    status = cur.fetchone()[0]
    conn.close()

    assert status == "flagged"
