"""
Vercel serverless function entry point for the FastAPI app.
"""
import sys
import os

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.app import app

# This is required for Vercel
handler = app
