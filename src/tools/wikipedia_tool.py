"""
Herramienta de Wikipedia para el Agente.

Esta herramienta permite al agente consultar información enciclopédica
de Wikipedia en español e inglés.

Ejemplo de uso:
    from src.tools.wikipedia_tool import wikipedia_tool

    result = wikipedia_tool.invoke("Albert Einstein")
    print(result)
"""

from typing import Optional
from langchain.tools import tool

# Intentar importar Wikipedia
try:
    from langchain_community.utilities import WikipediaAPIWrapper
    WIKIPEDIA_AVAILABLE = True
except ImportError:
    WIKIPEDIA_AVAILABLE = False

try:
    import wikipedia
    WIKIPEDIA_DIRECT_AVAILABLE = True
except ImportError:
    WIKIPEDIA_DIRECT_AVAILABLE = False


class WikipediaSearcher:
    """
    Clase que encapsula la lógica de consulta a Wikipedia.

    Proporciona acceso a artículos de Wikipedia con resúmenes
    concisos y relevantes.

    Attributes:
        wiki: El wrapper de Wikipedia de LangChain
        available: Si Wikipedia está disponible
    """

    def __init__(self, lang: str = "es", top_k_results: int = 3, doc_content_chars_max: int = 4000):
        """
        Inicializa el buscador de Wikipedia.

        Args:
            lang: Idioma de Wikipedia ("es" para español, "en" para inglés)
            top_k_results: Número máximo de resultados a retornar
            doc_content_chars_max: Máximo de caracteres por documento
        """
        self.available = False
        self.wiki = None
        self.lang = lang

        if WIKIPEDIA_AVAILABLE:
            try:
                self.wiki = WikipediaAPIWrapper(
                    lang=lang,
                    top_k_results=top_k_results,
                    doc_content_chars_max=doc_content_chars_max
                )
                self.available = True
            except Exception:
                pass

    def search(self, query: str) -> str:
        """
        Busca información en Wikipedia.

        Args:
            query: El término o tema a buscar

        Returns:
            Resumen del artículo de Wikipedia
        """
        if not self.available:
            return self._fallback_search(query)

        try:
            result = self.wiki.run(query)
            return result if result else f"No se encontró información sobre '{query}' en Wikipedia."

        except Exception as e:
            # Intentar fallback si falla
            return self._fallback_search(query)

    def _fallback_search(self, query: str) -> str:
        """
        Búsqueda alternativa usando la librería wikipedia directamente.

        Args:
            query: El término a buscar

        Returns:
            Resumen del artículo
        """
        if not WIKIPEDIA_DIRECT_AVAILABLE:
            return (
                "Error: Wikipedia no está disponible. "
                "Instala 'wikipedia' con: pip install wikipedia"
            )

        try:
            # Configurar idioma
            wikipedia.set_lang(self.lang)

            # Buscar artículo
            search_results = wikipedia.search(query, results=3)

            if not search_results:
                return f"No se encontraron artículos sobre '{query}' en Wikipedia."

            # Obtener resumen del primer resultado
            try:
                summary = wikipedia.summary(search_results[0], sentences=5)
                return f"**{search_results[0]}**\n\n{summary}"
            except wikipedia.DisambiguationError as e:
                # Si hay ambigüedad, tomar la primera opción
                if e.options:
                    summary = wikipedia.summary(e.options[0], sentences=5)
                    return f"**{e.options[0]}**\n\n{summary}"
                return f"Término ambiguo. Opciones: {', '.join(e.options[:5])}"

        except Exception as e:
            return f"Error al consultar Wikipedia: {str(e)}"


# Instancia global del buscador
_wiki_searcher: Optional[WikipediaSearcher] = None


def initialize_wikipedia(lang: str = "es") -> WikipediaSearcher:
    """
    Inicializa el buscador de Wikipedia.

    Args:
        lang: Código de idioma ("es", "en", etc.)

    Returns:
        La instancia del buscador configurado
    """
    global _wiki_searcher
    _wiki_searcher = WikipediaSearcher(lang=lang)
    return _wiki_searcher


def get_wikipedia_searcher() -> WikipediaSearcher:
    """
    Obtiene la instancia del buscador de Wikipedia.

    Returns:
        La instancia del buscador
    """
    global _wiki_searcher
    if _wiki_searcher is None:
        _wiki_searcher = WikipediaSearcher()
    return _wiki_searcher


@tool
def wikipedia_tool(query: str) -> str:
    """
    Consulta información enciclopédica en Wikipedia.

    Útil para obtener información sobre:
    - Biografías de personas famosas
    - Historia de países, ciudades o eventos
    - Conceptos científicos o técnicos
    - Definiciones y explicaciones detalladas
    - Datos históricos

    Args:
        query: El tema o término a buscar.
               Ejemplo: "Albert Einstein", "Segunda Guerra Mundial", "Fotosíntesis"

    Returns:
        Un resumen del artículo de Wikipedia sobre el tema.

    Note:
        Los resultados están en español por defecto.
        Para temas muy específicos, puede no encontrar resultados.
    """
    searcher = get_wikipedia_searcher()
    return searcher.search(query)


# Información sobre el estado de Wikipedia
def get_wikipedia_status() -> dict:
    """
    Obtiene información sobre el estado del buscador de Wikipedia.

    Returns:
        Dict con información del estado
    """
    return {
        "langchain_wrapper_available": WIKIPEDIA_AVAILABLE,
        "wikipedia_direct_available": WIKIPEDIA_DIRECT_AVAILABLE,
        "configured": _wiki_searcher is not None,
    }


# Para uso directo del módulo
if __name__ == "__main__":
    print("Estado de Wikipedia:")
    print("-" * 40)

    status = get_wikipedia_status()
    for key, value in status.items():
        print(f"{key}: {value}")

    print("\nPrueba de consulta:")
    print("-" * 40)

    result = wikipedia_tool.invoke("Python (lenguaje de programación)")
    print(result[:800] + "..." if len(result) > 800 else result)
