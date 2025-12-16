import sqlite3
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest

from db_manager import DatabaseManager


def test_save_action_insights_with_extra_fields(tmp_path: Path):
    db_file = tmp_path / "test.db"
    db = DatabaseManager(db_path=db_file)

    actions = [
        {
            "action_id": "TST-1",
            "action_type": "research",
            "title": "Research X",
            "description": "Do research",
            "priority": "high",
            "status": "pending",
            "result": "interim",
            "metadata": {"source": "unit_test", "extracted_by": "insights_engine"},
        },
        {
            "action_id": "TST-2",
            "action_type": "data_fetch",
            "title": "Fetch Y",
            "description": "Fetch data",
            "priority": "medium",
            "status": "pending",
            "extra_field": "should be ignored",
            "metadata": {"source": "unit_test"},
        },
    ]

    saved = db.save_action_insights(actions)
    assert saved == 2

    # Verify rows persisted and metadata stored as string
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT action_id, status, metadata FROM action_insights ORDER BY action_id")
        rows = cursor.fetchall()
        assert len(rows) == 2
        for row in rows:
            assert row[1] == "pending"
            assert isinstance(row[2], str)
            assert "unit_test" in row[2]
