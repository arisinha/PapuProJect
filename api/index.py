"""
API Web para el Agente Calculadora + Búsqueda.

Este módulo proporciona una API REST usando FastAPI para interactuar
con el agente desde una interfaz web.
"""

import sys
import os
from typing import Optional, List
from datetime import datetime

# Add root directory to path - try multiple strategies for Vercel compatibility
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)

# Strategy 1: Parent directory (works locally when running from api/)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

# Strategy 2: Current working directory (may work on some Vercel configs)
_cwd = os.getcwd()
if _cwd not in sys.path:
    sys.path.insert(0, _cwd)

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# Lazy imports for modules that might fail - wrap in try-except
try:
    from src.agents import CalculatorSearchAgent
    from src.config.settings import settings
    AGENT_AVAILABLE = True
    IMPORT_ERROR = None
except ImportError as e:
    AGENT_AVAILABLE = False
    IMPORT_ERROR = str(e)
    CalculatorSearchAgent = None
    settings = None


# Initialize FastAPI app
app = FastAPI(
    title="Agente Calculadora + Búsqueda",
    description="API para interactuar con el agente inteligente basado en LangChain y DeepSeek",
    version="1.0.0"
)

# Global agent instance
agent: Optional[CalculatorSearchAgent] = None


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str
    timestamp: str


class ToolInfo(BaseModel):
    """Model for tool information."""
    name: str
    description: str
    icon: str


class ChatWithStepsResponse(BaseModel):
    """Response model for chat with steps."""
    response: str
    steps: List[dict]
    timestamp: str


# Tool icons mapping
TOOL_ICONS = {
    "calculator_tool": "📊",
    "web_search_tool": "🔍",
    "wikipedia_tool": "📚",
    "datetime_tool": "📅",
    "unit_converter_tool": "📐",
    "text_analyzer_tool": "📝",
    "text_transform_tool": "🔄",
    "random_generator_tool": "🎲",
    "weather_tool": "🌤️",
}


def get_agent() -> CalculatorSearchAgent:
    """Get or create the agent instance."""
    global agent
    
    # Check if agent modules were imported successfully
    if not AGENT_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail=f"Agent not available. Import error: {IMPORT_ERROR}"
        )
    
    try:
        if agent is None:
            print("Validating settings...")
            settings.validate()
            print("Settings validated. Creating agent...")
            agent = CalculatorSearchAgent(verbose=False)
            print("Agent created successfully.")
    except Exception as e:
        print(f"CRITICAL ERROR initializing agent: {e}")
        raise HTTPException(status_code=503, detail=f"Agent initialization failed: {str(e)}")
    return agent


@app.get("/")
async def root():
    """Serve the main HTML page."""
    try:
        html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
        if os.path.isfile(html_path):
            return FileResponse(html_path)
        else:
            return {"message": "API is running. Static files not available.", "docs": "/docs"}
    except Exception as e:
        return {"error": str(e), "docs": "/docs"}


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.get("/api/debug")
async def debug_info():
    """Debug endpoint to diagnose deployment issues."""
    return {
        "agent_available": AGENT_AVAILABLE,
        "import_error": IMPORT_ERROR,
        "python_version": sys.version,
        "cwd": os.getcwd(),
        "file_dir": os.path.dirname(os.path.abspath(__file__)),
        "sys_path": sys.path[:5],  # First 5 entries
        "env_vars_set": {
            "DEEPSEEK_API_KEY": bool(os.getenv("DEEPSEEK_API_KEY")),
            "DEEPSEEK_MODEL": os.getenv("DEEPSEEK_MODEL", "not set"),
        },
        "static_dir_exists": os.path.isdir(os.path.join(os.path.dirname(__file__), "static")),
        "src_dir_exists": os.path.isdir(os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")),
    }


@app.get("/api/tools", response_model=List[ToolInfo])
async def get_tools():
    """Get available tools information."""
    try:
        agent = get_agent()
        tools_info = agent.get_tools_info()
        return [
            ToolInfo(
                name=tool["name"],
                description=tool["description"],
                icon=TOOL_ICONS.get(tool["name"], "🔧")
            )
            for tool in tools_info
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message and return the agent's response."""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío")
    
    try:
        agent = get_agent()
        response = agent.run(request.message)
        return ChatResponse(
            response=response,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/stream", response_model=ChatWithStepsResponse)
async def chat_with_steps(request: ChatRequest):
    """Process a chat message and return response with intermediate steps."""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="El mensaje no puede estar vacío")
    
    try:
        agent = get_agent()
        result = agent.run_with_steps(request.message)
        
        # Process messages to extract steps
        steps = []
        for msg in result.get("messages", []):
            step = {}
            if hasattr(msg, 'type'):
                step["type"] = msg.type
            if hasattr(msg, 'content'):
                step["content"] = msg.content
            if hasattr(msg, 'name'):
                step["tool"] = msg.name
            if step:
                steps.append(step)
        
        return ChatWithStepsResponse(
            response=result.get("output", ""),
            steps=steps,
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Mount static files (after defining routes)
# Wrapped in try-except because Vercel's serverless environment may not have the static directory
try:
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.isdir(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    else:
        print(f"WARNING: Static directory not found at {static_dir}")
except Exception as e:
    print(f"WARNING: Could not mount static files: {e}")


# Vercel auto-detects the FastAPI 'app' object

