import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.post_system_health import build_embed


def test_build_embed_ok():
    services = [
        {"name": "svc1", "active": "active", "since": "2025-12-21 10:00:00"},
        {"name": "svc2", "active": "inactive", "since": None},
    ]
    db_stats = {"pending": 2, "started": 0, "failed_24": 1, "failed_total": 5}
    model_stats = {"count": 2, "total_gb": 1.23, "unused_count": 1}

    embed = build_embed(services, db_stats, model_stats)
    assert "System Health" in embed["title"]
    assert any(f for f in embed["fields"] if f["name"] == "LLM Queue")
    assert any(f for f in embed["fields"] if f["name"] == "Models")
    # Should set Action field because service inactive and failed_24 > 0
    assert any("Action" in f["name"] or "Action" in f["value"] for f in embed["fields"])
