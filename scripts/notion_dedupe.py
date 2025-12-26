#!/usr/bin/env python3
"""Detect and (optionally) archive duplicate Notion pages in the configured database.

Usage:
    python scripts/notion_dedupe.py --dry-run            # list duplicates only
    python scripts/notion_dedupe.py --archive --yes     # archive duplicates (irreversible)

Behavior:
 - Groups pages by normalized Title (case-insensitive).
 - Keeps the most recently edited page in each duplicate group and archives the rest.
 - Backs up the duplicate page metadata to output/notion_duplicates_backup.json before archiving.
"""
from pathlib import Path
import json
import sys
import argparse
import logging
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from scripts.notion_publisher import NotionConfig
    from notion_client import Client
except Exception as e:
    print("Notion client not available or import failed:", e)
    print("Install notion-client and ensure NOTION_API_KEY/NOTION_DATABASE_ID are set in .env or environment")
    raise

from db_manager import get_db

OUT = PROJECT_ROOT / "output" / "notion_duplicates_backup.json"

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("notion_dedupe")


def fetch_all_pages(client: Client, database_id: str):
    """Yield pages from the database (handles pagination)."""
    pages = []
    payload = {
        "page_size": 100,
    }
    start = None
    while True:
        if start:
            payload["start_cursor"] = start
        resp = client.databases.query(database_id=database_id, **payload)
        pages.extend(resp.get("results", []))
        if not resp.get("has_more"):
            break
        start = resp.get("next_cursor")
    return pages


def extract_title(page: dict) -> str:
    try:
        props = page.get("properties", {})
        name = props.get("Name", {}).get("title", [{}])[0].get("plain_text", "")
        return name or page.get("id")
    except Exception:
        return page.get("id")


def normalize_title(t: str) -> str:
    # Lowercase and normalize spacing; optionally strip trailing Notion slug fragments
    s = (t or "").strip().lower()
    s = " ".join(s.split())
    return s


def main(dry_run: bool = True, do_archive: bool = False, confirm: bool = False):
    cfg = NotionConfig.from_env()
    client = Client(auth=cfg.api_key)
    db = get_db()

    pages = fetch_all_pages(client, cfg.database_id)
    log.info("Fetched %s pages from Notion database", len(pages))

    groups = {}
    for p in pages:
        title = extract_title(p)
        key = normalize_title(title)
        groups.setdefault(key, []).append(p)

    dup_groups = {k: v for k, v in groups.items() if len(v) > 1}
    log.info("Found %s duplicate title groups", len(dup_groups))

    if not dup_groups:
        print("No duplicate titles found in Notion database.")
        return 0

    OUT.parent.mkdir(parents=True, exist_ok=True)
    backup = []

    for title_key, items in dup_groups.items():
        # Sort by last_edited_time (newest first)
        def ts(p):
            return p.get("last_edited_time") or p.get("created_time") or ""

        items_sorted = sorted(items, key=ts, reverse=True)
        keep = items_sorted[0]
        remove = items_sorted[1:]

        print(f"\nDuplicate group: '{extract_title(keep)}' -> keep {keep['id']} (edited {keep.get('last_edited_time')})")
        for r in remove:
            print(f"   will remove {r['id']} (edited {r.get('last_edited_time')}) -> {r.get('url')}")
            backup.append({
                "keep": keep['id'],
                "remove": r['id'],
                "remove_url": r.get('url'),
                "title": extract_title(r),
                "created_time": r.get('created_time'),
                "last_edited_time": r.get('last_edited_time'),
            })

    # Write backup
    with open(OUT, "w") as f:
        json.dump({"timestamp": datetime.utcnow().isoformat(), "dups": backup}, f, indent=2)

    print(f"\nBacked up {len(backup)} duplicate entries to {OUT}")

    if do_archive:
        if not confirm:
            print("Archive requested but not confirmed. Re-run with --yes to proceed.")
            return 2

        for entry in backup:
            rid = entry['remove']
            try:
                print(f"Archiving page {rid} -> {entry['remove_url']}")
                client.pages.update(page_id=rid, archived=True)
            except Exception as e:
                log.exception("Failed to archive page %s: %s", rid, e)
                continue
            # Remove DB sync record (best-effort)
            try:
                db.clear_sync_for_file(entry.get('remove'))
            except Exception:
                pass
        print("Archiving complete")

    else:
        print("Dry run complete. No changes made. Re-run with --archive --yes to archive duplicates.")

    return 0


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--dry-run', action='store_true', default=False, help='Perform dry-run (default)')
    p.add_argument('--archive', action='store_true', help='Archive duplicate pages')
    p.add_argument('--yes', action='store_true', help='Confirm destructive operations (required with --archive)')
    args = p.parse_args()
    if args.archive:
        sys.exit(main(dry_run=False, do_archive=True, confirm=args.yes))
    else:
        sys.exit(main(dry_run=True, do_archive=False))
