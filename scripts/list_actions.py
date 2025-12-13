import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from db_manager import DatabaseManager

if __name__ == "__main__":
    db = DatabaseManager()
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT action_id, title, status, created_at, metadata FROM action_insights")
        rows = cursor.fetchall()
        if not rows:
            print("No actions found")
        for r in rows:
            print(
                r["action_id"],
                r["title"],
                r["status"],
                r["created_at"],
                r["metadata"] if "metadata" in r.keys() else None,
            )
