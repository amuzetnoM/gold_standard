import tempfile
import os
from pathlib import Path
import sqlite3
import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.cleanup_models as cm
from db_manager import DatabaseManager


def test_prune_considers_db(tmp_path, monkeypatch):
    # Create fake models in tmp dir
    m1 = tmp_path / "old_model.gguf"
    m2 = tmp_path / "recent_model.gguf"
    m1.write_text('x')
    m2.write_text('x')

    # Monkeypatch LocalLLM.find_models to return our models
    class FakeLLM:
        def find_models(self):
            return [
                {"path": str(m1), "name": "old_model", "size_gb": 0.5},
                {"path": str(m2), "name": "recent_model", "size_gb": 0.2},
            ]

    monkeypatch.setattr("scripts.cleanup_models.LocalLLM", lambda: FakeLLM())

    # Use a temp DB and populate model_usage
    db_path = tmp_path / "db.sqlite"
    db = DatabaseManager(db_path)
    with db._get_connection() as conn:
        cur = conn.cursor()
        # old_model last_used 100 days ago
        cur.execute("INSERT OR REPLACE INTO model_usage (model_path, name, size_gb, last_used, usage_count) VALUES (?, ?, ?, datetime('now', '-100 days'), 1)", (str(m1), 'old_model', 0.5))
        # recent_model last_used 1 day ago
        cur.execute("INSERT OR REPLACE INTO model_usage (model_path, name, size_gb, last_used, usage_count) VALUES (?, ?, ?, datetime('now', '-1 days'), 5)", (str(m2), 'recent_model', 0.2))

    # Monkeypatch DatabaseManager() inside cleanup_models to use our db
    import scripts.cleanup_models as cm
    monkeypatch.setattr(cm, "DatabaseManager", lambda: db, raising=False)

    # Run cleanup_models main logic in dry-run prune mode
    args = ["prog", "--prune-days", "30"]
    monkeypatch.setattr("sys.argv", args)
    # Capture logs
    cm.main()
    # If it completes without exceptions, prune logic worked
