# GOLD STANDARD v3.1.0

**Release Date:** December 3, 2025  
**First Public Release**

---

## Overview

Gold Standard is a comprehensive precious metals intelligence system that combines real-time market data, AI-powered analysis, and automated report generation. This release marks the first public availability of the platform.

---

## What's Included

### 🤖 AI-Powered Analysis
- **Gemini 2.0 Flash Integration** — Natural language market analysis with Google's latest AI model
- **Multi-Asset Coverage** — Gold, Silver, DXY, VIX, 10Y Treasury, S&P 500
- **Technical Indicators** — RSI, ADX, ATR, SMA (50/200) with pandas_ta

### 📊 Report Generation
- **Daily Journals** — Comprehensive market summaries with bias detection
- **Pre-Market Plans** — Morning briefings with key levels and catalysts
- **Horizon Analysis** — 3-month and 1-year outlook reports
- **Catalyst Tracking** — Event-driven market movers
- **Institutional Matrix** — Fund flows and positioning analysis
- **Economic Calendar** — Scheduled events and impact analysis

### 📈 Automated Charts
- Candlestick charts with SMA overlays
- Auto-generated and organized by date
- PNG export for reports and sharing

### 🧠 Cortex Memory System
- Prediction tracking with performance grading
- Historical accuracy metrics
- Win/loss streak maintenance

### 🔄 Autonomous Operation
- **Daemon Mode** — Continuous analysis at configurable intervals
- **Task Execution** — Priority-based action queue (research, monitoring, alerts)
- **Insights Engine** — Entity and action extraction from reports
- **File Organization** — Auto-categorization and archiving

### 🖥️ Modern GUI
- Dual-pane architecture with charts grid and AI workspace
- Real-time status indicators
- Task queue visualization
- Premium dark theme with gold accents

### 📤 Notion Integration (New in v3.1)
- Automatic publishing to Notion database
- Full markdown conversion (tables, code, callouts)
- Frontmatter metadata for categorization

---

## Quick Start

```bash
# Clone
git clone https://github.com/amuzetnoM/gold_standard.git
cd gold_standard

# Setup (Windows)
.\scripts\setup.ps1

# Setup (Unix)
./scripts/setup.sh

# Configure
cp .env.template .env
# Add your GEMINI_API_KEY (required)
# Add NOTION_API_KEY and NOTION_DATABASE_ID (optional)

# Run
python run.py --full
```

---

## System Requirements

- **Python** 3.10 – 3.13
- **OS** Windows, macOS, Linux
- **API Keys** Google Gemini (required), Notion (optional)

---

## Documentation

- [README](../README.md) — Project overview and setup
- [Architecture](ARCHITECTURE.md) — System design and modules
- [Guide](GUIDE.md) — Detailed usage instructions
- [Changelog](CHANGELOG.md) — Version history

---

## License

MIT License — See [LICENSE](../LICENSE) for details.

---

## Links

- **Repository:** [github.com/amuzetnoM/gold_standard](https://github.com/amuzetnoM/gold_standard)
- **Documentation:** [docs/index.html](index.html)
- **Notion Workspace:** [Open in Notion](https://false-pillow-a63.notion.site/2be743b492d58026b633cd407535658a)

---

*Built for traders, analysts, and anyone seeking clarity in precious metals markets.*
