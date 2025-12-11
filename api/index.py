"""
FastAPI with src import test for Vercel.
"""
import sys
import os
from fastapi import FastAPI

# Add parent directory to path for src imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI()

# Try to import src modules
try:
    from src.config.settings import settings
    SETTINGS_AVAILABLE = True
    SETTINGS_ERROR = None
except Exception as e:
    SETTINGS_AVAILABLE = False
    SETTINGS_ERROR = str(e)


@app.get("/")
def home():
    return {
        "message": "FastAPI with src modules",
        "settings_available": SETTINGS_AVAILABLE,
        "settings_error": SETTINGS_ERROR,
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/debug")
def debug():
    return {
        "settings_available": SETTINGS_AVAILABLE,
        "settings_error": SETTINGS_ERROR,
        "cwd": os.getcwd(),
        "file_dir": os.path.dirname(os.path.abspath(__file__)),
        "sys_path": sys.path[:5],
        "env_deepseek": bool(os.getenv("DEEPSEEK_API_KEY")),
    }
