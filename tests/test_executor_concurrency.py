import threading
import time
import sys
import os

# Ensure project root is on sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.task_executor import TaskExecutor, TaskResult
from scripts.insights_engine import InsightsExtractor, ActionInsight
from main import Config
import logging


def test_parallel_execution_smoke(tmp_path):
    config = Config()
    logger = logging.getLogger("test")
    logger.setLevel(logging.DEBUG)

    # Create a fake TaskExecutor with a dummy handler
    te = TaskExecutor(config, logger, None, InsightsExtractor(config, logger))

    # Register a dummy handler that sleeps
    def sleeper(action):
        time.sleep(0.1)
        return TaskResult(action_id=action.action_id, success=True, result_data={"ok": True}, execution_time_ms=100)

    te.handlers["dummy"] = sleeper

    # Create several pending actions
    actions = []
    for i in range(8):
        ai = ActionInsight(
            action_id=f"T-{i}",
            action_type="dummy",
            title=f"Dummy {i}",
            description="",
            priority="low",
        )
        te.insights_extractor.action_queue.append(ai)
        actions.append(ai)

    results = te.execute_all_pending()
    assert all(r.success for r in results)


def test_insights_threadsafe_id_generation():
    config = Config()
    logger = logging.getLogger("test")
    extractor = InsightsExtractor(config, logger)

    ids = set()

    def gen_ids(n):
        for _ in range(n):
            ids.add(extractor._generate_action_id())

    threads = [threading.Thread(target=gen_ids, args=(50,)) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(ids) == 200
