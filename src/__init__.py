"""
Agente Calculadora + Busqueda.

Un agente inteligente que usa LangChain y DeepSeek para realizar
calculos matematicos, buscar en la web y consultar Wikipedia.

Uso rapido:
    from src import CalculatorSearchAgent

    agent = CalculatorSearchAgent()
    response = agent.run("Cuanto es 15% de 200?")
    print(response)  # 30
"""

from src.agents import CalculatorSearchAgent, create_agent
from src.config.settings import settings

__version__ = "1.0.0"
__author__ = "Tu Nombre"

__all__ = [
    "CalculatorSearchAgent",
    "create_agent",
    "settings",
]
