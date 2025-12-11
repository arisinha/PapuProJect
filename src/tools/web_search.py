"""
Herramienta de Búsqueda Web para el Agente.

Esta herramienta permite al agente buscar información actualizada
en internet usando SerpAPI o DuckDuckGo como fallback.

Ejemplo de uso:
    from src.tools.web_search import web_search_tool

    result = web_search_tool.invoke("clima en Madrid hoy")
    print(result)
"""

from typing import Optional
from langchain.tools import tool

# Intentar importar SerpAPI, si no está disponible usar DuckDuckGo
try:
    from langchain_community.utilities import SerpAPIWrapper
    SERPAPI_AVAILABLE = True
except ImportError:
    SERPAPI_AVAILABLE = False

try:
    from langchain_community.tools import DuckDuckGoSearchRun
    DUCKDUCKGO_AVAILABLE = True
except ImportError:
    DUCKDUCKGO_AVAILABLE = False


class WebSearcher:
    """
    Clase que encapsula la lógica de búsqueda web.

    Intenta usar SerpAPI primero (mejor calidad), y si no está
    disponible, usa DuckDuckGo como alternativa gratuita.

    Attributes:
        search_engine: El motor de búsqueda configurado
        engine_name: Nombre del motor en uso
    """

    def __init__(self, serpapi_key: Optional[str] = None):
        """
        Inicializa el buscador web.

        Args:
            serpapi_key: API key de SerpAPI (opcional)
        """
        self.search_engine = None
        self.engine_name = "none"

        # Intentar configurar SerpAPI
        if serpapi_key and SERPAPI_AVAILABLE:
            try:
                self.search_engine = SerpAPIWrapper(serpapi_api_key=serpapi_key)
                self.engine_name = "SerpAPI"
                return
            except Exception:
                pass

        # Fallback a DuckDuckGo
        if DUCKDUCKGO_AVAILABLE:
            try:
                from duckduckgo_search import DDGS
                self.search_engine = DDGS()
                self.engine_name = "DuckDuckGo"
                return
            except Exception as e:
                print(f"Error inicializando DuckDuckGo: {e}")

    def search(self, query: str) -> str:
        """
        Realiza una busqueda web.

        Args:
            query: La consulta de busqueda

        Returns:
            Los resultados de la busqueda como texto
        """
        if self.search_engine is None:
            return (
                "Error: No hay motor de busqueda disponible. "
                "Instala 'google-search-results' para SerpAPI o "
                "'duckduckgo-search' para DuckDuckGo."
            )

        try:
            if self.engine_name == "SerpAPI":
                result = self.search_engine.run(query)
            else:
                # DuckDuckGo usando DDGS directamente
                results = self.search_engine.text(query, max_results=5)
                if results:
                    formatted = []
                    for r in results:
                        formatted.append(f"- {r.get('title', '')}: {r.get('body', '')}")
                    result = "\n".join(formatted)
                else:
                    result = None

            return result if result else "No se encontraron resultados."

        except Exception as e:
            return f"Error en la busqueda: {str(e)}"


# Instancia global del buscador (se configura en el agente)
_searcher: Optional[WebSearcher] = None


def initialize_searcher(serpapi_key: Optional[str] = None) -> WebSearcher:
    """
    Inicializa el buscador web global.

    Args:
        serpapi_key: API key de SerpAPI

    Returns:
        La instancia del buscador configurado
    """
    global _searcher
    _searcher = WebSearcher(serpapi_key)
    return _searcher


def get_searcher() -> WebSearcher:
    """
    Obtiene la instancia del buscador web.

    Si no está inicializado, crea uno con configuración por defecto.

    Returns:
        La instancia del buscador
    """
    global _searcher
    if _searcher is None:
        _searcher = WebSearcher()
    return _searcher


@tool
def web_search_tool(query: str) -> str:
    """
    Busca información actual en internet.

    Útil para obtener información actualizada como:
    - Noticias recientes
    - Precios y cotizaciones actuales
    - Eventos actuales
    - Información que cambia frecuentemente

    Args:
        query: La consulta de búsqueda en lenguaje natural.
               Ejemplo: "precio del bitcoin hoy", "noticias de tecnología"

    Returns:
        Los resultados de la búsqueda relevantes.

    Note:
        Esta herramienta requiere conexión a internet.
        Si SerpAPI está configurado, se usará para mejores resultados.
        De lo contrario, se usa DuckDuckGo como alternativa gratuita.
    """
    searcher = get_searcher()
    return searcher.search(query)


# Información sobre el estado del buscador
def get_search_status() -> dict:
    """
    Obtiene información sobre el estado del buscador.

    Returns:
        Dict con información del motor de búsqueda activo
    """
    searcher = get_searcher()
    return {
        "engine": searcher.engine_name,
        "available": searcher.search_engine is not None,
        "serpapi_available": SERPAPI_AVAILABLE,
        "duckduckgo_available": DUCKDUCKGO_AVAILABLE,
    }


# Para uso directo del módulo
if __name__ == "__main__":
    print("Estado del buscador web:")
    print("-" * 40)

    status = get_search_status()
    for key, value in status.items():
        print(f"{key}: {value}")

    print("\nPrueba de búsqueda:")
    print("-" * 40)

    result = web_search_tool.invoke("Python programming language")
    print(result[:500] + "..." if len(result) > 500 else result)
