"""
Herramientas disponibles para el Agente.

Este modulo exporta todas las herramientas que el agente puede usar:
- calculator_tool: Para calculos matematicos
- web_search_tool: Para busquedas en internet
- wikipedia_tool: Para consultas enciclopedicas
- datetime_tool: Para operaciones con fechas y horas
- unit_converter_tool: Para conversion de unidades
- text_analyzer_tool: Para analisis de texto
- text_transform_tool: Para transformaciones de texto
- random_generator_tool: Para generacion aleatoria
- weather_tool: Para consultar el clima

Uso:
    from src.tools import calculator_tool, web_search_tool, wikipedia_tool

    # O importar todas
    from src.tools import get_all_tools
    tools = get_all_tools()
"""

from src.tools.calculator import calculator_tool
from src.tools.web_search import (
    web_search_tool,
    initialize_searcher,
    get_search_status
)
from src.tools.wikipedia_tool import (
    wikipedia_tool,
    initialize_wikipedia,
    get_wikipedia_status
)
from src.tools.datetime_tool import datetime_tool
from src.tools.unit_converter import unit_converter_tool
from src.tools.text_tools import (
    text_analyzer_tool,
    text_transform_tool,
    random_generator_tool
)
from src.tools.weather_tool import weather_tool


def get_all_tools(serpapi_key: str = None, wikipedia_lang: str = "es") -> list:
    """
    Obtiene todas las herramientas configuradas.

    Args:
        serpapi_key: API key para SerpAPI (opcional)
        wikipedia_lang: Idioma para Wikipedia

    Returns:
        Lista de herramientas configuradas
    """
    # Inicializar herramientas que requieren configuracion
    initialize_searcher(serpapi_key)
    initialize_wikipedia(wikipedia_lang)

    return [
        calculator_tool,
        web_search_tool,
        wikipedia_tool,
        datetime_tool,
        unit_converter_tool,
        text_analyzer_tool,
        text_transform_tool,
        random_generator_tool,
        weather_tool,
    ]


__all__ = [
    # Herramientas originales
    "calculator_tool",
    "web_search_tool",
    "wikipedia_tool",
    # Nuevas herramientas
    "datetime_tool",
    "unit_converter_tool",
    "text_analyzer_tool",
    "text_transform_tool",
    "random_generator_tool",
    "weather_tool",
    # Funciones auxiliares
    "get_all_tools",
    "initialize_searcher",
    "initialize_wikipedia",
    "get_search_status",
    "get_wikipedia_status",
]
