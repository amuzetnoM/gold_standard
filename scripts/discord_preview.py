#!/usr/bin/env python3
"""Render and optionally send sample digest messages for testing.

Usage:
  python3 scripts/discord_preview.py --webhook <url> --hours 24 --send

If --send is omitted, the script will print the embed and plaintext to stdout.
"""
import argparse
import os
import json
import hashlib
from pathlib import Path

from src.digest_bot.daily_report import build_structured_report
from src.digest_bot.discord import templates as discord_templates
from db_manager import DatabaseManager
from scripts.notifier import send_discord


def main():
    parser = argparse.ArgumentParser(description='Preview or send digest embeds')
    parser.add_argument('--webhook', help='Webhook URL to send to')
    parser.add_argument('--hours', type=int, default=24)
    parser.add_argument('--send', action='store_true', help='Actually send to webhook')
    parser.add_argument('--dry-run', action='store_true', help='Print only')
    args = parser.parse_args()

    db = DatabaseManager()
    structured = build_structured_report(db, hours=args.hours)
    embed = discord_templates.build_daily_embed(structured)
    text = discord_templates.plain_daily_text(structured)

    print('--- EMBED JSON ---')
    print(json.dumps(embed, indent=2, default=str))
    print('\n--- PLAINTEXT ---')
    print(text)

    if args.send:
        # dedupe check
        webhook = args.webhook or os.getenv('DISCORD_WEBHOOK_URL') or 'default'
        try:
            payload_key = json.dumps(embed, sort_keys=True, default=str)
            fingerprint = hashlib.sha256(payload_key.encode('utf-8')).hexdigest()
        except Exception:
            fingerprint = None

        if fingerprint and db.was_discord_recent(webhook, fingerprint, minutes=10):
            print('Skipping send: recent duplicate fingerprint')
            return 0

        ok = send_discord(None, webhook_url=args.webhook, embed=embed)
        if ok:
            print('Sent successfully')
            if fingerprint:
                db.record_discord_send(webhook, fingerprint, hashlib.sha256(payload_key.encode('utf-8')).hexdigest())
        else:
            print('Send failed')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
