"""
Minimal API for Vercel - Testing basic functionality.
"""
import sys
import os
from datetime import datetime

from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Create the app
app = FastAPI(title="Test API")


@app.get("/")
async def root():
    """Basic root endpoint."""
    return {"message": "Hello from Vercel!", "timestamp": datetime.now().isoformat()}


@app.get("/api/health")
async def health():
    """Health check."""
    return {"status": "ok"}


@app.get("/api/debug")
async def debug():
    """Debug info."""
    return {
        "python_version": sys.version,
        "cwd": os.getcwd(),
        "file_location": __file__,
        "env_deepseek_key_set": bool(os.getenv("DEEPSEEK_API_KEY")),
        "files_in_cwd": os.listdir(os.getcwd())[:10] if os.path.isdir(os.getcwd()) else "N/A",
    }


# Required for Vercel
handler = app
