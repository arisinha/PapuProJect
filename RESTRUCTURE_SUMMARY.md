# Project Restructure for Vercel Deployment

## Changes Made

The project has been reorganized to follow Vercel's expected structure for Python serverless functions.

### What Changed

1. **Moved FastAPI app to `api/index.py`**
   - Previously, the app was in `web/app.py` and `api/index.py` just imported it
   - Now, `api/index.py` contains the complete FastAPI application
   - This ensures Vercel can properly recognize and deploy the serverless function

2. **Copied static files to `api/static/`**
   - Static files (HTML, CSS, JS) are now in `api/static/`
   - The FastAPI app serves these files from the correct location
   - Files include:
     - `index.html` - Main web interface
     - `styles.css` - Styling
     - `app.js` - Frontend JavaScript

3. **Updated file paths**
   - Static file serving now points to `api/static/` directory
   - All imports remain pointing to the `src/` directory in the project root

### Project Structure

```
PapuProJect/
├── api/
│   ├── index.py          # Main FastAPI app (Vercel entry point)
│   └── static/           # Static web files
│       ├── index.html
│       ├── styles.css
│       └── app.js
├── src/                  # Agent source code
│   ├── agents/
│   ├── config/
│   └── tools/
├── web/                  # Original web files (can be kept or removed)
│   ├── app.py
│   └── static/
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables

```

### How Vercel Recognizes the Files

1. **Entry Point**: `vercel.json` specifies `api/index.py` as the build source
2. **Serverless Function**: Vercel converts `api/index.py` into a serverless function
3. **Static Files**: The FastAPI app serves static files from `api/static/`
4. **Routes**: All routes (`/`, `/api/*`, `/static/*`) are handled by the FastAPI app

### Next Steps for Deployment

1. **Set environment variables in Vercel**:
   - `DEEPSEEK_API_KEY`
   - `SERPAPI_API_KEY`
   - Other optional variables are already in `vercel.json`

2. **Deploy**:
   ```bash
   vercel --prod
   ```

3. **Test the deployment**:
   - Visit your Vercel URL
   - Test the chat interface
   - Verify API endpoints work

### Optional Cleanup

You can optionally remove the old `web/` directory since the files are now in `api/`:
```bash
rm -rf web/
```

However, keeping it won't affect the Vercel deployment.
