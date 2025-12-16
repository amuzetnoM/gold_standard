#!/usr/bin/env python3
"""Inject a synthetic report containing clear action items for E2E smoke tests."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.insights_engine import InsightsExtractor
from main import Config, setup_logging
from db_manager import get_db


def main():
    cfg = Config()
    logger = setup_logging(cfg)

    reports_dir = Path(cfg.OUTPUT_DIR) / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    filename = reports_dir / "test_action_report.md"
    content = """
# Test Action Report

## Action Items

- Monitor GOLD: Watch for break above 2050; if occurs, consider LONG exposure (monitor GOLD for breakout).
- Research: Prepare a brief on GDX positioning and catalysts for next trading session (research GDX catalysts).
- Fetch Data: Retrieve latest COT reports and positions for GOLD (data_fetch COT GOLD).

--
This report is synthetic for testing.
"""

    filename.write_text(content, encoding="utf-8")
    print(f"Wrote test report: {filename}")

    extractor = InsightsExtractor(cfg, logger)
    actions = extractor.extract_actions(content, filename.name)

    if actions:
        db = get_db()
        saved = db.save_action_insights([a.__dict__ for a in actions])
        if saved != len(actions):
            print(f"Warning: Expected to save {len(actions)} actions, but saved {saved} (check logs for details)")
        else:
            print(f"Saved {saved} actions to DB")
    else:
        print("No actions extracted (unexpected)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())