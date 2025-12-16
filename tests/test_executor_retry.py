import logging
import os
import sys
from pathlib import Path

# Ensure project root is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.task_executor import TaskExecutor, TaskResult


class MockAction:
    def __init__(self, aid: str):
        self.action_id = aid
        self.title = "Test Action"


def test_execute_with_unlimited_retries(monkeypatch):
    logger = logging.getLogger("test")
    executor = TaskExecutor(config=None, logger=logger)

    # Avoid sleeping during tests
    monkeypatch.setattr(executor, "_wait_for_quota", lambda r: 0)

    attempts = {"count": 0}

    def handler(action):
        attempts["count"] += 1
        if attempts["count"] < 4:
            return TaskResult(action_id=action.action_id, success=False, result_data=None, execution_time_ms=0, error_message="Quota exceeded")
        return TaskResult(action_id=action.action_id, success=True, result_data={"ok": True}, execution_time_ms=10)

    # Force unlimited retries for test
    monkeypatch.setattr("scripts.task_executor.MAX_RETRIES", -1)

    res = executor._execute_with_retry(MockAction("A-1"), handler)
    assert res.success
    assert attempts["count"] == 4
