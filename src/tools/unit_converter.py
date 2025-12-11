"""
Herramienta de Conversión de Unidades para el Agente.

Esta herramienta permite al agente convertir entre diferentes unidades
de medida: longitud, peso, temperatura, volumen, tiempo, etc.

Ejemplo de uso:
    from src.tools.unit_converter import unit_converter_tool

    result = unit_converter_tool.invoke("100 km a millas")
    print(result)
"""

import re
from typing import Tuple, Optional
from langchain.tools import tool


# Factores de conversión (todo a unidad base)
CONVERSIONS = {
    # Longitud (base: metros)
    "longitud": {
        "base": "metros",
        "unidades": {
            "km": 1000,
            "kilómetros": 1000,
            "kilometros": 1000,
            "m": 1,
            "metros": 1,
            "cm": 0.01,
            "centímetros": 0.01,
            "centimetros": 0.01,
            "mm": 0.001,
            "milímetros": 0.001,
            "milimetros": 0.001,
            "mi": 1609.344,
            "millas": 1609.344,
            "yd": 0.9144,
            "yardas": 0.9144,
            "ft": 0.3048,
            "pies": 0.3048,
            "in": 0.0254,
            "pulgadas": 0.0254,
        }
    },
    
    # Peso/Masa (base: gramos)
    "peso": {
        "base": "gramos",
        "unidades": {
            "kg": 1000,
            "kilogramos": 1000,
            "kilos": 1000,
            "g": 1,
            "gramos": 1,
            "mg": 0.001,
            "miligramos": 0.001,
            "lb": 453.592,
            "libras": 453.592,
            "oz": 28.3495,
            "onzas": 28.3495,
            "t": 1000000,
            "toneladas": 1000000,
        }
    },
    
    # Volumen (base: litros)
    "volumen": {
        "base": "litros",
        "unidades": {
            "l": 1,
            "litros": 1,
            "ml": 0.001,
            "mililitros": 0.001,
            "gal": 3.78541,
            "galones": 3.78541,
            "pt": 0.473176,
            "pintas": 0.473176,
            "fl oz": 0.0295735,
            "oz líquidas": 0.0295735,
            "m3": 1000,
            "metros cúbicos": 1000,
            "cm3": 0.001,
        }
    },
    
    # Tiempo (base: segundos)
    "tiempo": {
        "base": "segundos",
        "unidades": {
            "s": 1,
            "segundos": 1,
            "min": 60,
            "minutos": 60,
            "h": 3600,
            "horas": 3600,
            "días": 86400,
            "dias": 86400,
            "semanas": 604800,
            "meses": 2592000,  # 30 días
            "años": 31536000,  # 365 días
        }
    },
    
    # Velocidad (base: m/s)
    "velocidad": {
        "base": "m/s",
        "unidades": {
            "m/s": 1,
            "km/h": 0.277778,
            "kmh": 0.277778,
            "mph": 0.44704,
            "millas/hora": 0.44704,
            "nudos": 0.514444,
            "knots": 0.514444,
        }
    },
    
    # Área (base: metros cuadrados)
    "area": {
        "base": "m²",
        "unidades": {
            "km2": 1000000,
            "km²": 1000000,
            "m2": 1,
            "m²": 1,
            "metros cuadrados": 1,
            "cm2": 0.0001,
            "cm²": 0.0001,
            "ha": 10000,
            "hectáreas": 10000,
            "hectareas": 10000,
            "acres": 4046.86,
            "ft2": 0.092903,
            "pies cuadrados": 0.092903,
        }
    },
    
    # Datos (base: bytes)
    "datos": {
        "base": "bytes",
        "unidades": {
            "b": 1,
            "bytes": 1,
            "kb": 1024,
            "kilobytes": 1024,
            "mb": 1048576,
            "megabytes": 1048576,
            "gb": 1073741824,
            "gigabytes": 1073741824,
            "tb": 1099511627776,
            "terabytes": 1099511627776,
        }
    },
}


