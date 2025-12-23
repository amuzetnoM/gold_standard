import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

# Ensure project root on path (consistent with other tests)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.digest_bot.daily_report import build_report
from db_manager import DatabaseManager


def make_db_with_data(tmp_path: Path) -> DatabaseManager:
    db_path = tmp_path / "gstest.db"
    db = DatabaseManager(db_path)
    # Insert a couple of tasks and sanitizer audits
    with db._get_connection() as conn:
        cur = conn.cursor()
        # Completed task
        cur.execute("INSERT INTO llm_tasks (document_path, prompt, status, completed_at) VALUES (?, ?, 'completed', ?)",
                    ("output/reports/premarket/premarket_2025-01-01.md", "prompt1", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")))
        # Flagged task
        cur.execute("INSERT INTO llm_tasks (document_path, prompt, status, completed_at) VALUES (?, ?, 'flagged', ?)",
                    ("output/reports/premarket/premarket_2025-01-01_flagged.md", "prompt2", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")))
        # Sanitizer audit
        cur.execute("INSERT INTO llm_sanitizer_audit (task_id, corrections, notes, created_at) VALUES (?, ?, ?, ?)",
                    (1, 2, "corrected numeric values", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")))
    return db


def test_build_report_contains_sections(tmp_path: Path):
    db = make_db_with_data(tmp_path)
    report = build_report(db, hours=48)
    assert "LLM Daily Report" in report
    assert "Queue length" in report
    assert "Sanitizer corrections" in report
    assert "Flagged tasks" in report
    assert "Recent sanitizer audits" in report
