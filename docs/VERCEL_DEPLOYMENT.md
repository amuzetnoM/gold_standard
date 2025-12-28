# Vercel Deployment Guide for Syndicate

## Overview

Syndicate is configured for deployment on Vercel as a fully autonomous AI system. The deployment uses Vercel's serverless functions with a background worker that runs continuous analysis cycles.

## Architecture

### How It Works

1. **Serverless Function**: `api/index.py` acts as the entry point for HTTP requests
2. **Background Worker**: Automatically starts on first request and runs continuous analysis
3. **Autonomous Operation**: Uses `--wait-forever` flag to ensure all tasks complete before next cycle
4. **Health Monitoring**: Built-in health check and status endpoints

### Key Features

- ✅ Continuous operation (runs non-stop)
- ✅ Autonomous task completion with `--wait-forever`
- ✅ Health check endpoints for monitoring
- ✅ Manual trigger endpoint for on-demand analysis
- ✅ Automatic error recovery and retry logic
- ✅ Configurable run intervals via environment variables

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Push your code to GitHub
3. **Environment Variables**: Prepare your API keys and configuration

## Required Environment Variables

Configure these in your Vercel project settings:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional - Notion Integration
NOTION_TOKEN=your_notion_token
NOTION_DATABASE_ID=your_notion_database_id

# Optional - Discord Notifications
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_OPS_CHANNEL_ID=your_channel_id
DISCORD_WEBHOOK_URL=your_webhook_url

# Optional - Configuration
RUN_INTERVAL_MINUTES=240          # Default: 240 (4 hours)
PREFER_LOCAL_LLM=0                # Use Gemini by default
LOCAL_LLM_MODEL=                  # Path to local LLM if needed

# Optional - Feature Toggles
LLM_ASYNC_QUEUE=1
OLLAMA_MAX_CONCURRENCY=2
GOLDSTANDARD_LLM_TIMEOUT=240
```

## Deployment Steps

### Option 1: Deploy via Vercel CLI (Recommended)

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy from project root
cd /path/to/syndicate
vercel

# Follow prompts:
# - Link to existing project or create new
# - Set project name (e.g., "syndicate")
# - Set framework preset: "Other"
# - Do not override settings

# Set environment variables
vercel env add GEMINI_API_KEY
vercel env add NOTION_TOKEN
vercel env add RUN_INTERVAL_MINUTES

# Deploy to production
vercel --prod
```

### Option 2: Deploy via Vercel Dashboard

1. **Connect Repository**:
   - Go to [vercel.com/new](https://vercel.com/new)
   - Import your GitHub repository
   - Select the `syndicate` repository

2. **Configure Project**:
   - **Project Name**: `syndicate` (or your preferred name)
   - **Framework Preset**: Other
   - **Root Directory**: `./` (leave as default)
   - **Build Command**: Leave empty (Python runtime handles it)
   - **Output Directory**: Leave empty

3. **Environment Variables**:
   - Click "Environment Variables"
   - Add all required variables from the list above
   - Make sure to add for "Production" environment

4. **Deploy**:
   - Click "Deploy"
   - Wait for build to complete (2-5 minutes)
   - Your app will be live at `https://syndicate-<random>.vercel.app`

## Verification

### 1. Health Check

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
  "background_worker": "running",
  "health": {
    "tasks": {...},
    "documents": {...}
  }
}
```

### 2. Status Check

```bash
curl https://your-app.vercel.app/status
```

This provides detailed system statistics.

### 3. Manual Trigger

```bash
curl -X POST https://your-app.vercel.app/api/trigger
```

This manually triggers an analysis cycle.

## Monitoring

### Vercel Dashboard

1. Go to your project in Vercel dashboard
2. Navigate to "Logs" tab
3. Monitor function invocations and errors
4. Check "Analytics" for performance metrics

### Custom Monitoring Endpoints

- **Health**: `GET /health` or `GET /api/health`
- **Status**: `GET /status` or `GET /api/status`
- **Trigger**: `POST /api/trigger`

### Recommended Monitoring Setup

1. **Uptime Monitoring**:
   - Use services like UptimeRobot or Pingdom
   - Configure to check `/health` endpoint every 5 minutes
   - Set up alerts for downtime

2. **Log Monitoring**:
   - Check Vercel logs regularly
   - Look for error patterns
   - Monitor API quota usage

## Continuous Operation

### How Continuous Operation Works

The system uses a background worker thread that:

1. **Starts automatically** on first HTTP request
2. **Runs in continuous loop** with configurable intervals
3. **Executes analysis cycles** with full AI processing
4. **Uses `--wait-forever` flag** to ensure all tasks complete
5. **Recovers automatically** from errors with exponential backoff

### Keeping the Function Alive

Vercel serverless functions have execution time limits. To ensure continuous operation:

1. **External Pinger**: Set up a cron job or monitoring service to ping the health endpoint every 5-10 minutes:

```bash
# Using cron (on your local machine or server)
*/5 * * * * curl -s https://your-app.vercel.app/health > /dev/null
```

2. **Vercel Cron Jobs** (Recommended for Pro plan):

Create `vercel.json` with cron configuration:

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

3. **GitHub Actions** (Free alternative):

Create `.github/workflows/keep-alive.yml`:

```yaml
name: Keep Alive
on:
  schedule:
    - cron: '*/10 * * * *'  # Every 10 minutes