def find_unit_category(unit: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Encuentra la categoría a la que pertenece una unidad.
    
    Args:
        unit: Nombre de la unidad
        
    Returns:
        Tupla (categoría, unidad_normalizada) o (None, None)
    """
    unit_lower = unit.lower().strip()
    
    for category, data in CONVERSIONS.items():
        if unit_lower in data["unidades"]:
            return category, unit_lower
    
    return None, None


def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convierte temperaturas (caso especial, no es multiplicativo).
    """
    from_unit = from_unit.lower()
    to_unit = to_unit.lower()
    
    # Normalizar nombres
    from_map = {"c": "c", "celsius": "c", "°c": "c", "f": "f", "fahrenheit": "f", "°f": "f", "k": "k", "kelvin": "k"}
    to_map = from_map
    
    from_unit = from_map.get(from_unit, from_unit)
    to_unit = to_map.get(to_unit, to_unit)
    
    # Convertir a Celsius primero
    if from_unit == "c":
        celsius = value
    elif from_unit == "f":
        celsius = (value - 32) * 5/9
    elif from_unit == "k":
        celsius = value - 273.15
    else:
        raise ValueError(f"Unidad de temperatura no reconocida: {from_unit}")
    
    # Convertir de Celsius a destino
    if to_unit == "c":
        return celsius
    elif to_unit == "f":
        return celsius * 9/5 + 32
    elif to_unit == "k":
        return celsius + 273.15
    else:
        raise ValueError(f"Unidad de temperatura no reconocida: {to_unit}")


def convert_units(value: float, from_unit: str, to_unit: str) -> Tuple[float, str]:
    """
    Convierte un valor de una unidad a otra.
    
    Returns:
        Tupla (valor_convertido, mensaje)
    """
    from_unit_lower = from_unit.lower().strip()
    to_unit_lower = to_unit.lower().strip()
    
    # Manejar temperatura por separado
    temp_units = ["c", "celsius", "°c", "f", "fahrenheit", "°f", "k", "kelvin"]
    if from_unit_lower in temp_units or to_unit_lower in temp_units:
        result = convert_temperature(value, from_unit_lower, to_unit_lower)
        return result, f"{value} {from_unit} = {result:.2f} {to_unit}"
    
    # Encontrar categorías
    from_cat, from_normalized = find_unit_category(from_unit_lower)
    to_cat, to_normalized = find_unit_category(to_unit_lower)
    
    if from_cat is None:
        raise ValueError(f"Unidad no reconocida: {from_unit}")
    if to_cat is None:
        raise ValueError(f"Unidad no reconocida: {to_unit}")
    if from_cat != to_cat:
        raise ValueError(f"No se puede convertir {from_unit} ({from_cat}) a {to_unit} ({to_cat})")
    
    # Obtener factores
    from_factor = CONVERSIONS[from_cat]["unidades"][from_normalized]
    to_factor = CONVERSIONS[from_cat]["unidades"][to_normalized]
    
    # Convertir: valor -> base -> destino
    base_value = value * from_factor
    result = base_value / to_factor
    
    return result, f"{value} {from_unit} = {result:.6g} {to_unit}"


@tool
def unit_converter_tool(query: str) -> str:
    """
    Convierte entre diferentes unidades de medida.
    
    Soporta conversiones de: longitud, peso, volumen, tiempo, temperatura,
    velocidad, área y datos/almacenamiento.
    
    Args:
        query: Consulta de conversión en formato "valor unidad_origen a unidad_destino"
               Ejemplos:
               - "100 km a millas"
               - "75 fahrenheit a celsius"
               - "5 libras a kilogramos"
               - "1024 mb a gb"
               
    Returns:
        El resultado de la conversión.
        
    Examples:
        - "100 km a millas" → "100 km = 62.1371 millas"
        - "32 fahrenheit a celsius" → "32 fahrenheit = 0.00 celsius"
        - "1 hora a minutos" → "1 hora = 60 minutos"
    """
    query = query.strip()
    
    # Patrones de conversión
    patterns = [
        r'(\d+\.?\d*)\s*(\S+)\s+(?:a|to|en|=)\s+(\S+)',
        r'convertir\s+(\d+\.?\d*)\s*(\S+)\s+a\s+(\S+)',
        r'cuánto[s]?\s+(?:es|son)\s+(\d+\.?\d*)\s*(\S+)\s+en\s+(\S+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            try:
                value = float(match.group(1))
                from_unit = match.group(2)
                to_unit = match.group(3)
                
                result, message = convert_units(value, from_unit, to_unit)
                return message
                
            except ValueError as e:
                return f"Error: {str(e)}"
            except Exception as e:
                return f"Error inesperado: {str(e)}"
    
    # Si no se reconoció el formato
    return """No pude entender la conversión. Usa el formato: "valor unidad a unidad_destino"
    
Ejemplos:
- "100 km a millas"
- "32 fahrenheit a celsius"  
- "5 libras a kg"
- "1024 mb a gb"

Categorías soportadas: longitud, peso, volumen, tiempo, temperatura, velocidad, área, datos"""


# Para uso directo del módulo
if __name__ == "__main__":
    test_queries = [
        "100 km a millas",
        "32 fahrenheit a celsius",
        "5 libras a kilogramos",
        "1024 mb a gb",
        "1 hora a minutos",
        "100 metros a pies",
    ]
    
    print("Pruebas del conversor de unidades:")
    print("-" * 50)
    
    for query in test_queries:
        result = unit_converter_tool.invoke(query)
        print(f"'{query}' → {result}")
        print()
