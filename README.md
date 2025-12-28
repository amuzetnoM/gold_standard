# Syndicate - Autonomous Precious Metals Intelligence System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/AI-Gemini-orange.svg" alt="AI Powered">
  <img src="https://img.shields.io/badge/Status-Production-green.svg" alt="Status">
  <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License">
</p>

## Overview

Syndicate is a fully autonomous AI-powered system for precious metals market analysis. It continuously monitors markets, generates insights, executes research tasks, and publishes reports — all without human intervention.

### Key Features

- 🤖 **Fully Autonomous**: Runs 24/7 with zero manual intervention
- 🧠 **AI-Powered Analysis**: Uses Google Gemini for sophisticated market analysis
- 📊 **Comprehensive Reporting**: Daily journals, weekly rundowns, monthly/yearly reports
- 🎯 **Task Execution**: Automatically identifies and completes research tasks
- 📝 **Notion Integration**: Auto-publishes reports with smart scheduling
- 🔄 **Continuous Operation**: Background worker ensures non-stop execution
- ⚡ **Multiple Deployment Options**: Docker, Vercel, or direct Python

## Quick Start

### Deploy to Vercel (Recommended)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FamuzetnoM%2Fsyndicate)

**One-click deployment with:**
- Automatic continuous operation
- Built-in health monitoring
- Serverless architecture
- Free tier available

👉 **[Full Vercel Deployment Guide](README-VERCEL.md)**

### Docker Deployment

```bash
# Quick start with Docker Compose
docker compose up -d

# With monitoring stack
docker compose --profile monitoring up -d
```

👉 **[Docker Deployment Guide](docker/README.md)**

### Local Installation

```bash
# Clone repository
git clone https://github.com/amuzetnoM/syndicate.git
cd syndicate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run autonomous mode
python run.py
```

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Syndicate                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Quant       │  │  AI          │  │  Task        │    │
│  │  Engine      │→│  Strategist  │→│  Executor    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│         ↓                  ↓                  ↓            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Market      │  │  Reports &   │  │  Notion      │    │
│  │  Data        │  │  Insights    │  │  Publisher   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### How It Works

1. **Data Collection**: Fetches market data from Yahoo Finance
2. **Technical Analysis**: Calculates indicators (RSI, ADX, ATR, SMAs)
3. **AI Analysis**: Gemini generates sophisticated market insights
4. **Task Generation**: Identifies research needs and creates tasks
5. **Task Execution**: Autonomous system completes research tasks
6. **Report Publishing**: Auto-publishes to Notion with smart scheduling
7. **Continuous Loop**: Repeats every 4 hours (configurable)

## Configuration

### Required Environment Variables

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here
```

### Optional Environment Variables

```bash
# Run Interval (default: 240 minutes = 4 hours)
RUN_INTERVAL_MINUTES=240

# Notion Integration
NOTION_TOKEN=your_notion_token
NOTION_DATABASE_ID=your_database_id

# Discord Notifications
DISCORD_WEBHOOK_URL=your_webhook_url
DISCORD_OPS_CHANNEL_ID=your_channel_id

# Feature Toggles
INSIGHTS_EXTRACTION_ENABLED=1
TASK_EXECUTION_ENABLED=1
NOTION_PUBLISHING_ENABLED=1

# Local LLM (Optional - for offline operation)
PREFER_LOCAL_LLM=0
LOCAL_LLM_MODEL=/path/to/model.gguf
LOCAL_LLM_GPU_LAYERS=-1
```

See [`.env.template`](.env.template) for complete configuration options.

## Usage

### Command Line Interface

```bash
# Autonomous daemon mode (default)
python run.py

# Single run and exit
python run.py --once

# Single run with wait-forever (ensures all tasks complete)
python run.py --once --wait-forever

# Interactive mode
python run.py --interactive

# No-AI mode (for testing)
python run.py --no-ai

# Custom interval (in minutes)
python run.py --interval-min 60

# Show current status
python run.py --status
```

### Programmatic Usage

```python
from main import Config, setup_logging, create_llm_provider, execute
import run

# Set up
config = Config()
logger = setup_logging(config)
model = create_llm_provider(config, logger)

# Run analysis
success = execute(config, logger, model=model)

# Run post-analysis tasks with wait-forever
if success:
    run._run_post_analysis_tasks(
        force_inline=True,
        wait_forever=True
    )
```

## Features

### Report Types

- **Daily Journals**: Comprehensive market analysis with bias and trade ideas
- **Pre-Market Plans**: Morning trading blueprints with key levels
- **Weekly Rundowns**: Week-over-week trend analysis
- **Monthly Reports**: Deep-dive monthly performance reviews
- **Yearly Reports**: Annual strategy and performance summaries

### Task Execution

The system autonomously:
- Identifies research needs from reports
- Creates and prioritizes tasks
- Executes research (data analysis, monitoring, calculations)
- Publishes results to Notion
- Tracks completion and success metrics

### Monitoring

Built-in endpoints for health monitoring:

```bash
# Health check
curl http://localhost:8080/health

