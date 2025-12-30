# Syndicate Operations — The Intelligence Pipeline

This document details the **functional workflow** of the Syndicate system — how raw market data is transformed into actionable intelligence and distributed.

---

## 1. The Core Loop (Daemon)

The standard operation is a continuous **Event Loop** managed by `run.py --daemon`.

### Phase 1: Data Ingestion
*   **Trigger**: Daily Schedule (market open/close) or continuous polling.
*   **Sources**:
    *   `yfinance`: OHLCV data for crypto/stocks.
    *   `newsapi`: Global macro news headers.
    *   `economic_calendar`: Upcoming high-impact events.
*   **Storage**: Raw data is structured and stored in `data/syndicate.db` (SQLite).

### Phase 2: Quantitative Analysis (`QuantEngine`)
Before any AI touches the data, hard quantitative rules are applied:
*   **Trend Analysis**: Moving Averages (SMA/EMA), RSI, MACD.
*   **Level Detection**: Support/Resistance zones based on volume profiles.
*   **Signal Generation**: Probabilistic scoring (0-100) for "Long" vs "Short" bias.

### Phase 3: Cognitive Synthesis (`Strategist`)
This is where the "Agent" comes in. The quantitative data is wrapped into a prompt context but **not processed synchronously**.
1.  **Task Creation**: The Daemon constructs a prompt (JSON) containing the Quant data + News.
2.  **Queue Injection**: This task is inserted into the `llm_tasks` table with `status='pending'`.
3.  **Decoupling**: The Daemon moves on immediately. It does *not* wait for the LLM.

---

## 2. The Compute Layer (LLM Worker)

The heavy lifting is done by the **LLM Worker** (`scripts/llm_worker.py`), running in parallel.

### Execution Flow
1.  **Poll**: Checks `llm_tasks` queue for `pending` items.
2.  **Context Loading**: Loads the local LLM (Phi-3) or connects to Gemini (Fallback).
3.  **Generation**:
    *   Processes the prompt.
    *   Enforces "Persona" (Syndicate tone, no fluff).
    *   Extracts structured JSON or Markdown output.
4.  **Completion**: Updates the DB record with `response` and sets `status='completed'`.

---

## 3. Publication & Distribution

Once a task is `completed`, the Daemon (or a separate publisher thread) picks it up.

### Channel Routing
Intelligence is routed based on type (defined in `self_guide.py`):
*   **Digests** -> `#daily-digests` (High-level summary).
*   **Premarket** -> `#premarket-plans` (Actionable levels).
*   **Journals** -> `#trading-journal` (Execution review).
*   **Alerts** -> `#alerts` (Real-time crosses).

### External Sync (Notion)
*   All reports are converted to Notion Blocks.
*   Pushed to the configured `NOTION_DATABASE_ID`.
*   Provides a persistent, searchable archive of all intelligence.

---

## 4. Manual Override Commands

Operators can inject tasks into this pipeline manually via Discord (`#syndicate-intel`):

| Command | Action | Flow |
| :--- | :--- | :--- |
| `/intel [query]` | ad-hoc analysis | User -> Bot -> **Queue** -> Worker -> Bot -> User |
| `!force_publish` | manual sync | Bot -> Daemon -> Notion API |
| `!health` | status check | Bot -> Sentinel -> Discord |
