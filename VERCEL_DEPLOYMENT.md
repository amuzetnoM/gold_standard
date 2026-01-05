# Vercel Deployment Guide for Syndicate

This guide explains how to deploy the Syndicate Web UI to Vercel's platform.

## Overview

Syndicate is deployed to Vercel as a Python serverless application. The Flask web application is adapted to work with Vercel's serverless functions architecture.

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Vercel CLI** (optional but recommended):
   ```bash
   npm install -g vercel
   ```

## Quick Deployment

### Option 1: Deploy via Vercel CLI

1. Install Vercel CLI:
   ```bash
   npm install -g vercel
   ```

2. Login to Vercel:
   ```bash
   vercel login
   ```

3. Deploy from the project root:
   ```bash
   vercel
   ```

4. For production deployment:
   ```bash
   vercel --prod
   ```

### Option 2: Deploy via GitHub Integration

1. Push your code to GitHub
2. Go to [vercel.com/new](https://vercel.com/new)
3. Import your GitHub repository
4. Vercel will automatically detect the configuration from `vercel.json`
5. Click "Deploy"

## Configuration Files

### `vercel.json`
Main Vercel configuration file that defines:
- Build settings for Python runtime
- Route mappings
- Environment variables
- Function memory and timeout limits

### `api/index.py`
Serverless function entry point that adapts the Flask application for Vercel.

### `.vercelignore`
Specifies files to exclude from deployment (similar to `.gitignore`).

### `package.json`
Provides project metadata and deployment scripts for Vercel.

## Environment Variables

Configure these environment variables in your Vercel project settings:

### Required Variables

```bash
# Flask Configuration
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=production

# Database (use external service for production)
# Note: SQLite files don't persist in Vercel's serverless environment
# Consider using PostgreSQL, MySQL, or a managed database service
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# AI API Keys
GOOGLE_API_KEY=your-google-gemini-api-key

# Optional: Notion Integration
NOTION_API_KEY=your-notion-api-key
NOTION_DATABASE_ID=your-notion-database-id

# Optional: Discord Bot
DISCORD_BOT_TOKEN=your-discord-bot-token

# Optional: Image Hosting
IMGBB_API_KEY=your-imgbb-api-key
```

### Setting Environment Variables

#### Via Vercel Dashboard:
1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add each variable with appropriate scope (Production, Preview, Development)

#### Via Vercel CLI:
```bash
vercel env add SECRET_KEY
vercel env add GOOGLE_API_KEY
vercel env add DATABASE_URL
```

## Important Limitations

### 1. WebSocket Support
- **Issue**: Flask-SocketIO WebSockets have limited support in Vercel's serverless environment
- **Solution**: Real-time features will work via polling fallback, or consider:
  - Using Vercel's Edge Functions
  - External WebSocket service (e.g., Pusher, Ably)
  - Deploying the WebSocket server separately

### 2. File System
- **Issue**: Vercel serverless functions have read-only file systems (except `/tmp`)
- **Solution**: 
  - Use external storage for charts/reports (S3, Cloudflare R2, etc.)
  - Store data in external database
  - Use `/tmp` for temporary files (cleared between invocations)

### 3. Database
- **Issue**: SQLite files don't persist between function invocations
- **Solution**: Use a managed database service:
  - Vercel Postgres
  - PlanetScale (MySQL)
  - Supabase (PostgreSQL)
  - MongoDB Atlas

### 4. Execution Time
- **Limit**: Maximum function execution time (10s on Hobby, 60s on Pro)
- **Solution**: Offload long-running tasks to background jobs or separate services

## Database Migration

To migrate from SQLite to a cloud database:

1. **Export existing data**:
   ```bash
   python db_manager.py export --output data.json
   ```

2. **Set up cloud database** (example with PostgreSQL):
   ```bash
   # Install PostgreSQL adapter
   pip install psycopg2-binary
   
   # Update connection in code
   DATABASE_URL=postgresql://...
   ```

3. **Import data**:
   ```bash
   python db_manager.py import --input data.json
   ```

## Testing Locally

Test the Vercel deployment locally before pushing:

```bash
# Install Vercel CLI
npm install -g vercel

# Run development server
vercel dev

# Access at http://localhost:3000
```

## Monitoring and Logs

### View Logs:
```bash
vercel logs [deployment-url]
```

### Via Dashboard:
1. Go to your project on vercel.com
2. Click on a deployment
3. View "Functions" tab for execution logs

## Troubleshooting

### Issue: Module Import Errors
**Solution**: Ensure all dependencies are in `requirements.txt` at the project root.

### Issue: Static Files Not Loading
**Solution**: Check the `routes` configuration in `vercel.json` for proper static file routing.

### Issue: Database Connection Fails
**Solution**: Verify `DATABASE_URL` environment variable is set correctly.

### Issue: Function Timeout
**Solution**: 
- Optimize slow operations
- Consider upgrading to Vercel Pro for longer timeouts
- Move intensive tasks to background workers

### Issue: WebSocket Not Working
**Solution**: 
- Use long-polling fallback (automatically handled by SocketIO)
- Consider alternative real-time solutions mentioned above

## Performance Optimization

1. **Enable Caching**: Use Vercel's Edge Network for static assets
2. **Database Indexes**: Add indexes for frequently queried fields
3. **Code Splitting**: Load only necessary modules in each function
4. **Asset Optimization**: Compress images and minify CSS/JS

## Production Checklist

- [ ] Set all required environment variables
- [ ] Configure external database
- [ ] Set up external file storage for charts/reports
- [ ] Change `SECRET_KEY` to a secure random value
- [ ] Configure custom domain (optional)
- [ ] Set up monitoring/alerting
- [ ] Test all API endpoints
- [ ] Verify WebSocket/polling fallback works
- [ ] Review Vercel function logs
- [ ] Set up CI/CD pipeline (Vercel has built-in GitHub integration)

## Custom Domain

To use a custom domain:

1. Go to Project Settings → Domains
2. Add your domain
3. Configure DNS records as shown
4. Wait for SSL certificate provisioning

## Cost Considerations

- **Hobby Plan**: Free tier with limitations (10s function timeout)
- **Pro Plan**: $20/month with better limits (60s timeout)
- **Enterprise**: Custom pricing for high-scale deployments

Monitor your usage at: [vercel.com/dashboard/usage](https://vercel.com/dashboard/usage)

## Support

- **Vercel Documentation**: https://vercel.com/docs
- **Vercel Discord**: https://vercel.com/discord
- **GitHub Issues**: https://github.com/amuzetnoM/syndicate/issues

## Alternative Deployment Options

If Vercel's limitations are too restrictive, consider:
- **Railway**: Better for long-running processes
- **Render**: Good for WebSocket support
- **Fly.io**: Full VM control
- **Heroku**: Traditional PaaS
- **AWS Lambda + API Gateway**: More control over serverless
- **Google Cloud Run**: Container-based serverless

## Next Steps

1. Complete the deployment using one of the methods above
2. Configure environment variables
3. Set up external database
4. Test the deployment thoroughly
5. Monitor logs and performance
6. Set up custom domain (optional)

For more information, see the main [Web UI README](web_ui/README.md).
