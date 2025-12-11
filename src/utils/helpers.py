"""
Funciones auxiliares para el Agente.

Este módulo contiene utilidades y funciones de ayuda
usadas en todo el proyecto.
"""

import logging
from typing import Any, Dict, List
from functools import wraps
import time


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Configura el sistema de logging.

    Args:
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR)

    Returns:
        Logger configurado
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    return logging.getLogger("agent")


def timing_decorator(func):
    """
    Decorador para medir el tiempo de ejecución de una función.

    Usage:
        @timing_decorator
        def my_function():
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        print(f"⏱️  {func.__name__} ejecutado en {end_time - start_time:.2f}s")
        return result

    return wrapper


def format_agent_response(response: str, steps: List = None) -> str:
    """
    Formatea la respuesta del agente para mostrar al usuario.

    Args:
        response: La respuesta del agente
        steps: Pasos intermedios (opcional)

    Returns:
        Respuesta formateada
    """
    output = []

    if steps:
        output.append("📝 Pasos del razonamiento:")
        for i, (action, observation) in enumerate(steps, 1):
            output.append(f"   {i}. {action.tool}: {action.tool_input[:50]}...")
            output.append(f"      → {observation[:100]}...")
        output.append("")

    output.append(f"✅ Respuesta: {response}")

    return "\n".join(output)


def parse_math_expression(text: str) -> str:
    """
    Intenta extraer una expresión matemática de texto en lenguaje natural.

    Args:
        text: Texto con una pregunta matemática

    Returns:
        Expresión matemática extraída

    Examples:
        >>> parse_math_expression("¿Cuánto es 25 por 4?")
        "25 * 4"
    """
    # Reemplazos comunes
    replacements = {
        " por ": " * ",
        " multiplicado por ": " * ",
        " dividido entre ": " / ",
        " entre ": " / ",
        " más ": " + ",
        " menos ": " - ",
        " al cuadrado": " ** 2",
        " al cubo": " ** 3",
        " elevado a ": " ** ",
        "raíz cuadrada de ": "sqrt(",
        "raiz cuadrada de ": "sqrt(",
        "porcentaje": "/ 100 *",
        "% de ": " / 100 * ",
    }

    result = text.lower()
    for old, new in replacements.items():
        result = result.replace(old, new)

    # Cerrar paréntesis de sqrt si es necesario
    if "sqrt(" in result and ")" not in result:
        result += ")"

    return result


def validate_api_key(api_key: str, service: str = "DeepSeek") -> bool:
    """
    Valida que una API key tenga un formato válido.

    Args:
        api_key: La API key a validar
        service: Nombre del servicio

    Returns:
        True si parece válida

    Raises:
        ValueError: Si la API key es inválida
    """
    if not api_key:
        raise ValueError(f"API key de {service} no proporcionada")

    if len(api_key) < 10:
        raise ValueError(f"API key de {service} parece demasiado corta")

    if api_key.startswith("sk-") or api_key.startswith("api-"):
        return True

    # Aceptar otros formatos pero con advertencia
    return True


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """
    Trunca texto a una longitud máxima.

    Args:
        text: Texto a truncar
        max_length: Longitud máxima
        suffix: Sufijo a agregar si se trunca

    Returns:
        Texto truncado
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


class AgentMetrics:
    """
    Clase para rastrear métricas del agente.

    Útil para monitorear el rendimiento y uso del agente.
    """

    def __init__(self):
        self.total_queries = 0
        self.total_tool_calls = 0
        self.tool_usage: Dict[str, int] = {}
        self.total_time = 0.0
        self.errors = 0

    def record_query(self, duration: float, tools_used: List[str] = None):
        """Registra una consulta al agente."""
        self.total_queries += 1
        self.total_time += duration

        if tools_used:
            self.total_tool_calls += len(tools_used)
            for tool in tools_used:
                self.tool_usage[tool] = self.tool_usage.get(tool, 0) + 1

    def record_error(self):
        """Registra un error."""
        self.errors += 1

    def get_summary(self) -> Dict[str, Any]:
        """Obtiene un resumen de las métricas."""
        avg_time = self.total_time / self.total_queries if self.total_queries > 0 else 0

        return {
            "total_queries": self.total_queries,
            "total_tool_calls": self.total_tool_calls,
            "tool_usage": self.tool_usage,
            "average_response_time": f"{avg_time:.2f}s",
            "total_time": f"{self.total_time:.2f}s",
            "errors": self.errors,
            "error_rate": f"{(self.errors / self.total_queries * 100):.1f}%" if self.total_queries > 0 else "0%"
        }

    def __str__(self) -> str:
        summary = self.get_summary()
        return f"AgentMetrics(queries={summary['total_queries']}, avg_time={summary['average_response_time']})"
