import sys
import types
import os
from pathlib import Path

# Make test environment hermetic by stubbing heavy optional dependencies
sys.modules.setdefault('yfinance', types.ModuleType('yfinance'))

# Ensure pytest-asyncio plugin is available for async tests
pytest_plugins = "pytest_asyncio"

# Provide a fake Google GenAI module for Gemini integration tests when real API is unavailable
if os.getenv("GEMINI_TEST") != "1":
    try:
        # Create namespaced module google.generativeai
        import types as _types

        pkg = _types.ModuleType("google")
        genai = _types.ModuleType("google.generativeai")

        def configure(api_key=None):
            # No-op configuration for tests
            return None

        class GenerativeModel:
            def __init__(self, model_name=None):
                self.model_name = model_name or "fake-model"

            def generate_content(self, prompt):
                class R:
                    text = "Test generated content (fake genai)"

                return R()

        genai.configure = configure
        genai.GenerativeModel = GenerativeModel

        pkg.generativeai = genai
        sys.modules.setdefault("google", pkg)
        sys.modules.setdefault("google.generativeai", genai)
    except Exception:
        pass

# Provide a fallback OllamaProvider for environments without an Ollama server
try:
    import socket

    def _ollama_reachable(host: str) -> bool:
        try:
            hostpart = host.replace("http://", "").replace("https://", "").split(":")[0]
            port = int(host.split(":")[-1]) if ":" in host else 11434
            with socket.create_connection((hostpart, port), timeout=1):
                return True
        except Exception:
            return False

    if not _ollama_reachable(os.getenv("OLLAMA_HOST", "http://localhost:11434")):
        import main as _main

        class FakeOllama:
            def __init__(self, model=None):
                self.name = f"FakeOllama({model})"
                self.is_available = True

            def generate_content(self, prompt: str):
                class R:
                    text = "Fake Ollama generated content"

                return R()

        # Monkeypatch the symbol so tests that import OllamaProvider get this fake
        setattr(_main, "OllamaProvider", FakeOllama)
except Exception:
    pass

# Provide fallback market data to avoid data-dependent skips in TA tests
try:
    import pandas as pd
    from main import QuantEngine

    _orig_fetch = QuantEngine._fetch

    def _fetch_with_fallback(self, ticker, bg=None):
        df = _orig_fetch(self, ticker, bg)
        if df is None:
            # Create deterministic synthetic data for tests
            import numpy as _np
            idx = pd.date_range(end=pd.Timestamp.today(), periods=250, freq="D")
            close = _np.linspace(1800, 1900, 250)
            high = close + 5
            low = close - 5
            df = pd.DataFrame({"Close": close, "High": high, "Low": low}, index=idx)
            # Add a simple SMA and RSI-like columns to satisfy tests
            df["SMA_50"] = df["Close"].rolling(window=50, min_periods=1).mean()
            df["SMA_200"] = df["Close"].rolling(window=200, min_periods=1).mean()
            df["RSI"] = 50 + (df["Close"].pct_change().fillna(0).rolling(window=14).mean() * 100)
            df["ATR"] = (df["High"] - df["Low"]).rolling(window=14, min_periods=1).mean()
            df["ADX_14"] = 25.0
        return df

    QuantEngine._fetch = _fetch_with_fallback
except Exception:
    pass

