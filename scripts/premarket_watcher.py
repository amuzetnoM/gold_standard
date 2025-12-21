#!/usr/bin/env python3
"""Premarket Watcher: ensures a pre-market plan exists for today and generates it if missing.
Runs as a simple long-lived agent (can be managed by systemd).
"""
import time
import datetime
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from db_manager import get_db
from scripts.pre_market import generate_premarket
from main import Config, setup_logging

CHECK_INTERVAL = int(__import__("os").environ.get("PREMARKET_WATCH_INTERVAL", "300"))  # seconds


def main():
    config = Config()
    logger = setup_logging(config)
    logger.info("Starting premarket_watcher agent")

    while True:
        try:
            today = datetime.date.today().isoformat()
            db = get_db()
            # Also consider the filesystem: if the premarket file exists, treat it as present.
            report_path = Path(config.OUTPUT_DIR) / "reports" / f"premarket_{today}.md"
            file_exists = report_path.exists()
            if not (file_exists or db.has_premarket_for_date(today)):
                logger.info(f"Premarket missing for {today} - generating now")
                try:
                    generated_path = generate_premarket(config, logger, model=None, dry_run=False, no_ai=False)
                    logger.info("Premarket generation finished")
                    try:
                        # Persist the generated premarket into the DB so subsequent checks succeed.
                        # generate_premarket returns the written path; if not, fall back to computed path.
                        try:
                            rp = Path(generated_path) if generated_path else report_path
                        except Exception:
                            rp = report_path

                        if rp.exists():
                            try:
                                content = rp.read_text(encoding="utf-8")
                                # Save into DB (will upsert)
                                db.save_premarket_plan(today, content, ai_enabled=True)
                            except Exception:
                                logger.exception("Failed to persist premarket content to DB")
                        # Best-effort marker method for older DBs
                        try:
                            if hasattr(db, 'set_premarket_generated'):
                                db.set_premarket_generated(today)
                        except Exception:
                            pass
                    except Exception:
                        # set_premarket_generated may not exist; it's best-effort
                        pass

                    # Post today's premarket and journal to the admin reports channel
                    try:
                        import subprocess
                        script = Path(__file__).parent / "post_reports_to_admin.py"
                        logger.info("Posting reports to admin channel via %s", script)
                        subprocess.run([sys.executable, str(script)], check=False)
                    except Exception as e:
                        logger.warning("Failed to post reports to admin: %s", e)
                except Exception as e:
                    logger.error(f"Failed to generate premarket: {e}", exc_info=True)
            else:
                logger.debug(f"Premarket already exists for {today}")
        except Exception as e:
            logger.error(f"Watcher loop error: {e}", exc_info=True)

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
