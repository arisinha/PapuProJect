"""
FastAPI test for Vercel.
"""
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Hello from FastAPI on Vercel!"}


@app.get("/api/health")
def health():
    return {"status": "ok"}
