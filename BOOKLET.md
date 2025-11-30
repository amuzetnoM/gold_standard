# Gold Standard — Technical Booklet & Educational Guide

This booklet is an educational companion to the Gold Standard project and is intended for developers and quants interested in understanding the mathematical foundations, the design choices, and suggested extension points.

Sections:
- Indicator explanations: RSI, ATR, ADX, SMA
- Gold/Silver ratio rationale
- Memory grading logic
- AI prompt design and best practices
- Implementation details & code walk-through
- Testing and validation guidance
- Deployment and operation tips

---

Indicator explanations
----------------------
1) RSI (Relative Strength Index)
   - Definition: RSI = 100 - (100 / (1 + RS)), where RS is the average of gains divided by average of losses over a lookback period (default 14 days).
   - Use: Identify overbought (typically >70) and oversold (typically <30) conditions.

2) ATR (Average True Range)
   - Definition: ATR measures volatility and is typically a smoothed moving average of the True Range (TR), which is the greatest of:
     - current high - current low
     - absolute value of current high - previous close
     - absolute value of current low - previous close
   - Use: Position sizing, stop loss width determination (often multiplied by some factor, e.g., 2x ATR).

3) ADX (Average Directional Index)
   - Definition: The ADX is derived from the DMI (Directional Movement Index) composed of +DI and -DI. ADX measures trend strength without showing direction; values >25 often indicate a strong trend.
   - Use: Distinguish trending markets from ranging markets.

4) SMA (Simple Moving Average)
   - Use: Trend identification and crossovers (SMA 50/200 are common for longer-term regime identification).

Gold/Silver Ratio (GSR)
------------------------
- Definition: gold price / silver price.
- Rationale: As both metals often move together, the relative ratio can indicate relative value opportunities (i.e., Silver cheap relative to Gold). Historically, GSR varying above or below certain thresholds indicates potential rotation benefits.

Memory grading logic
---------------------
- The `Cortex` module stores the last prediction (bias) and price; once a new price is fetched, the system compares the new price to the previously recorded price; if the bias direction was correct, it logs a WIN; otherwise, a LOSS.
- Historical entries are kept bounded to `MAX_HISTORY_ENTRIES` for memory budgeting.

AI prompt design & best practices
---------------------------------
- The `Strategist` builds a strict prompt with:
  - a clear system identity and role
  - performance memory for self-correction
  - an enumerated, structured output format in Markdown so parsing is straightforward
  - numeric thresholds and expectations for indicators
- Practical tips for AI prompts:
  - keep the prompt concise but provide critical values and the required output format
  - prefer to ask for explicit bias statements (BULLISH/BEARISH/NEUTRAL) so parsing is unambiguous
  - consider adding a JSON response format schema to future AI calls to make downstream parsing more robust

Implementation details & code walk-through
-----------------------------------------
- `main.py` houses the entire pipeline for simplicity, but you may split into `cortex.py`, `quant.py`, and `strategist.py` for maintainability.
- Key functions and logic paths are documented with inline comments.

Testing & validation guidance
-----------------------------
- Unit tests should cover:
  - Bias extraction for different AI outputs
  - Memory grading for edge cases (zero previous price, unchanged price, etc.)
  - Data pipeline handling for short/no data (fallback to backup tickers)
  - ADX & ATR fallback computations to ensure their values are sane

CI & deployment
----------------
- CI should run with Python 3.11.
- Include steps for ensuring `pandas_ta` and `numba` are properly installed in CI if you require numeric parity with production.
- Consider containerizing your pipeline into a small Alpine or Debian-based image pinned to Python 3.11 and run a single process scheduling job.

Operational notes
------------------
- Rotate Gemini keys and any secrets used for third-party APIs.
- Disable AI in low-cost or test environments with `--no-ai` for faster runs.

Appendix: Where to start extending
----------------------------------
- Add new assets in the `ASSETS` dictionary in `main.py`.
- Add new signals to `QuantEngine._fetch` and chart to `QuantEngine._chart`.
- Add unit tests for any new signal calculations and backtest your logic with historical candle data before placing any trades.

---

This booklet aims to be a developer-first resource. If you'd like, I can produce a slide deck or an HTML book for human consumption.
