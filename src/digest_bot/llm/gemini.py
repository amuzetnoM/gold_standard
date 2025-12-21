#!/usr/bin/env python3
"""Gemini LLM provider with simple rate-limiting.

This provider tries to use the `google.generativeai` (or compat shim)
GenerativeModel API when available. It enforces a minimum interval
between requests (rate_limit_sec) to avoid hitting API quotas.
"""

import logging
import os
import threading
import time
from typing import Optional

from .base import GenerationConfig, InferenceError, LLMProvider, LLMResponse, ProviderError

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """Provider for Google Gemini with a blocking rate-limit throttler."""

    name = "gemini"

    def __init__(self, model: str = "models/gemini-pro-latest", rate_limit_sec: float = 60.0, timeout: float = 20.0):
        super().__init__()
        self._model_name = model
        self.rate_limit = float(rate_limit_sec)
        self.timeout = float(timeout)
        self._last_call = 0.0
        self._lock = threading.Lock()
        self._client = None

    def load(self) -> None:
        """Attempt to import/configure Gemini client. Does not make a network call here."""
        if self._loaded:
            return

        try:
            import google.generativeai as genai  # type: ignore

            # Configure API key if present
            api_key = os.getenv("GEMINI_API_KEY")
            try:
                if api_key:
                    genai.configure(api_key=api_key)
            except Exception:
                # non-fatal - rely on environment or service account
                logger.debug("gemini: configure() raised, continuing")

            self._client = genai
            self._loaded = True
            logger.info(f"Gemini provider initialized (model={self._model_name})")
        except Exception as e:
            raise ProviderError(
                "Gemini provider not available: install/configure google.generativeai or compat shim",
                provider=self.name,
                retryable=False,
            ) from e

    def unload(self) -> None:
        self._client = None
        self._loaded = False

    def health_check(self) -> bool:
        if not self._client:
            return False
        # Quick cheap check: ensure API key present OR SDK reachable
        try:
            return bool(os.getenv("GEMINI_API_KEY") or hasattr(self._client, "GenerativeModel"))
        except Exception:
            return False

    def _enforce_rate_limit(self) -> None:
        """Block until rate-limit window has passed (simple global throttle)."""
        with self._lock:
            now = time.time()
            elapsed = now - self._last_call
            wait = self.rate_limit - elapsed
            if wait > 0:
                logger.info(f"Gemini rate-limited: sleeping {wait:.1f}s to respect {self.rate_limit}s interval")
                time.sleep(wait)
            # update last_call timestamp to now (we'll call shortly)
            self._last_call = time.time()

    def generate(self, prompt: str, config: Optional[GenerationConfig] = None) -> LLMResponse:
        if not self._loaded:
            self.load()

        if self._client is None:
            raise ProviderError("Gemini client not initialized", provider=self.name, retryable=True)

        # Enforce rate limiting before making call
        self._enforce_rate_limit()

        try:
            start = time.time()

            # Try the modern GenerativeModel interface, falling back when necessary
            if hasattr(self._client, "GenerativeModel"):
                model = self._client.GenerativeModel(self._model_name)
                # Many compat shims expose `generate`/`generate_content` or return rich objects
                try:
                    resp = model.generate_content(prompt)
                except Exception:
                    # Some versions use `generate` with text output
                    resp = model.generate(prompt=prompt)

                # Try a few ways to get text out
                text = ""
                try:
                    if hasattr(resp, "content"):
                        text = resp.content
                    elif isinstance(resp, dict):
                        # genai may return structured dicts
                        if "candidates" in resp:
                            text = resp.get("candidates", [{}])[0].get("content", "")
                        else:
                            # Try common fields
                            text = resp.get("content", "") or resp.get("output", "") or ""
                    else:
                        text = str(resp)
                except Exception:
                    text = str(resp)

            else:
                raise ProviderError("Gemini client API not compatible", provider=self.name, retryable=False)

            elapsed = time.time() - start

            return LLMResponse(
                text=text.strip(),
                tokens_used=0,
                generation_time=elapsed,
                model=self._model_name,
                provider=self.name,
                finish_reason="stop",
                raw_response={"note": "raw object may be SDK-specific"},
            )

        except Exception as e:
            # If it's a timeout or connectivity issue, surface as retryable inference error
            msg = str(e)
            if "timeout" in msg.lower():
                raise InferenceError(f"Gemini request timed out: {e}", provider=self.name, retryable=True)
            raise InferenceError(f"Gemini generation failed: {e}", provider=self.name, retryable=True)
