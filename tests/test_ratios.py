import datetime
import logging
import os
import sys

# Ensure project root is on sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import Config, QuantEngine
from db_manager import DatabaseManager, AnalysisSnapshot


def test_gsr_uses_db_fallback(tmp_path):
    db_file = tmp_path / "test_gsr.db"
    db = DatabaseManager(db_path=db_file)

    today = datetime.date.today().isoformat()
    snap = AnalysisSnapshot(date=today, asset="SILVER", price=25.0)
    assert db.save_analysis_snapshot(snap) is True

    cfg = Config()
    logger = logging.getLogger("test")

    # Ensure the QuantEngine sees our test DB as the global DB
    import db_manager

    db_manager._db_manager = db

    qe = QuantEngine(cfg, logger)

    snapshot = {"GOLD": {"price": 2000}}
    out = qe._compute_intermarket_ratios(snapshot)

    assert "RATIOS" in out
    assert out["RATIOS"].get("GSR") == round(2000 / 25.0, 2)


def test_gsr_not_computed_when_no_data(tmp_path):
    # No DB fallback and missing silver: GSR should not be present
    cfg = Config()
    logger = logging.getLogger("test")
    qe = QuantEngine(cfg, logger)

    snapshot = {"GOLD": {"price": None}}
    out = qe._compute_intermarket_ratios(snapshot)

    assert "RATIOS" not in out or out.get("RATIOS", {}).get("GSR") is None
