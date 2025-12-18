"""
Provider-specific adapters to extract usage metrics (tokens, costs) from LLM responses.
These are best-effort parsers for Gemini and Ollama response shapes.
"""
from typing import Any, Tuple


def parse_gemini_usage(resp: Any) -> Tuple[int, float]:
    """Parse Gemini (google.generativeai) response for tokens and cost.
    Returns (tokens_used, cost_usd). Best-effort; returns (0, 0.0) on unknown shapes.
    """
    tokens = 0
    cost = 0.0
    try:
        # genai may include .metadata or .candidates[*].metadata or .usage
        if hasattr(resp, "metadata") and isinstance(resp.metadata, dict):
            meta = resp.metadata
            tokens = int(meta.get("tokens", meta.get("tokenCount", 0)) or 0)
            cost = float(meta.get("cost", 0.0) or 0.0)
        elif hasattr(resp, "candidates"):
            # Candidates may be list-like
            cans = getattr(resp, "candidates")
            if isinstance(cans, (list, tuple)) and len(cans) > 0:
                c0 = cans[0]
                if hasattr(c0, "metadata") and isinstance(c0.metadata, dict):
                    tokens = int(c0.metadata.get("tokens", 0) or 0)
                    cost = float(c0.metadata.get("cost", 0.0) or 0.0)
        elif isinstance(resp, dict):
            meta = resp.get("metadata") or resp.get("usage") or {}
            if isinstance(meta, dict):
                tokens = int(meta.get("total_tokens", meta.get("tokens", 0)) or 0)
                cost = float(meta.get("cost", 0.0) or 0.0)
    except Exception:
        pass
    return tokens, cost


def parse_ollama_usage(resp: Any) -> Tuple[int, float]:
    """Parse Ollama response shape for usage. Ollama returns JSON and may include 'usage' or 'token_usage'.
    Returns (tokens_used, cost_usd).
    """
    tokens = 0
    cost = 0.0
    try:
        if isinstance(resp, dict):
            usage = resp.get("usage") or resp.get("token_usage") or {}
            if isinstance(usage, dict):
                tokens = int(usage.get("total_tokens", usage.get("tokens", 0)) or 0)
                cost = float(usage.get("cost", 0.0) or 0.0)
        # Ollama python wrappers might attach attributes
        if hasattr(resp, "usage"):
            usage = getattr(resp, "usage")
            if isinstance(usage, dict):
                tokens = int(usage.get("total_tokens", usage.get("tokens", 0)) or 0)
                cost = float(usage.get("cost", 0.0) or 0.0)
    except Exception:
        pass
    return tokens, cost


def parse_generic_usage(resp: Any) -> Tuple[int, float]:
    """Fallback generic parser that inspects common keys.
    """
    tokens = 0
    cost = 0.0
    try:
        if isinstance(resp, dict):
            meta = resp.get("usage") or resp.get("metadata") or {}
            if isinstance(meta, dict):
                tokens = int(meta.get("total_tokens", meta.get("tokens", 0)) or 0)
                cost = float(meta.get("cost", 0.0) or 0.0)
        if hasattr(resp, "usage") and isinstance(getattr(resp, "usage"), dict):
            usage = getattr(resp, "usage")
            tokens = int(usage.get("total_tokens", usage.get("tokens", 0)) or 0)
    except Exception:
        pass
    return tokens, cost
