import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from db_manager import DatabaseManager

if __name__ == "__main__":
    db = DatabaseManager()
    print("Before delete:", db.get_action_stats())
    with db._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM action_insights")
        conn.commit()
    print("After delete:", db.get_action_stats())
