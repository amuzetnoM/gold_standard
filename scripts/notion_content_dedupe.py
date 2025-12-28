#!/usr/bin/env python3
"""Detect duplicate Notion pages by identical content (block text)."""
from pathlib import Path
import sys
import json
import logging
from collections import defaultdict
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from notion_client import Client
    from scripts.notion_publisher import NotionConfig
except Exception as e:
    print("Notion client not available or failed import:", e)
    raise

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("notion_content_dedupe")

OUT = PROJECT_ROOT / "output" / "notion_content_duplicates.json"


def fetch_workspace_pages(client):
    pages = {}
    start = None
    while True:
        kwargs = {"page_size": 100}
        if start:
            kwargs["start_cursor"] = start
        resp = client.search(**kwargs)
        for r in resp.get("results", []):
            if r.get("object") == "page":
                pages[r["id"]] = r
        if not resp.get("has_more"):
            break
        start = resp.get("next_cursor")
    return pages


def fetch_block_text(client, block_id):
    """Recursively fetch text content from a block and its descendants."""
    texts = []

    def fetch_children(bid):
        start = None
        while True:
            kwargs = {"block_id": bid, "page_size": 100}
            if start:
                kwargs["start_cursor"] = start
            resp = client.blocks.children.list(**kwargs)
            for ch in resp.get("results", []):
                t = extract_text_from_block(ch)
                if t:
                    texts.append(t)
                if ch.get("has_children"):
                    fetch_children(ch["id"])
            if not resp.get("has_more"):
                break
            start = resp.get("next_cursor")

    # Page is a top-level block with id; fetch top-level children
    fetch_children(block_id)
    return "\n".join(texts)


def extract_text_from_block(block):
    # Extract text for common types
    t = None
    typ = block.get("type")
    if not typ:
        return ""
    content = block.get(typ)
    if not content:
        return ""
    if isinstance(content, dict):
        if "text" in content:  # legacy
            parts = content.get("text", [])
            t = " ".join(p.get("plain_text", "") for p in parts)
        elif "rich_text" in content:
            parts = content.get("rich_text", [])
            t = " ".join(p.get("plain_text", "") for p in parts)
        elif "paragraph" in content and isinstance(content.get("paragraph"), dict):
            parts = content.get("paragraph", {}).get("rich_text", [])
            t = " ".join(p.get("plain_text", "") for p in parts)
        else:
            # fallback: try common keys
            for k in ("rich_text", "text", "title"):
                if k in content:
                    parts = content.get(k, [])
                    t = " ".join(p.get("plain_text", "") for p in parts)
                    break
    if not t:
        t = ""
    return t


def normalize_text(s: str) -> str:
    if not s:
        return ""
    s = s.lower()
    s = s.replace("\n", " ")
    import re

    s = re.sub(r"\s+", " ", s).strip()
    return s


def main(dry_run=True, do_archive=False, confirm=False):
    cfg = NotionConfig.from_env()
    client = Client(auth=cfg.api_key)

    pages = fetch_workspace_pages(client)
    log.info("Fetched %s pages", len(pages))

    content_map = defaultdict(list)

    for pid, page in pages.items():
        try:
            text = fetch_block_text(client, pid)
        except Exception as e:
            log.exception("Failed to fetch blocks for page %s: %s", pid, e)
            continue
        norm = normalize_text(text)
        if not norm:
            continue
        import hashlib

        h = hashlib.sha256(norm.encode("utf-8")).hexdigest()
        content_map[h].append({"id": pid, "title": page.get("properties", {}).get("Name", {}).get("title", [{}])[0].get("plain_text", ""), "last_edited_time": page.get("last_edited_time"), "url": page.get("url")})

    duplicates = {h: v for h, v in content_map.items() if len(v) > 1}
    log.info("Found %s exact-content duplicate groups", len(duplicates))

    backup = []
    for h, group in duplicates.items():
        # keep most recently edited
        keep = sorted(group, key=lambda x: x.get("last_edited_time") or "", reverse=True)[0]
        remove = [g for g in group if g["id"] != keep["id"]]
        for r in remove:
            backup.append({"keep": keep, "remove": r})
            print(f"Duplicate content group: keep {keep['id']} remove {r['id']} (title: {r['title']})")

    if backup:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        with open(OUT, "w") as f:
            json.dump({"timestamp": datetime.utcnow().isoformat(), "dups": backup}, f, indent=2)
        print(f"Backed up {len(backup)} duplicate metadata rows to {OUT}")

    else:
        print("No exact-content duplicates found across workspace pages.")

    if do_archive and backup:
        if not confirm:
            print("Archive requested but not confirmed. Re-run with --yes to proceed.")
            return 2
        for entry in backup:
            rid = entry['remove']['id']
            try:
                print(f"Archiving {rid} -> {entry['remove']['url']}")
                client.pages.update(page_id=rid, archived=True)
            except Exception as e:
                log.exception("Archive failed for %s: %s", rid, e)
                continue
        print("Archiving complete")

    return 0


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument('--dry-run', action='store_true', default=False)
    p.add_argument('--archive', action='store_true')
    p.add_argument('--yes', action='store_true')
    args = p.parse_args()
    if args.archive:
        sys.exit(main(dry_run=False, do_archive=True, confirm=args.yes))
    else:
        sys.exit(main(dry_run=True, do_archive=False))
