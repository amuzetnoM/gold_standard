import sqlite3
from pathlib import Path
import tempfile
import os

import pytest
import sys
from pathlib import Path
# Add project root to path for test imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.offloaded_executor import poll_once, choose_fast_model
import scripts.offloaded_executor as oe


class FakeLLM:
    def __init__(self):
        self.loaded = False
        self.model_name = "fake-mini"

    def find_models(self):
        return [{"path": "/tmp/fake-mini.gguf", "name": "fake-mini", "size_gb": 0.5}]

    def load_model(self, path):
        self.loaded = True
        return True

    def generate(self, prompt, **kwargs):
        return "GENERATED:" + prompt[:50]


def test_poll_once_executes_task(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    # create DB and insert a pending llm task
    import db_manager

    db = db_manager.DatabaseManager(db_path)
    with db._get_connection() as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO llm_tasks (document_path, prompt, status, task_type, priority) VALUES (?, ?, 'pending', 'generate', 'fast')", ("/tmp/doc.md", "Hello small prompt",))

    # Use FakeLLM
    llm = FakeLLM()

    n = poll_once(db, llm, max_tasks=2)
    assert n == 1

    # Verify DB updated
    with db._get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT status, response FROM llm_tasks")
        row = cur.fetchone()
        assert row[0] == 'done'
        assert row[1].startswith('GENERATED:')


def test_choose_fast_model_prefers_mini(monkeypatch):
    class L:
        def find_models(self):
            return [
                {"path": "/models/big.gguf", "name": "big", "size_gb": 10},
                {"path": "/models/mini.gguf", "name": "mini", "size_gb": 0.3},
            ]

    assert choose_fast_model(L()) == "/models/mini.gguf"
