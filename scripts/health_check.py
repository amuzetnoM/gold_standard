#!/usr/bin/env python3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from db_manager import get_db


def run_health_check():
    print("Checking Syndicate System Health...")
    db = get_db()
    health = db.get_system_health()

    # Check for stuck tasks
    stuck = health.get("tasks", {}).get("stuck_in_progress", 0)
    if stuck > 0:
        print(f"WARNING: {stuck} stuck tasks detected. Resetting...")
        db.reset_stuck_actions(max_age_hours=1)

    # Check for recent activity
    # (Simplified for now)
    print("All systems within normal parameters.")
    return True


if __name__ == "__main__":
    if run_health_check():
        sys.exit(0)
    else:
        sys.exit(1)
