import os
import sys
from pathlib import Path
import pytest

# Skip this mock test by default unless explicitly allowed via env
if os.environ.get("ALLOW_MOCK_OLLAMA", "0") != "1":
    pytest.skip("Mock Ollama tests disabled (set ALLOW_MOCK_OLLAMA=1 to enable)", allow_module_level=True)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.task_executor import TaskExecutor, TaskResult


class MockModel:
    def __init__(self):
        self.name = "Ollama(mock)"

    def generate_content(self, prompt: str):
        class R:
            text = "mock response"
            usage = {"total_tokens": 10, "cost": 0.0}

        return R()


def test_executor_with_mock(tmp_path):
    class Cfg:
        OUTPUT_DIR = str(tmp_path)
        OLLAMA_MODEL = "mock"

    class Action:
        def __init__(self):
            self.action_id = "m1"
            self.title = "Research: Mock"
            self.description = ""
            self.priority = "low"
            self.action_type = "research"
            self.source_context = "test"
            self.source_report = None
            self.status = "pending"

    class Extractor:
        def __init__(self, actions):
            self._actions = actions

        def get_pending_actions(self):
            return list(self._actions)

        def mark_action_complete(self, action_id, result_str):
            pass

        def mark_action_failed(self, action_id, reason):
            pass

    executor = TaskExecutor(Cfg(), __import__("logging").getLogger("test"), model=MockModel(), insights_extractor=Extractor([Action()]))
    results = executor.execute_all_pending()
    assert len(results) == 1
    assert results[0].success
