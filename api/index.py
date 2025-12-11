"""
Minimal Flask API for Vercel.
"""
from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return "Hello from Vercel!"


@app.route("/api/health")
def health():
    return {"status": "ok"}
