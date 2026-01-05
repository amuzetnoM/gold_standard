# Quick Start: Deploy Syndicate to Vercel

## 1. Install Vercel CLI

```bash
npm install -g vercel
```

## 2. Login to Vercel

```bash
vercel login
```

## 3. Configure Environment Variables (Required)

Create a `.env` file in the project root with your configuration:

```bash
# Copy the example file
cp .env.vercel.example .env

# Edit with your values
nano .env
```

**Minimum required variables:**
```bash
SECRET_KEY=your-secret-key-here
GOOGLE_API_KEY=your-google-gemini-api-key
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

## 4. Deploy to Vercel

### Development/Preview Deployment
```bash
vercel
```

### Production Deployment
```bash
vercel --prod
```

## 5. Set Environment Variables in Vercel

After first deployment, set your environment variables:

```bash
# Set each variable
vercel env add SECRET_KEY
vercel env add GOOGLE_API_KEY
vercel env add DATABASE_URL

# Pull environment variables to local
vercel env pull
```

Or set them via the Vercel Dashboard:
1. Go to https://vercel.com/dashboard
2. Select your project
3. Go to Settings → Environment Variables
4. Add each variable

## 6. Redeploy with Environment Variables

```bash
vercel --prod
```

## Common Commands

```bash
# Local development with Vercel
vercel dev

# Check deployment status
vercel ls

# View logs
vercel logs

# Remove a deployment
vercel rm [deployment-url]

# Link local project to Vercel project
vercel link
```

## Troubleshooting

### Issue: "No builds matched"
**Fix:** Ensure `api/index.py` exists and `vercel.json` is properly configured.

### Issue: Module import errors
**Fix:** Check that `requirements.txt` includes all necessary dependencies.

### Issue: Database connection fails
**Fix:** Ensure `DATABASE_URL` environment variable is set in Vercel dashboard.

### Issue: Function timeout
**Fix:** Optimize code or upgrade to Vercel Pro for 60s timeout.

## Next Steps

1. ✅ Deploy to Vercel
2. ✅ Set environment variables
3. ✅ Configure external database
4. ✅ Test the deployment
5. ⚙️ Set up custom domain (optional)
6. 📊 Monitor performance and logs

For detailed information, see [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md)
