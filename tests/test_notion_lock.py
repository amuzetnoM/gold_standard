import builtins
from pathlib import Path
import sys
from pathlib import Path as _P

# Ensure project root is importable
sys.path.insert(0, str(_P(__file__).resolve().parent.parent))

import pytest

from scripts.notion_publisher import NotionPublisher


def test_sync_file_skips_when_lock_unavailable(monkeypatch, tmp_path):
    # Create a dummy markdown file
    md = tmp_path / "test.md"
    md.write_text("---\nstatus: published\n---\n# Test\n\nContent")

    # Monkeypatch NotionPublisher.__init__ to avoid requiring notion-client
    def fake_init(self, *args, **kwargs):
        self.config = type("C", (), {"database_id": "TESTDB"})

    monkeypatch.setattr(NotionPublisher, "__init__", fake_init)

    # Make FileLock.acquire raise to simulate another process holding the lock
    import filelock

    def raise_timeout(self, timeout=None):
        raise Exception("lock busy")

    monkeypatch.setattr(filelock.FileLock, "acquire", raise_timeout)

    pub = NotionPublisher()
    res = pub.sync_file(str(md))
    assert res.get("skipped") is True
    assert res.get("reason") == "publish_in_progress"
