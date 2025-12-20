from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from db_manager import DatabaseManager


def test_subscriptions_crud(tmp_path: Path):
    db_path = tmp_path / "sub.db"
    db = DatabaseManager(db_path)
    sid = db.add_subscription("12345", "sanitizer")
    assert isinstance(sid, int) and sid > 0
    topics = db.get_user_subscriptions("12345")
    assert "sanitizer" in topics
    ok = db.remove_subscription("12345", "sanitizer")
    assert ok
    topics2 = db.get_user_subscriptions("12345")
    assert "sanitizer" not in topics2
