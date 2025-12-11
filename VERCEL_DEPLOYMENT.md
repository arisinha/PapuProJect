# Vercel Deployment Guide

This guide will help you deploy the Agente Calculadora app to Vercel.

## Prerequisites

1. A [Vercel account](https://vercel.com/signup)
2. [Vercel CLI](https://vercel.com/cli) installed (optional, but recommended)

## Deployment Steps

### Option 1: Deploy via Vercel CLI (Recommended)

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy from the project directory**:
   ```bash
   vercel
   ```
   
   Follow the prompts:
   - Set up and deploy? **Y**
   - Which scope? Select your account
   - Link to existing project? **N** (for first deployment)
   - What's your project's name? **papu-project** (or your preferred name)
   - In which directory is your code located? **./**
   - Want to override the settings? **N**

4. **Set environment variables**:
   ```bash
   vercel env add DEEPSEEK_API_KEY
   vercel env add SERPAPI_API_KEY
   ```
   
   When prompted, paste your API keys and select all environments (production, preview, development).

5. **Deploy to production**:
   ```bash
   vercel --prod
   ```

### Option 2: Deploy via GitHub Integration

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Add Vercel configuration"
   git push origin main
   ```

2. **Import project in Vercel**:
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "Add New..." → "Project"
   - Import your GitHub repository
   - Vercel will auto-detect the configuration

3. **Configure environment variables**:
   - In the project settings, go to "Environment Variables"
   - Add the following variables:
     - `DEEPSEEK_API_KEY`: Your DeepSeek API key
     - `SERPAPI_API_KEY`: Your SerpAPI key
   - Make sure to add them for all environments

4. **Deploy**:
   - Click "Deploy"
   - Vercel will build and deploy your app

## Environment Variables

Make sure to set these in Vercel:

| Variable | Description | Example |
|----------|-------------|---------|
| `DEEPSEEK_API_KEY` | Your DeepSeek API key | `sk-...` |
| `SERPAPI_API_KEY` | Your SerpAPI key | `0a2b...` |
| `DEEPSEEK_MODEL` | Model name (optional) | `deepseek-chat` |
| `AGENT_VERBOSE` | Enable verbose logging (optional) | `false` |

## Important Notes

1. **Serverless Functions**: Vercel runs Python apps as serverless functions with a 10-second timeout on the free tier. For longer operations, consider upgrading to Pro.

2. **Static Files**: The `web/static` directory is served automatically through the FastAPI app.

3. **Cold Starts**: The first request after inactivity may be slower due to cold starts.

4. **Dependencies**: All dependencies in `requirements.txt` will be installed automatically.

## Troubleshooting

### Build Fails
- Check that all dependencies in `requirements.txt` are compatible with Vercel's Python runtime
- Ensure environment variables are set correctly

### 404 Errors
- Verify that `vercel.json` routing is correct
- Check that the `api/index.py` file exists

### Timeout Errors
- Consider upgrading to Vercel Pro for longer execution times
- Optimize your agent's operations

## Local Testing

To test the Vercel build locally:

```bash
vercel dev
```

This will start a local development server that mimics Vercel's environment.

## Custom Domain

After deployment, you can add a custom domain:
1. Go to your project settings in Vercel
2. Navigate to "Domains"
3. Add your custom domain and follow the DNS configuration instructions

## Monitoring

Monitor your deployment:
- **Logs**: View real-time logs in the Vercel dashboard
- **Analytics**: Enable analytics in project settings
- **Performance**: Check function execution times and errors

## Support

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [FastAPI on Vercel](https://vercel.com/guides/deploying-fastapi-with-vercel)
