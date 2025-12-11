"""
Herramienta de Calculadora para el Agente.

Esta herramienta permite al agente realizar cálculos matemáticos
de forma segura y controlada.

Ejemplo de uso:
    from src.tools.calculator import calculator_tool

    result = calculator_tool.invoke("25 * 4")
    print(result)  # 100
"""

import math
import re
from typing import Union
from langchain.tools import tool


# Funciones matemáticas permitidas para eval seguro
ALLOWED_NAMES = {
    # Constantes
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
    "inf": math.inf,

    # Funciones básicas
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "pow": pow,

    # Funciones matemáticas
    "sqrt": math.sqrt,
    "ceil": math.ceil,
    "floor": math.floor,
    "factorial": math.factorial,
    "gcd": math.gcd,
    "lcm": getattr(math, 'lcm', lambda a, b: abs(a * b) // math.gcd(a, b)),

    # Trigonometría
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,

    # Logaritmos y exponenciales
    "log": math.log,
    "log10": math.log10,
    "log2": math.log2,
    "exp": math.exp,

    # Conversiones
    "degrees": math.degrees,
    "radians": math.radians,
}


def safe_eval(expression: str) -> Union[int, float]:
    """
    Evalúa una expresión matemática de forma segura.

    Esta función solo permite operaciones matemáticas y bloquea
    cualquier código potencialmente peligroso.

    Args:
        expression: Expresión matemática a evaluar

    Returns:
        El resultado numérico de la expresión

    Raises:
        ValueError: Si la expresión contiene código no permitido
        SyntaxError: Si la expresión tiene sintaxis inválida

    Examples:
        >>> safe_eval("2 + 2")
        4
        >>> safe_eval("sqrt(16)")
        4.0
        >>> safe_eval("pi * 2")
        6.283185307179586
    """
    # Limpiar la expresión
    expression = expression.strip()

    # Verificar caracteres peligrosos
    dangerous_patterns = [
        r'__',           # Dunder methods
        r'import',       # Import statements
        r'exec',         # Exec function
        r'eval',         # Eval function
        r'open',         # File operations
        r'os\.',         # OS module
        r'sys\.',        # Sys module
        r'subprocess',   # Subprocess module
        r'\bclass\b',    # Class definitions
        r'\bdef\b',      # Function definitions
        r'\blambda\b',   # Lambda functions
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, expression, re.IGNORECASE):
            raise ValueError(f"Expresión no permitida: contiene '{pattern}'")

    # Reemplazar operadores comunes en español/texto
    expression = expression.replace('^', '**')  # Potencia
    expression = expression.replace('×', '*')   # Multiplicación
    expression = expression.replace('÷', '/')   # División
    expression = expression.replace(',', '.')   # Decimales

    try:
        # Evaluar con namespace restringido
        result = eval(expression, {"__builtins__": {}}, ALLOWED_NAMES)
        return result
    except Exception as e:
        raise ValueError(f"Error al evaluar '{expression}': {str(e)}")


@tool
def calculator_tool(expression: str) -> str:
    """
    Realiza cálculos matemáticos.

    Útil para operaciones aritméticas, porcentajes, potencias, raíces,
    trigonometría y otras funciones matemáticas.

    Args:
        expression: Una expresión matemática válida.
                   Ejemplos: "25 * 4", "sqrt(16)", "15/100 * 200"

    Returns:
        El resultado del cálculo como string.

    Examples:
        - "25 * 4" → "100"
        - "15/100 * 200" (15% de 200) → "30.0"
        - "sqrt(144)" → "12.0"
        - "2 ** 10" → "1024"
    """
    try:
        result = safe_eval(expression)

        # Formatear resultado
        if isinstance(result, float):
            # Si es un número entero, mostrarlo sin decimales
            if result.is_integer():
                return str(int(result))
            # Limitar decimales para mejor legibilidad
            return f"{result:.10g}"

        return str(result)

    except ValueError as e:
        return f"Error: {str(e)}"
    except SyntaxError:
        return f"Error: Sintaxis inválida en la expresión '{expression}'"
    except Exception as e:
        return f"Error inesperado: {str(e)}"


# Para uso directo del módulo
if __name__ == "__main__":
    # Ejemplos de prueba
    test_expressions = [
        "2 + 2",
        "25 * 4",
        "15/100 * 200",  # 15% de 200
        "sqrt(144)",
        "2 ** 10",
        "pi * 2",
        "sin(radians(90))",
        "log10(1000)",
    ]

    print("Pruebas de la calculadora:")
    print("-" * 40)

    for expr in test_expressions:
        result = calculator_tool.invoke(expr)
        print(f"{expr:20} = {result}")
