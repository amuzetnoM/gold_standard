# Vercel Deployment Checklist

Use this checklist to ensure your Syndicate application is ready for Vercel deployment.

## Pre-Deployment Checklist

### ✅ Configuration Files
- [ ] `vercel.json` exists and is valid
- [ ] `api/index.py` exists (serverless entry point)
- [ ] `package.json` exists
- [ ] `.vercelignore` exists
- [ ] `.gitignore` updated with Vercel entries

### ✅ Dependencies
- [ ] `requirements.txt` includes all necessary packages
- [ ] Heavy dependencies reviewed (consider `requirements.vercel.txt`)
- [ ] No local-only dependencies (e.g., system libraries)

### ✅ Environment Setup
- [ ] `.env.vercel.example` reviewed
- [ ] Required environment variables identified
- [ ] Cloud database selected and provisioned
- [ ] Database connection string obtained
- [ ] API keys gathered (Gemini, Notion, Discord, etc.)

### ✅ Code Readiness
- [ ] No hardcoded absolute paths
- [ ] No direct file system writes (except `/tmp`)
- [ ] Database connection uses environment variable
- [ ] Static files are in `web_ui/static/`
- [ ] Templates are in `web_ui/templates/`

## Vercel Account Setup

### ✅ Vercel CLI
- [ ] Node.js installed (v18 or higher)
- [ ] Vercel CLI installed (`npm install -g vercel`)
- [ ] Logged into Vercel (`vercel login`)

### ✅ Vercel Dashboard
- [ ] Account created at https://vercel.com
- [ ] Team/organization selected (if applicable)
- [ ] Payment method added (for Pro features)

## Environment Variables

### ✅ Required Variables
- [ ] `SECRET_KEY` - Flask secret key (random string)
- [ ] `GOOGLE_API_KEY` - Google Gemini API key
- [ ] `DATABASE_URL` - Cloud database connection string

### ✅ Optional Variables
- [ ] `NOTION_API_KEY` - For Notion integration
- [ ] `NOTION_DATABASE_ID` - For Notion publishing
- [ ] `DISCORD_BOT_TOKEN` - For Discord bot
- [ ] `DISCORD_GUILD_ID` - Discord server ID
- [ ] `DISCORD_CHANNEL_ID` - Discord channel ID
- [ ] `IMGBB_API_KEY` - For image hosting

### ✅ Storage Variables (if using external storage)
- [ ] `AWS_ACCESS_KEY_ID` - AWS S3 credentials
- [ ] `AWS_SECRET_ACCESS_KEY` - AWS S3 credentials
- [ ] `AWS_S3_BUCKET` - S3 bucket name
- [ ] `AWS_S3_REGION` - S3 region

## Database Setup

### ✅ Database Configuration
- [ ] Cloud database service selected
- [ ] Database instance created
- [ ] Database schema initialized
- [ ] Connection string tested
- [ ] Firewall rules configured (allow Vercel IPs)
- [ ] Data migrated from SQLite (if applicable)

### ✅ Database Migration (if needed)
- [ ] Existing data exported from SQLite
- [ ] Schema created in cloud database
- [ ] Data imported to cloud database
- [ ] Connection verified

## External Storage (Optional)

### ✅ Storage Setup
- [ ] Storage service selected (S3, R2, etc.)
- [ ] Bucket/container created
- [ ] Access credentials generated
- [ ] Public access configured (for chart images)
- [ ] CORS configured (if needed)

## First Deployment

### ✅ Preview Deployment
- [ ] Run `vercel` command in project root
- [ ] Review preview URL
- [ ] Test basic functionality
- [ ] Check logs for errors
- [ ] Verify environment variables loaded

### ✅ Production Deployment
- [ ] All environment variables set in production scope
- [ ] Run `vercel --prod` command
- [ ] Production URL received
- [ ] Domain configured (optional)
- [ ] SSL certificate active

## Post-Deployment Testing

### ✅ Functionality Tests
- [ ] Homepage loads (`/`)
- [ ] Dashboard displays data
- [ ] API status endpoint works (`/api/status`)
- [ ] Charts page accessible (`/analysis`)
- [ ] Tasks page accessible (`/tasks`)
- [ ] Settings page accessible (`/settings`)
- [ ] Static files load correctly
- [ ] Database queries work
- [ ] WebSocket/polling works (real-time updates)

### ✅ Integration Tests
- [ ] External API calls work (Gemini, etc.)
- [ ] Database reads/writes work
- [ ] File storage works (if configured)
- [ ] Notion publishing works (if configured)
- [ ] Discord integration works (if configured)

### ✅ Performance Tests
- [ ] Page load time acceptable
- [ ] API response time acceptable
- [ ] Cold start time acceptable
- [ ] No timeout errors

## Monitoring & Maintenance

### ✅ Monitoring Setup
- [ ] Vercel dashboard reviewed
- [ ] Function logs accessible
- [ ] Error tracking configured
- [ ] Performance metrics reviewed
- [ ] Alerts configured (optional)

### ✅ Documentation
- [ ] Deployment documented
- [ ] Environment variables documented
- [ ] Known issues documented
- [ ] Team members notified

## Troubleshooting Checklist

### If Deployment Fails
- [ ] Check build logs in Vercel dashboard
- [ ] Verify `vercel.json` syntax
- [ ] Check Python version compatibility
- [ ] Review dependency conflicts
- [ ] Check for missing dependencies

### If Runtime Errors Occur
- [ ] Check function logs
- [ ] Verify environment variables
- [ ] Test database connection
- [ ] Check file path issues
- [ ] Review import errors

### If Performance Issues Occur
- [ ] Monitor function execution time
- [ ] Check database query performance
- [ ] Review cold start times
- [ ] Consider Pro plan upgrade
- [ ] Optimize heavy operations

## Success Criteria

### ✅ Deployment Successful When:
- [ ] All pages load without errors
- [ ] API endpoints return expected data
- [ ] Database operations work correctly
- [ ] Real-time features work (polling fallback OK)
- [ ] No critical errors in logs
- [ ] Performance is acceptable
- [ ] All required integrations work

---

## Ready to Deploy?

If all items above are checked, you're ready to deploy!

```bash
# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

## Need Help?

- 📖 [Quick Start Guide](VERCEL_QUICKSTART.md)
- 📖 [Full Deployment Guide](VERCEL_DEPLOYMENT.md)
- 📖 [Setup Summary](VERCEL_SETUP_SUMMARY.md)
- 🐛 [GitHub Issues](https://github.com/amuzetnoM/syndicate/issues)
- 💬 [Vercel Support](https://vercel.com/support)
