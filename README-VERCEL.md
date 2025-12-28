# Syndicate - Vercel Deployment

## Quick Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FamuzetnoM%2Fsyndicate&env=GEMINI_API_KEY,RUN_INTERVAL_MINUTES&envDescription=API%20keys%20and%20configuration%20for%20Syndicate&envLink=https%3A%2F%2Fgithub.com%2FamuzetnoM%2Fsyndicate%2Fblob%2Fmain%2Fdocs%2FVERCEL_DEPLOYMENT.md)

## Overview

This repository is configured for one-click deployment to Vercel as a fully autonomous AI system that:

- ✅ Runs continuously (24/7 operation)
- ✅ Executes market analysis every 4 hours (configurable)
- ✅ Uses `--wait-forever` flag for complete task execution
- ✅ Provides health check and monitoring endpoints
- ✅ Automatically recovers from errors
- ✅ Supports manual trigger for on-demand analysis

## Prerequisites

Before deploying, you'll need:

1. **Vercel Account** - Sign up at [vercel.com](https://vercel.com) (free tier available)
2. **Gemini API Key** - Get one from [Google AI Studio](https://makersuite.google.com/app/apikey)
3. **Optional**: Notion API credentials for document publishing
4. **Optional**: Discord webhook for notifications

## Environment Variables

### Required

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### Optional

```bash
# Run interval (default: 240 minutes = 4 hours)
RUN_INTERVAL_MINUTES=240

# Notion integration
NOTION_TOKEN=your_notion_token
NOTION_DATABASE_ID=your_database_id

# Discord notifications
DISCORD_BOT_TOKEN=your_bot_token
DISCORD_WEBHOOK_URL=your_webhook_url
DISCORD_OPS_CHANNEL_ID=your_channel_id
```

## Deployment Methods

### Method 1: One-Click Deploy (Easiest)

1. Click the "Deploy with Vercel" button above
2. Sign in to Vercel (or create account)
3. Fork/clone the repository
4. Add environment variables when prompted
5. Click "Deploy"
6. Wait 2-5 minutes for build to complete

### Method 2: Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Clone repository
git clone https://github.com/amuzetnoM/syndicate.git
cd syndicate

# Login to Vercel
vercel login

# Deploy
vercel

# Set environment variables
vercel env add GEMINI_API_KEY
vercel env add RUN_INTERVAL_MINUTES

# Deploy to production
vercel --prod
```

### Method 3: Vercel Dashboard

1. Go to [vercel.com/new](https://vercel.com/new)
2. Import your GitHub repository
3. Configure:
   - Framework Preset: **Other**
   - Build Command: `bash build.sh`
   - Install Command: `pip install -r requirements.txt`
4. Add environment variables
5. Click "Deploy"

## Verifying Deployment

After deployment completes, test your endpoints:

### Health Check

```bash
curl https://your-app.vercel.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-12-28T20:00:00",
  "service": "syndicate",
  "version": "3.7.0",
  "background_worker": "running"
}
```

### Status Check

```bash
curl https://your-app.vercel.app/status
```

Returns detailed system statistics and health information.

### Manual Trigger

```bash
curl -X POST https://your-app.vercel.app/api/trigger
```

Manually triggers an analysis cycle.

## Continuous Operation

### How It Works

1. **Background Worker**: Starts automatically on first HTTP request
2. **Continuous Loop**: Runs analysis cycles at configured intervals
3. **Task Completion**: Uses `--wait-forever` to ensure all tasks complete
4. **Auto-Recovery**: Automatically recovers from errors with retry logic
5. **Stay Alive**: GitHub Actions pings the endpoint every 10 minutes

### Keeping It Running

The repository includes a GitHub Actions workflow (`.github/workflows/keep-alive.yml`) that:
- Pings your health endpoint every 10 minutes
- Keeps the serverless function warm
- Monitors deployment health

**Setup:**

1. Go to your repository on GitHub
2. Navigate to Settings → Secrets → Actions
3. Add a new secret:
   - Name: `VERCEL_DEPLOYMENT_URL`
   - Value: `https://your-app.vercel.app` (your actual Vercel URL)
4. The workflow will run automatically

## Configuration

### Change Run Interval

Update the `RUN_INTERVAL_MINUTES` environment variable in Vercel:

```bash
# Via CLI
vercel env add RUN_INTERVAL_MINUTES
# Enter: 60 (for hourly runs)

# Or in Vercel Dashboard:
# Project Settings → Environment Variables → Edit RUN_INTERVAL_MINUTES
```

Common intervals:
- **15 minutes**: High-frequency monitoring
- **60 minutes**: Hourly analysis
- **240 minutes**: Default (4 hours)
- **720 minutes**: Every 12 hours

### Enable/Disable Features

Features can be toggled via environment variables:

```bash
# Disable Notion publishing
NOTION_PUBLISHING_ENABLED=0

# Disable task execution
TASK_EXECUTION_ENABLED=0

# Disable insights extraction
INSIGHTS_EXTRACTION_ENABLED=0
```

## Monitoring

### Vercel Dashboard

- **Logs**: View real-time logs at `https://vercel.com/<team>/<project>/logs`
- **Analytics**: Monitor function performance
- **Deployments**: View deployment history

### Custom Endpoints

- **Health**: `GET /health` - Quick health status
- **Status**: `GET /status` - Detailed system information
- **Trigger**: `POST /api/trigger` - Manual analysis trigger

### External Monitoring

Consider setting up:

1. **UptimeRobot** or **Pingdom** - Monitor `/health` endpoint
2. **Datadog** or **New Relic** - APM monitoring
3. **Sentry** - Error tracking

## Troubleshooting

### Build Fails

**Issue**: Build fails with "Module not found"

**Solution**:
```bash
# Verify requirements.txt is up to date
pip freeze > requirements.txt

# Test locally
pip install -r requirements.txt
python api/index.py
```

### Background Worker Not Starting

**Issue**: Worker doesn't start after deployment

**Solution**:
1. Check Vercel logs for errors
2. Verify all environment variables are set
3. Ping the health endpoint: `curl https://your-app.vercel.app/health`

### Timeout Errors

**Issue**: Function times out during analysis

**Solution**: This is expected! The background worker continues in the background. Check the status endpoint for progress.

### API Quota Exceeded

**Issue**: Too many Gemini API calls

**Solution**:
1. Increase `RUN_INTERVAL_MINUTES` to reduce frequency
2. Check logs for error loops
3. Consider adding rate limiting

## Local Development

Test the Vercel function locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run local server
python api/index.py

# Test endpoints
curl http://localhost:8080/health
curl http://localhost:8080/status
curl -X POST http://localhost:8080/api/trigger
```

## Advanced Configuration

### Custom Domain

1. Go to Vercel project settings
2. Navigate to "Domains"
3. Add your custom domain
4. Update DNS records as instructed

### Environment-Specific Variables

Set different values for each environment:

- **Production**: Full AI processing, 4-hour intervals
- **Preview**: Shorter intervals for testing
- **Development**: Debug mode, no-AI option

### Cron Jobs (Pro Plan)

For Vercel Pro users, add to `vercel.json`:

```json
{
  "crons": [
    {
      "path": "/api/health",
      "schedule": "*/5 * * * *"
    }
  ]
}
```

## Migration from Docker

If migrating from Docker:

1. Export your data: `docker cp syndicate:/app/data ./backup`
2. Deploy to Vercel (follow steps above)
3. Verify deployment health
4. Consider using external storage (S3, Vercel Blob) for persistence

## Cost Estimate

### Vercel Free Tier

- 100 GB bandwidth/month
- 100 GB-hours compute/month
- Serverless function execution

**Estimated Usage** (with 4-hour intervals):
- Health checks: ~5 MB/day
- Analysis cycles: ~50-100 MB/day
- **Total**: ~3 GB/month ✅ (well within free tier)

### Pro Plan ($20/month)

Benefits for production:
- Longer function timeouts
- More memory (3008 MB)
- Faster cold starts
- Cron jobs support
- Better analytics

## Documentation

- **Full Deployment Guide**: [docs/VERCEL_DEPLOYMENT.md](docs/VERCEL_DEPLOYMENT.md)
- **API Reference**: See `api/index.py` for endpoint documentation
- **Configuration**: See `.env.example` for all environment variables
- **Docker Alternative**: See [docker/README.md](docker/README.md)

## Support

- **Issues**: [GitHub Issues](https://github.com/amuzetnoM/syndicate/issues)
- **Vercel Docs**: [vercel.com/docs](https://vercel.com/docs)
- **Python on Vercel**: [vercel.com/docs/runtimes/python](https://vercel.com/docs/runtimes/python)

## License

MIT License - See [LICENSE](LICENSE) for details.

---

**Ready to deploy?** Click the button at the top to get started! 🚀
