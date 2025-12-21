#!/usr/bin/env python3
"""Cleanup unused GGUF models to reclaim disk space.

By default runs in dry-run mode and prints candidates for deletion. Use
--confirm to actually delete files.

Environment:
    KEEP_LOCAL_MODELS - comma-separated model names to keep (overrides --keep)
"""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path
from typing import List

from scripts.local_llm import LocalLLM

LOG = logging.getLogger("cleanup_models")

KEEP_ENV = [m.strip() for m in os.environ.get("KEEP_LOCAL_MODELS", "").split(",") if m.strip()]


def candidates_to_remove(models: List[dict], keep_list: List[str]) -> List[dict]:
    keep_lower = [k.lower() for k in keep_list]
    to_remove = []
    for m in models:
        name = m.get("name", "") or Path(m.get("path", "")).stem
        if any(k in name.lower() for k in keep_lower):
            continue
        to_remove.append(m)
    return to_remove


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirm", action="store_true", help="Actually delete candidate models")
    parser.add_argument("--keep", type=str, help="Comma-separated model names to keep (overrides env KEEP_LOCAL_MODELS)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

    keep = [k.strip() for k in args.keep.split(",")] if args.keep else KEEP_ENV

    llm = LocalLLM()
    models = llm.find_models()
    if not models:
        LOG.info("No GGUF models found")
        return

    candidates = candidates_to_remove(models, keep)

    if not candidates:
        LOG.info("No models match deletion criteria (keep=%s).", keep)
        return

    LOG.info("Models found: %s", [m.get('name') for m in models])
    LOG.info("Candidates for removal: %s", [m.get('name') for m in candidates])

    if not args.confirm:
        LOG.info("Dry-run mode: no files will be deleted. Re-run with --confirm to delete files.")
        for m in candidates:
            LOG.info("Would remove: %s (path=%s, size_gb=%.3f)", m.get('name'), m.get('path'), m.get('size_gb', 0.0))
        return

    # Confirmed: perform deletion
    for m in candidates:
        p = Path(m.get("path"))
        try:
            p.unlink()
            LOG.info("Deleted model: %s", p)
        except Exception as e:
            LOG.exception("Failed to delete %s: %s", p, e)


if __name__ == "__main__":
    main()
