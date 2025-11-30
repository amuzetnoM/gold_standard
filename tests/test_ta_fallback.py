import sys
from pathlib import Path
import pytest
import types

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))

from main import Config, setup_logging
from main import ta as orig_ta
from main import QuantEngine


def test_fetch_with_broken_ta(monkeypatch):
    cfg = Config()
    logger = setup_logging(cfg)
    q = QuantEngine(cfg, logger)

    # Ensure a baseline fetch works
    df = q._fetch('GC=F', 'GLD')
    if df is None:
        pytest.skip("No data available for GC/GLD in test environment")

    # Replace ta with a broken implementation to force fallback
    class BrokenTA:
        def rsi(self, *a, **k):
            raise RuntimeError("rsi crash")
        def sma(self, *a, **k):
            raise RuntimeError("sma crash")
        def atr(self, *a, **k):
            raise RuntimeError("atr crash")
        def adx(self, *a, **k):
            raise RuntimeError("adx crash")

    monkeypatch.setattr('main.ta', BrokenTA())
    try:
        df2 = q._fetch('GC=F', 'GLD')
        assert df2 is not None
        assert 'Close' in df2.columns
    finally:
        # restore
        monkeypatch.setattr('main.ta', orig_ta)
