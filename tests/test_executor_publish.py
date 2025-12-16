import logging
from pathlib import Path

import pytest

from scripts.task_executor import TaskExecutor


class MockConfig:
    OUTPUT_DIR = str(Path(__file__).resolve().parent / "tmp_output")


def test_executor_does_not_force_publish(monkeypatch, tmp_path):
    logger = logging.getLogger("test")
    cfg = MockConfig()
    # Ensure output dir exists
    out = Path(cfg.OUTPUT_DIR)
    out.mkdir(parents=True, exist_ok=True)

    executor = TaskExecutor(cfg, logger)

    called = {}

    class MockPublisher:
        def sync_file(self, filepath, doc_type=None, tags=None, force=False):
            called['force'] = force
            return {"skipped": True}

    # Patch internal _get_notion_publisher to return our mock
    monkeypatch.setattr(executor, "_get_notion_publisher", lambda: MockPublisher())

    # Call _publish_to_notion and assert sync_file was called without forcing
    result = executor._publish_to_notion("/nonexistent/path.md", doc_type="research")
    assert called.get('force') is False
    assert result is False or isinstance(result, bool)
