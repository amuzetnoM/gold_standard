#!/usr/bin/env python3
import os
import json
import logging
from typing import Optional, Dict, Any

try:
    import requests
except ImportError:
    requests = None


def send_discord(message: str = None, webhook_url: Optional[str] = None, embed: Optional[Dict[str, Any]] = None) -> bool:
    """Send a simple message to a Discord webhook.

    Returns True on success, False on failure. Uses DISCORD_WEBHOOK_URL from
    environment when webhook_url is not provided.
    """
    url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
    if not url:
        logging.warning("No Discord webhook URL configured; skipping alert: %s", message)
        return False

    # Build webhook payload. When `embed` is provided, prefer sending an embed
    # (Discord webhook accepts both `content` and `embeds`). We create a single
    # embed list to keep payload minimal.
    payload = {}
    if embed:
        payload["embeds"] = [embed]
        if message:
            payload["content"] = message
    else:
        payload["content"] = message or ""

    if requests is None:
        logging.warning("requests not installed; cannot send webhook: %s", message)
        return False

    # Implement simple retries with exponential backoff
    import time
    attempts = 3
    delay = 1.0
    for attempt in range(1, attempts + 1):
        try:
            r = requests.post(url, json=payload, timeout=10)
            # Support simple fake responses used in tests (may expose raise_for_status)
            if hasattr(r, "status_code"):
                if r.status_code in (200, 204):
                    logging.info("Sent alert to Discord webhook (attempt %s)", attempt)
                    return True
                logging.warning("Discord webhook returned HTTP %s on attempt %s: %s", getattr(r, "status_code", None), attempt, getattr(r, "text", ""))
            elif hasattr(r, "raise_for_status"):
                try:
                    r.raise_for_status()
                    logging.info("Sent alert to Discord webhook (attempt %s)", attempt)
                    return True
                except Exception as rr_e:
                    logging.warning("Discord webhook raised on attempt %s: %s", attempt, rr_e)
            else:
                logging.warning("Discord webhook returned unexpected response object on attempt %s: %r", attempt, r)
        except Exception as e:
            logging.exception("Failed to send Discord webhook on attempt %s: %s", attempt, e)

        if attempt < attempts:
            time.sleep(delay)
            delay *= 2

    logging.error("Discord webhook failed after %s attempts", attempts)
    return False