# Detailed status
curl http://localhost:8080/status

# Manual trigger
curl -X POST http://localhost:8080/api/trigger
```

## Deployment Options

### 1. Vercel (Serverless) - ⭐ Recommended for Production

**Best for**: Autonomous 24/7 operation with zero maintenance

✅ **Features:**
- One-click deployment with GitHub integration
- Continuous operation with `--wait-forever` support
- Automatic error recovery and retry logic
- Built-in health check and monitoring endpoints
- Free tier available (3GB/month bandwidth)
- Serverless architecture scales automatically

🚀 **Deploy Now:**

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FamuzetnoM%2Fsyndicate)

**Quick Start:**
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd syndicate
vercel

# Add environment variables
vercel env add GEMINI_API_KEY
vercel env add RUN_INTERVAL_MINUTES

# Deploy to production
vercel --prod
```

**Endpoints:**
- Health: `https://your-app.vercel.app/health`
- Status: `https://your-app.vercel.app/status`
- Manual Trigger: `POST https://your-app.vercel.app/api/trigger`

**📖 [Complete Vercel Deployment Guide →](README-VERCEL.md)**

**📄 [Detailed Documentation →](docs/VERCEL_DEPLOYMENT.md)**

### 2. Docker (Containerized)

**Best for**: Self-hosted deployments, full control

- Complete monitoring stack
- Prometheus + Grafana
- PostgreSQL option
- Easy updates

**[Docker Deployment Guide →](docker/README.md)**

### 3. Local/VM (Direct)

**Best for**: Development, testing, custom setups

```bash
python run.py
```

**[Local Setup Guide →](docs/README.md)**

## Documentation

- **[Vercel Deployment](README-VERCEL.md)** - Serverless deployment guide
- **[Docker Deployment](docker/README.md)** - Container deployment guide
- **[Full Documentation](docs/README.md)** - Complete technical documentation
- **[API Reference](docs/VERCEL_DEPLOYMENT.md#monitoring)** - HTTP endpoints
- **[Configuration](docs/VERCEL_DEPLOYMENT.md#configuration)** - All settings

## Development

### Project Structure

```
syndicate/
├── api/               # Vercel serverless functions
├── src/               # Source packages
│   ├── gost/         # Core library
│   ├── digest_bot/   # Discord bot
│   └── social/       # Social media automation
├── scripts/          # Utility scripts
├── docker/           # Docker configurations
├── docs/             # Documentation
├── main.py           # Main analysis engine
├── run.py            # CLI interface
└── db_manager.py     # Database management
```

### Running Tests

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# With coverage
pytest --cov=. --cov-report=html
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## Monitoring & Observability

### Prometheus Metrics

- Task execution rates
- Analysis cycle duration
- API quota usage
- Error rates
- System health

### Grafana Dashboards

- Real-time system overview
- Task execution analytics
- Resource utilization
- Alert history

### Logging

- Structured JSON logs
- Rotating file handler
- Console output with colors
- Error tracking

## Performance

### Benchmarks

- **Analysis Cycle**: ~2-5 minutes
- **Task Execution**: ~30s-2m per task
- **Report Generation**: ~10-30 seconds
- **Memory Usage**: ~200-500 MB
- **API Calls**: ~5-10 per cycle

### Scaling

- **Free Tier**: ~100 cycles/month
- **Pro Tier**: Unlimited cycles
- **Self-hosted**: Limited only by resources

## Troubleshooting

### Common Issues

**"Module not found" errors**
```bash
pip install -r requirements.txt
```

**"API quota exceeded"**
- Increase `RUN_INTERVAL_MINUTES`
- Check for error loops in logs

**"Database locked"**
- Only one instance should run at a time
- Check for orphaned processes

**Background worker not starting**
- Check environment variables
- Verify API keys are set
- Review Vercel/Docker logs

See **[Troubleshooting Guide](docs/VERCEL_DEPLOYMENT.md#troubleshooting)** for more solutions.

## Support

- **Issues**: [GitHub Issues](https://github.com/amuzetnoM/syndicate/issues)
- **Discussions**: [GitHub Discussions](https://github.com/amuzetnoM/syndicate/discussions)
- **Documentation**: [docs/](docs/)

## License

MIT License - See [LICENSE](LICENSE) for details.

## Acknowledgments

- **AI**: Google Gemini for market analysis
- **Data**: Yahoo Finance for market data
- **Integration**: Notion for report publishing
- **Monitoring**: Prometheus + Grafana

---

**Ready to deploy?**

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FamuzetnoM%2Fsyndicate)

Or check out the **[Vercel Deployment Guide](README-VERCEL.md)** for step-by-step instructions.
