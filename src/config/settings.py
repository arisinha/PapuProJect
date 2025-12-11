"""
Configuración centralizada del Agente.

Este módulo carga las variables de entorno y proporciona
una interfaz limpia para acceder a la configuración.

Uso:
    from src.config.settings import settings

    api_key = settings.DEEPSEEK_API_KEY
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()


@dataclass
class Settings:
    """
    Clase de configuración que encapsula todas las variables de entorno.

    Attributes:
        DEEPSEEK_API_KEY: API key para DeepSeek (requerido)
        DEEPSEEK_MODEL: Modelo de DeepSeek a usar
        DEEPSEEK_API_BASE: URL base de la API de DeepSeek
        SERPAPI_API_KEY: API key para SerpAPI (opcional)
        AGENT_VERBOSE: Si mostrar el razonamiento del agente
        AGENT_MAX_ITERATIONS: Máximo de iteraciones del agente
        LLM_TEMPERATURE: Temperatura del modelo
        LOG_LEVEL: Nivel de logging
    """

    # DeepSeek Configuration
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    DEEPSEEK_API_BASE: str = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")

    # SerpAPI Configuration (opcional)
    SERPAPI_API_KEY: Optional[str] = os.getenv("SERPAPI_API_KEY")

    # Agent Configuration
    AGENT_VERBOSE: bool = os.getenv("AGENT_VERBOSE", "true").lower() == "true"
    AGENT_MAX_ITERATIONS: int = int(os.getenv("AGENT_MAX_ITERATIONS", "10"))

    # LLM Configuration
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    def validate(self) -> bool:
        """
        Valida que las configuraciones requeridas estén presentes.

        Returns:
            bool: True si la configuración es válida

        Raises:
            ValueError: Si falta alguna configuración requerida
        """
        if not self.DEEPSEEK_API_KEY:
            raise ValueError(
                "DEEPSEEK_API_KEY no está configurada. "
                "Por favor, crea un archivo .env con tu API key. "
                "Puedes usar .env.example como referencia."
            )
        return True

    def has_search_capability(self) -> bool:
        """
        Verifica si la búsqueda web está disponible.

        Returns:
            bool: True si SerpAPI está configurado
        """
        return bool(self.SERPAPI_API_KEY)

    def __repr__(self) -> str:
        """Representación segura (sin mostrar API keys)."""
        return (
            f"Settings(\n"
            f"  DEEPSEEK_API_KEY={'*' * 8 if self.DEEPSEEK_API_KEY else 'NOT SET'},\n"
            f"  DEEPSEEK_MODEL={self.DEEPSEEK_MODEL},\n"
            f"  SERPAPI_API_KEY={'*' * 8 if self.SERPAPI_API_KEY else 'NOT SET'},\n"
            f"  AGENT_VERBOSE={self.AGENT_VERBOSE},\n"
            f"  AGENT_MAX_ITERATIONS={self.AGENT_MAX_ITERATIONS},\n"
            f"  LLM_TEMPERATURE={self.LLM_TEMPERATURE}\n"
            f")"
        )


# Instancia singleton de la configuración
settings = Settings()


# Constantes adicionales
TOOL_DESCRIPTIONS = {
    "calculator": """
    Útil para realizar cálculos matemáticos.
    Usa esta herramienta cuando necesites:
    - Operaciones aritméticas (suma, resta, multiplicación, división)
    - Porcentajes
    - Potencias y raíces
    - Cualquier expresión matemática

    Input: Una expresión matemática válida en Python (ej: "25 * 4", "100 * 0.15", "2 ** 10")
    """,

    "web_search": """
    Útil para buscar información actual en internet.
    Usa esta herramienta cuando necesites:
    - Información actualizada o reciente
    - Noticias actuales
    - Precios o cotizaciones actuales
    - Eventos recientes

    Input: Una consulta de búsqueda en texto natural
    """,

    "wikipedia": """
    Útil para consultar información enciclopédica.
    Usa esta herramienta cuando necesites:
    - Biografías de personas famosas
    - Historia de países, eventos o conceptos
    - Definiciones y explicaciones detalladas
    - Datos científicos o históricos

    Input: El tema o término a buscar en Wikipedia
    """
}
