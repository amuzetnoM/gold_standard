#!/usr/bin/env python3
"""Cleanup Notion pages for files matching repository ignore patterns.
This script archives matching Notion pages and removes their notion_sync DB entries.
Run from project root: python scripts/notion_cleanup_remove_patterns.py
"""
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from notion_client import Client
except Exception:
    Client = None

from db_manager import get_db
from scripts.notion_publisher import NotionConfig, NotionPublisher, IGNORE_PATTERNS


def main(dry_run: bool = False):
    config = NotionConfig.from_env()
    if Client is None:
        print("notion-client package not available; cannot perform remote cleanup")
        return
    pub = NotionPublisher(config=config)
    db = get_db()

    synced = db.get_all_synced_files()
    to_remove = []
    for row in synced:
        file_path = row.get("file_path") or ""
        fname = Path(file_path).name.lower()
        matched = False
        for p in IGNORE_PATTERNS:
            if p.lower() in fname or p.lower() in str(file_path).lower():
                matched = True
                break
        if matched:
            to_remove.append(row)

    print(f"Found {len(to_remove)} Notion pages matching ignore patterns")

    for r in to_remove:
        page_id = r.get("notion_page_id")
        file_path = r.get("file_path")
        url = r.get("notion_url")
        name = Path(file_path).name
        try:
            if dry_run:
                print(f"DRY RUN: would archive {name} -> {url} (page_id={page_id})")
            else:
                print(f"Archiving {name} -> {url} (page_id={page_id})")
                try:
                    pub.client.pages.update(page_id=page_id, archived=True)
                except Exception as e:
                    print(f"  Archive failed for {name}: {e}")
                # Remove DB record
                try:
                    cleared = db.clear_sync_for_file(file_path)
                    if cleared:
                        print(f"  Removed DB sync record for {name}")
                except Exception as e:
                    print(f"  Failed to clear DB record for {name}: {e}")
        except Exception as e:
            print(f"Error processing {name}: {e}")

    print("Cleanup complete")


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()
    main(dry_run=args.dry_run)
