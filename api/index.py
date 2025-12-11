"""
API Web para el Agente Calculadora + Búsqueda.

Este módulo proporciona una API REST usando FastAPI para interactuar
con el agente desde una interfaz web.
"""

import sys
import os
from typing import Optional, List
from datetime import datetime

# Add root directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from src.agents import CalculatorSearchAgent
from src.config.settings import settings


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
    try:
        if agent is None:
            print("Validating settings...")
            settings.validate()
            print("Settings validated. Creating agent...")
            agent = CalculatorSearchAgent(verbose=False)
            print("Agent created successfully.")
    except Exception as e:
        print(f"CRITICAL ERROR initializing agent: {e}")
        # Re-raise so Vercel logs show it clearly
        raise e
    return agent


@app.get("/")
async def root():
    """Serve the main HTML page."""
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "index.html"))


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


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
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")


# This is required for Vercel
handler = app
