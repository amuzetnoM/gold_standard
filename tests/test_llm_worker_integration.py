import os
import sys
import time
import pytest
from pathlib import Path

# Ensure project root is on path for tests
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from db_manager import get_db
from scripts.llm_worker import process_task
from main import Config


class DummyProvider:
    class Resp:
        def __init__(self, text):
            self.text = text

    def generate_content(self, prompt: str):
        return DummyProvider.Resp("Generated content: canonical price enforcement test.")


def test_worker_process_generate_and_insights(tmp_path, monkeypatch):
    # Use an isolated DB per test to avoid cross-test interference
    test_db = tmp_path / "gs_test.db"
    monkeypatch.setenv("GOLD_STANDARD_TEST_DB", str(test_db))

    # Prepare an isolated report file
    rpt = tmp_path / "int_test_premarket.md"
    rpt.write_text("# INT TEST PLACEHOLDER\n")

    db = get_db()
    # Ensure DB is reachable
    assert db is not None

    # Enqueue a generate task
    task_id = db.add_llm_task(str(rpt), prompt="Test prompt", task_type="generate")
    assert task_id is not None

    # Patch create_llm_provider to return our dummy provider
    monkeypatch.setenv("LLM_ASYNC_QUEUE", "1")
    # Monkeypatch the symbol used by the worker module directly so process_task uses DummyProvider
    import scripts.llm_worker as worker_mod
    monkeypatch.setattr(worker_mod, "create_llm_provider", lambda cfg, log: DummyProvider())

    # Claim the task and process it using process_task
    tasks = db.claim_llm_tasks(limit=1)
    assert tasks, "Expected at least one task claimed"

    cfg = Config()
    process_task(tasks[0], cfg)

    # Validate task completed
    row = db.get_llm_task(tasks[0]["id"]) if hasattr(db, "get_llm_task") else None
    # Fallback: read from table directly
    # Wait for DB update
    time.sleep(0.2)
    import sqlite3

    conn = sqlite3.connect(str(db.db_path))
    cur = conn.cursor()
    cur.execute("SELECT status, response FROM llm_tasks WHERE id = ?", (tasks[0]["id"],))
    r = cur.fetchone()
    conn.close()

    assert r and r[0] == "completed"
    assert r[1] and "Generated content" in r[1]

    # Enqueue an insights task
    rpt2 = tmp_path / "int_test_insights.md"
    rpt2.write_text("# INT TEST INSIGHTS\nSome market notes\n")
    task_id2 = db.add_llm_task(str(rpt2), prompt="", task_type="insights")

    tasks2 = db.claim_llm_tasks(limit=1)
    assert tasks2
    process_task(tasks2[0], cfg)

    # Check insights task completed
    conn = sqlite3.connect(str(db.db_path))
    cur = conn.cursor()
    cur.execute("SELECT status, response FROM llm_tasks WHERE id = ?", (tasks2[0]["id"],))
    r2 = cur.fetchone()
    conn.close()

    assert r2 and r2[0] == "completed"
    assert r2[1] and r2[1].startswith("insights:")
