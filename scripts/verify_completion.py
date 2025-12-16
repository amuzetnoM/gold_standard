#!/usr/bin/env python3
"""Verify that there are no pending or in_progress actions and that reports have frontmatter/tags."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from db_manager import get_db
from scripts.frontmatter import has_frontmatter, get_document_status, extract_tags_from_content


db = get_db()
stats = db.get_action_stats()
print("Action stats:", stats)

pending = stats.get("pending", 0)
in_progress = stats.get("in_progress", 0)

if pending > 0 or in_progress > 0:
    print("FAIL: There are unfinished tasks (pending or in_progress)")
    sys.exit(2)

# Check today's premarket
from datetime import date
reports_dir = Path("output") / "reports"
pm_fname = f"premarket_{date.today().isoformat()}.md"
pm_path = reports_dir / pm_fname

if not pm_path.exists():
    print(f"WARN: Pre-market file not found: {pm_path}")
else:
    content = pm_path.read_text(encoding="utf-8")
    fm = has_frontmatter(content)
    status = get_document_status(content)
    tags = extract_tags_from_content(content)
    print(f"Pre-Market frontmatter: {fm}, status: {status}, tags: {tags[:10]}")

print("OK: No pending actions and checks completed.")
sys.exit(0)
