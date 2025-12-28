import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import scripts.cleanup_models as cm


def test_candidates_to_remove():
    models = [
        {"path": "/models/a.gguf", "name": "a", "size_gb": 1},
        {"path": "/models/mini.gguf", "name": "mini", "size_gb": 0.3},
    ]
    res = cm.candidates_to_remove(models, ["mini"])
    assert len(res) == 1
    assert res[0]["name"] == "a"
