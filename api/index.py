"""
Ultra-minimal API - No external dependencies, pure Python.
"""
import json
from datetime import datetime


def handler(request):
    """Handle incoming requests - Vercel Python runtime format."""
    path = request.get("path", "/")
    
    response_body = {
        "message": "Hello from pure Python!",
        "path": path,
        "timestamp": datetime.now().isoformat(),
        "python_works": True
    }
    
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response_body)
    }
