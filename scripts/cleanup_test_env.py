import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import shutil

from db_manager import DatabaseManager

print("Starting cleanup test environment...")

# Remove output files
out_dir = Path("output")
if out_dir.exists():
    for p in out_dir.glob("*"):
        try:
            if p.is_file():
                p.unlink()
            elif p.is_dir():
                shutil.rmtree(p)
        except Exception as e:
            print(f"Failed to remove {p}: {e}")
print("Output directory cleaned.")

# Backup DB & clear action_insights
from db_manager import DB_PATH

bak = DB_PATH.with_suffix(".bak")
try:
    shutil.copy(DB_PATH, bak)
    print(f"Backed up DB to {bak.name}")
except Exception as e:
    print(f"Failed to backup DB: {e}")

# Clear action_insights
try:
    db = DatabaseManager()
    print("Action stats BEFORE:", db.get_action_stats())
    with db._get_connection() as conn:
        conn.execute("DELETE FROM action_insights")
        conn.commit()
    print("Action stats AFTER:", db.get_action_stats())
except Exception as e:
    print("Error clearing action_insights:", e)

print("Cleanup complete.")
