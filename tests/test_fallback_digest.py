from src.digest_bot.writer import DigestWriter
from src.digest_bot.summarizer import DigestResult
from src.digest_bot.daily_report import build_report
from db_manager import DatabaseManager


def test_fallback_digest_write(tmp_path):
    db = DatabaseManager()
    msg = build_report(db, hours=24)
    assert msg and len(msg) > 50

    writer = DigestWriter()
    res = writer.write(DigestResult(content=msg, success=True, metadata={"fallback": True}), target_date=None)
    assert res.success
    assert res.path.exists()