jobs:
  ping:
    runs-on: ubuntu-latest
    steps:
      - name: Ping health endpoint
        run: |
          curl -s https://your-app.vercel.app/health
          curl -s https://your-app.vercel.app/status
```

## Configuration

### Run Interval

Control how often analysis cycles run:

```bash
# In Vercel environment variables
RUN_INTERVAL_MINUTES=240  # Default: 4 hours

# For more frequent analysis (e.g., hourly)
RUN_INTERVAL_MINUTES=60

# For high-frequency (every 15 minutes)
RUN_INTERVAL_MINUTES=15
```

### Memory and Timeout

The `vercel.json` configuration sets:
- **Memory**: 3008 MB (maximum for Pro plan)
- **Timeout**: 300 seconds (5 minutes)

For longer analysis cycles, the background worker continues in the background.

## Troubleshooting

### Common Issues

#### 1. "Module not found" errors

**Problem**: Missing dependencies in Vercel build.

**Solution**: Ensure `requirements.txt` is in root directory and contains all dependencies.

```bash
# Verify locally
pip install -r requirements.txt
python api/index.py
```

#### 2. "Background worker not starting"

**Problem**: Worker thread fails to initialize.

**Solution**: Check Vercel logs for import errors. Ensure all environment variables are set.

#### 3. "Timeout errors"

**Problem**: Analysis takes longer than function timeout.

**Solution**: This is expected. The background worker continues in the background. Check status endpoint for progress.

#### 4. "API quota exceeded"

**Problem**: Too many Gemini API calls.

**Solution**: Increase `RUN_INTERVAL_MINUTES` or check for error loops in logs.

### Debugging

1. **Check Vercel Logs**:
```bash
vercel logs your-deployment-url
```

2. **Test Locally**:
```bash
# Install dependencies
pip install -r requirements.txt

# Run test server
python api/index.py

# Test endpoints
curl http://localhost:8080/health
curl http://localhost:8080/status
```

3. **Verify Environment Variables**:
```bash
vercel env ls
```

## Performance Optimization

### 1. Reduce Cold Starts

- Keep function warm with regular health checks
- Use Vercel Pro for faster cold starts
- Minimize import statements in `api/index.py`

### 2. Optimize Analysis Interval

- Balance between real-time updates and API costs
- Recommended: 4 hours (240 minutes) for production
- Use shorter intervals (15-60 minutes) for testing

### 3. Database Optimization

- SQLite database is stored in `/tmp` on Vercel
- Consider using external database (PostgreSQL, MongoDB) for persistent storage
- Implement caching for frequently accessed data

## Advanced Configuration

### Custom Domain

1. Go to Vercel project settings
2. Navigate to "Domains"
3. Add your custom domain
4. Update DNS records as instructed

### Multiple Environments

Deploy to different environments:

```bash
# Development
vercel --target development

# Preview (for pull requests)
vercel --target preview

# Production
vercel --target production
```

### Environment-specific Variables

Set different values for each environment in Vercel dashboard:
- Production: Full AI processing
- Preview: Shorter intervals for testing
- Development: No-AI mode for debugging

## Migration from Docker

If migrating from Docker deployment:

1. **Export Data**: Backup your SQLite database and output files
2. **Deploy to Vercel**: Follow deployment steps above
3. **Verify**: Check health and status endpoints
4. **Migrate Data**: Upload backup data to Vercel (or external storage)
5. **Update DNS**: Point your domain to Vercel deployment

## Support and Resources

- **Vercel Documentation**: https://vercel.com/docs
- **Python on Vercel**: https://vercel.com/docs/runtimes#official-runtimes/python
- **Syndicate GitHub**: https://github.com/amuzetnoM/syndicate
- **Issues**: Report issues on GitHub Issues page

## Security Best Practices

1. **Environment Variables**: Never commit API keys to repository
2. **HTTPS Only**: Vercel provides automatic HTTPS
3. **Rate Limiting**: Monitor API usage to prevent abuse
4. **Access Control**: Consider adding authentication for trigger endpoint
5. **Regular Updates**: Keep dependencies updated for security patches

## Cost Considerations

### Vercel Free Tier

- 100 GB bandwidth per month
- 100 GB-hours function execution per month
- Serverless function execution

**Estimated Usage**:
- Health checks: ~5 MB/day
- Analysis cycles: ~50-100 MB/day
- **Total**: ~3 GB/month (well within free tier)

### Pro Plan Benefits

- Faster cold starts
- Longer function timeout (15 minutes vs 10 seconds)
- More memory (3008 MB vs 1024 MB)
- Cron jobs support
- Better analytics

**Recommended for production use.**

## Next Steps

After successful deployment:

1. ✅ Set up uptime monitoring
2. ✅ Configure custom domain (optional)
3. ✅ Enable Notion integration
4. ✅ Set up Discord notifications
5. ✅ Monitor logs for first 24 hours
6. ✅ Optimize run interval based on usage
7. ✅ Set up automated backups

---

**Questions?** Open an issue on GitHub or check the Vercel documentation.
