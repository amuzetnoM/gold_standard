import time
from pathlib import Path
from datetime import datetime, timedelta

import pytest

import importlib.util
import sys
from pathlib import Path
# ensure project root is on sys.path so db_manager can be imported
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from db_manager import DatabaseManager

# load scripts/cleanup_retirement.py as module (pytest may not have scripts package on path)
src = importlib.util.spec_from_file_location("cleanup_retirement", str(Path(__file__).resolve().parents[1] / "scripts" / "cleanup_retirement.py"))
cr = importlib.util.module_from_spec(src)
src.loader.exec_module(cr)



def test_find_and_reset_stale_task(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    db = DatabaseManager(db_path=db_path)

    # Insert a stale task
    from datetime import timezone
    started_at = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    with db._get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO llm_tasks (document_path, prompt, status, attempts, started_at) VALUES (?, ?, ?, ?, ?)",
            ("/tmp/foo.md", "prompt", "started", 0, started_at),
        )
        task_id = cur.lastrowid

    # Run cleanup by calling script as subprocess with no drain/retry
    import subprocess
    cmd = [sys.executable, str(Path(__file__).resolve().parents[1] / "scripts" / "cleanup_retirement.py"), "--db-path", str(db_path), "--no-drain", "--no-retry"]
    subprocess.check_call(cmd)

    # Verify task was reset to pending and attempts incremented
    with db._get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT status, attempts FROM llm_tasks WHERE id = ?", (task_id,))
        row = cur.fetchone()
        assert row["status"] == "pending"
        assert row["attempts"] == 1
